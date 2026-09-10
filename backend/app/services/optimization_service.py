import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import (
    OptimizationRun,
    Route,
    RouteStop,
    Depot,
    Vehicle,
    Driver,
    CollectionPoint,
    User,
)
from app.models.enums import (
    OptimizationStatus,
    RouteStatus,
    StopStatus,
    VehicleStatus,
)
from app.optimization import (
    cvrp_solver,
    OptimizationInput,
    DepotNode,
    VehicleNode,
    CollectionPointNode,
    OptimizationOutput,
)
from app.services.osrm_service import osrm_service, haversine_distance
from app.services.priority_service import calculate_collection_point_priority
from app.schemas.optimization import (
    OptimizationGenerateRequest,
    OptimizationRunDetailResponse,
    OptimizationRunSummaryResponse,
    ReoptimizeRequest,
)
from app.schemas.route import RouteResponse, RouteStopResponse

logger = logging.getLogger(__name__)


class OptimizationService:
    @staticmethod
    def generate_and_persist_optimization(
        db: Session, request: OptimizationGenerateRequest
    ) -> OptimizationRunDetailResponse:
        # 1. Fetch Depot
        depot: Optional[Depot] = None
        if request.depot_id:
            depot = db.query(Depot).filter(Depot.id == request.depot_id).first()
        else:
            depot = db.query(Depot).first()

        if not depot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No central depot found in system. Please configure a depot first.",
            )

        # 2. Fetch Vehicles
        vehicles_query = db.query(Vehicle).options(
            joinedload(Vehicle.driver).joinedload(Driver.user)
        )
        if request.vehicle_ids:
            vehicles = vehicles_query.filter(Vehicle.id.in_(request.vehicle_ids)).all()
        else:
            vehicles = vehicles_query.filter(
                Vehicle.status.in_([VehicleStatus.AVAILABLE, VehicleStatus.ON_ROUTE])
            ).all()

        if not vehicles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available vehicles found for route optimization.",
            )

        # 3. Fetch Collection Points
        points_query = db.query(CollectionPoint)
        if request.collection_point_ids:
            collection_points = points_query.filter(
                CollectionPoint.id.in_(request.collection_point_ids)
            ).all()
        else:
            collection_points = points_query.filter(
                CollectionPoint.status == "ACTIVE"
            ).all()

        if not collection_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active collection points found for route optimization.",
            )

        # 4. Construct Optimization Input
        depot_node = DepotNode(
            id=depot.id,
            name=depot.name,
            latitude=depot.latitude,
            longitude=depot.longitude,
        )

        vehicle_nodes = [
            VehicleNode(
                id=v.id,
                vehicle_number=v.vehicle_number,
                capacity_kg=v.capacity_kg,
            )
            for v in vehicles
        ]

        cp_map = {cp.id: cp for cp in collection_points}
        cp_nodes = []
        for cp in collection_points:
            _, score = calculate_collection_point_priority(
                estimated_waste_kg=cp.estimated_waste_kg,
                waste_type=cp.waste_type,
                last_collection_date=cp.last_collection_date,
                overflow_status=cp.overflow_status,
            )
            cp_nodes.append(
                CollectionPointNode(
                    id=cp.id,
                    name=cp.name,
                    latitude=cp.latitude,
                    longitude=cp.longitude,
                    estimated_waste_kg=cp.estimated_waste_kg,
                    priority_score=score,
                )
            )



        opt_input = OptimizationInput(
            depot=depot_node,
            vehicles=vehicle_nodes,
            collection_points=cp_nodes,
            time_limit_seconds=request.time_limit_seconds,
        )

        # 5. Run OR-Tools CVRP Solver
        solver_result: OptimizationOutput = cvrp_solver.solve(opt_input)

        # 6. Baseline Unoptimized Comparison
        # Naive baseline: individual round-trips from depot to each collection point
        baseline_distance = sum(
            2 * haversine_distance(depot.latitude, depot.longitude, cp.latitude, cp.longitude)
            for cp in collection_points
        )
        baseline_duration = (baseline_distance / 30.0) * 60.0  # 30 km/h average urban speed

        dist_saved_pct = 0.0
        time_saved_pct = 0.0
        if baseline_distance > 0 and solver_result.total_distance_km > 0:
            dist_saved_pct = max(
                0.0,
                round(
                    ((baseline_distance - solver_result.total_distance_km) / baseline_distance) * 100.0,
                    2,
                ),
            )
            time_saved_pct = max(
                0.0,
                round(
                    ((baseline_duration - solver_result.total_duration_minutes) / baseline_duration) * 100.0,
                    2,
                ),
            )

        # 7. Determine Optimization Run Status
        opt_status = OptimizationStatus.SUCCESS
        if solver_result.status == "INFEASIBLE":
            opt_status = OptimizationStatus.INFEASIBLE
        elif solver_result.status == "NO_SOLUTION":
            opt_status = OptimizationStatus.FAILED
        elif solver_result.unassigned_points or solver_result.status == "INSUFFICIENT_CAPACITY":
            opt_status = OptimizationStatus.PARTIAL_SUCCESS

        now = datetime.utcnow()
        opt_run_id: Optional[int] = None
        routes_response: List[RouteResponse] = []

        # Vehicle ID to Entity mapping
        v_entity_map = {v.id: v for v in vehicles}

        # 8. Persist if requested
        if request.persist and solver_result.routes:
            opt_run = OptimizationRun(
                created_at=now,
                number_of_vehicles=len(vehicles),
                number_of_collection_points=len(collection_points),
                total_distance_before=round(baseline_distance, 2),
                total_distance_after=solver_result.total_distance_km,
                total_duration_before=round(baseline_duration, 2),
                total_duration_after=solver_result.total_duration_minutes,
                waste_collected=solver_result.total_waste_collected_kg,
                distance_saved_percentage=dist_saved_pct,
                time_saved_percentage=time_saved_pct,
                status=opt_status,
            )
            db.add(opt_run)
            db.flush()
            opt_run_id = opt_run.id

            for v_route in solver_result.routes:
                if len(v_route.stops) <= 1:
                    continue  # Skip vehicles with no assigned stops

                # Fetch OSRM road geometry for this route
                waypoint_coords = [(s.latitude, s.longitude) for s in v_route.stops]
                geom_result = osrm_service.get_route_geometry(waypoint_coords)
                geom_geojson_str = json.dumps(geom_result.get("geometry_coordinates", []))

                v_entity = v_entity_map.get(v_route.vehicle_id)

                db_route = Route(
                    route_date=now.date(),
                    vehicle_id=v_route.vehicle_id,
                    total_distance_km=v_route.total_distance_km,
                    estimated_duration_minutes=v_route.total_duration_minutes,
                    total_waste_kg=v_route.total_waste_kg,
                    utilization_percentage=v_route.utilization_percentage,
                    status=RouteStatus.PLANNED,
                    optimization_run_id=opt_run.id,
                    geometry_geojson=geom_geojson_str,
                    created_at=now,
                    updated_at=now,
                )
                db.add(db_route)
                db.flush()

                # Add Route Stops (exclude start depot stop index 0 and end depot return)
                stops_resp_list: List[RouteStopResponse] = []
                for s in v_route.stops:
                    if s.point_id is None:
                        continue  # Skip depot markers for database route_stops table

                    cp_entity = cp_map.get(s.point_id)
                    if not cp_entity:
                        continue

                    eta = now + timedelta(minutes=s.estimated_arrival_minutes)
                    db_stop = RouteStop(
                        route_id=db_route.id,
                        collection_point_id=cp_entity.id,
                        sequence_number=s.sequence_number,
                        estimated_arrival_time=eta,
                        status=StopStatus.PENDING,
                    )
                    db.add(db_stop)
                    db.flush()

                    stops_resp_list.append(
                        RouteStopResponse(
                            id=db_stop.id,
                            route_id=db_route.id,
                            collection_point_id=cp_entity.id,
                            point_name=cp_entity.name,
                            point_address=cp_entity.address,
                            latitude=cp_entity.latitude,
                            longitude=cp_entity.longitude,
                            estimated_waste_kg=cp_entity.estimated_waste_kg,
                            waste_type=cp_entity.waste_type,
                            priority=cp_entity.priority,
                            sequence_number=db_stop.sequence_number,
                            estimated_arrival_time=eta,
                            actual_arrival_time=None,
                            status=db_stop.status,
                        )
                    )

                driver_id = v_entity.driver.id if v_entity and v_entity.driver else None
                driver_name = (
                    v_entity.driver.user.name
                    if v_entity and v_entity.driver and v_entity.driver.user
                    else None
                )

                routes_response.append(
                    RouteResponse(
                        id=db_route.id,
                        route_date=db_route.route_date,
                        vehicle_id=db_route.vehicle_id,
                        vehicle_number=v_route.vehicle_number,
                        driver_id=driver_id,
                        driver_name=driver_name,
                        total_distance_km=db_route.total_distance_km,
                        estimated_duration_minutes=db_route.estimated_duration_minutes,
                        total_waste_kg=db_route.total_waste_kg,
                        utilization_percentage=db_route.utilization_percentage,
                        status=db_route.status,
                        optimization_run_id=opt_run.id,
                        geometry_geojson=geom_geojson_str,
                        created_at=db_route.created_at,
                        updated_at=db_route.updated_at,
                        stops=stops_resp_list,
                    )
                )

            db.commit()
        else:
            # Ephemeral / non-persisted response
            for v_route in solver_result.routes:
                if len(v_route.stops) <= 1:
                    continue

                waypoint_coords = [(s.latitude, s.longitude) for s in v_route.stops]
                geom_result = osrm_service.get_route_geometry(waypoint_coords)
                geom_geojson_str = json.dumps(geom_result.get("geometry_coordinates", []))

                v_entity = v_entity_map.get(v_route.vehicle_id)
                driver_id = v_entity.driver.id if v_entity and v_entity.driver else None
                driver_name = (
                    v_entity.driver.user.name
                    if v_entity and v_entity.driver and v_entity.driver.user
                    else None
                )

                stops_resp_list = []
                for s in v_route.stops:
                    if s.point_id is None:
                        continue
                    cp_entity = cp_map.get(s.point_id)
                    if cp_entity:
                        stops_resp_list.append(
                            RouteStopResponse(
                                id=0,
                                route_id=0,
                                collection_point_id=cp_entity.id,
                                point_name=cp_entity.name,
                                point_address=cp_entity.address,
                                latitude=cp_entity.latitude,
                                longitude=cp_entity.longitude,
                                estimated_waste_kg=cp_entity.estimated_waste_kg,
                                waste_type=cp_entity.waste_type,
                                priority=cp_entity.priority,
                                sequence_number=s.sequence_number,
                                estimated_arrival_time=now + timedelta(minutes=s.estimated_arrival_minutes),
                                actual_arrival_time=None,
                                status=StopStatus.PENDING,
                            )
                        )

                routes_response.append(
                    RouteResponse(
                        id=0,
                        route_date=now.date(),
                        vehicle_id=v_route.vehicle_id,
                        vehicle_number=v_route.vehicle_number,
                        driver_id=driver_id,
                        driver_name=driver_name,
                        total_distance_km=v_route.total_distance_km,
                        estimated_duration_minutes=v_route.total_duration_minutes,
                        total_waste_kg=v_route.total_waste_kg,
                        utilization_percentage=v_route.utilization_percentage,
                        status=RouteStatus.PLANNED,
                        optimization_run_id=None,
                        geometry_geojson=geom_geojson_str,
                        created_at=now,
                        updated_at=now,
                        stops=stops_resp_list,
                    )
                )

        return OptimizationRunDetailResponse(
            id=opt_run_id,
            created_at=now,
            status=opt_status,
            optimization_status_code=solver_result.status,
            number_of_vehicles=len(vehicles),
            number_of_collection_points=len(collection_points),
            total_distance_before=round(baseline_distance, 2),
            total_distance_after=solver_result.total_distance_km,
            total_duration_before=round(baseline_duration, 2),
            total_duration_after=solver_result.total_duration_minutes,
            waste_collected=solver_result.total_waste_collected_kg,
            distance_saved_percentage=dist_saved_pct,
            time_saved_percentage=time_saved_pct,
            fleet_utilization_percentage=solver_result.fleet_utilization_percentage,
            routes=routes_response,
            unassigned_points=solver_result.unassigned_points,
            warnings=solver_result.warnings,
        )

    @staticmethod
    def list_optimization_runs(
        db: Session, skip: int = 0, limit: int = 20
    ) -> List[OptimizationRunSummaryResponse]:
        runs = (
            db.query(OptimizationRun)
            .options(joinedload(OptimizationRun.routes))
            .order_by(OptimizationRun.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [
            OptimizationRunSummaryResponse(
                id=run.id,
                created_at=run.created_at,
                number_of_vehicles=run.number_of_vehicles,
                number_of_collection_points=run.number_of_collection_points,
                total_distance_before=run.total_distance_before,
                total_distance_after=run.total_distance_after,
                total_duration_before=run.total_duration_before,
                total_duration_after=run.total_duration_after,
                waste_collected=run.waste_collected,
                distance_saved_percentage=run.distance_saved_percentage,
                time_saved_percentage=run.time_saved_percentage,
                status=run.status,
                routes_count=len(run.routes),
            )
            for run in runs
        ]

    @staticmethod
    def get_optimization_run_by_id(
        db: Session, run_id: int
    ) -> OptimizationRunDetailResponse:
        run = (
            db.query(OptimizationRun)
            .options(
                joinedload(OptimizationRun.routes)
                .joinedload(Route.vehicle)
                .joinedload(Vehicle.driver)
                .joinedload(Driver.user),
                joinedload(OptimizationRun.routes)
                .joinedload(Route.stops)
                .joinedload(RouteStop.collection_point),
            )
            .filter(OptimizationRun.id == run_id)
            .first()
        )

        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Optimization run with ID {run_id} not found.",
            )

        routes_resp: List[RouteResponse] = []
        for r in run.routes:
            v = r.vehicle
            d_id = v.driver.id if v and v.driver else None
            d_name = v.driver.user.name if v and v.driver and v.driver.user else None

            stops_list = [
                RouteStopResponse(
                    id=s.id,
                    route_id=r.id,
                    collection_point_id=s.collection_point_id,
                    point_name=s.collection_point.name if s.collection_point else "Collection Point",
                    point_address=s.collection_point.address if s.collection_point else "",
                    latitude=s.collection_point.latitude if s.collection_point else 0.0,
                    longitude=s.collection_point.longitude if s.collection_point else 0.0,
                    estimated_waste_kg=s.collection_point.estimated_waste_kg if s.collection_point else 0.0,
                    waste_type=s.collection_point.waste_type if s.collection_point else "MIXED_PLASTIC",
                    priority=s.collection_point.priority if s.collection_point else "MEDIUM",
                    sequence_number=s.sequence_number,
                    estimated_arrival_time=s.estimated_arrival_time,
                    actual_arrival_time=s.actual_arrival_time,
                    status=s.status,
                )
                for s in r.stops
            ]

            routes_resp.append(
                RouteResponse(
                    id=r.id,
                    route_date=r.route_date,
                    vehicle_id=r.vehicle_id,
                    vehicle_number=v.vehicle_number if v else f"Vehicle #{r.vehicle_id}",
                    driver_id=d_id,
                    driver_name=d_name,
                    total_distance_km=r.total_distance_km,
                    estimated_duration_minutes=r.estimated_duration_minutes,
                    total_waste_kg=r.total_waste_kg,
                    utilization_percentage=r.utilization_percentage,
                    status=r.status,
                    optimization_run_id=run.id,
                    geometry_geojson=r.geometry_geojson,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                    stops=stops_list,
                )
            )

        return OptimizationRunDetailResponse(
            id=run.id,
            created_at=run.created_at,
            status=run.status,
            optimization_status_code=run.status.value,
            number_of_vehicles=run.number_of_vehicles,
            number_of_collection_points=run.number_of_collection_points,
            total_distance_before=run.total_distance_before,
            total_distance_after=run.total_distance_after,
            total_duration_before=run.total_duration_before,
            total_duration_after=run.total_duration_after,
            waste_collected=run.waste_collected,
            distance_saved_percentage=run.distance_saved_percentage,
            time_saved_percentage=run.time_saved_percentage,
            fleet_utilization_percentage=0.0,
            routes=routes_resp,
            unassigned_points=[],
            warnings=[],
        )

    @staticmethod
    def reoptimize_run(
        db: Session, run_id: int, request: ReoptimizeRequest
    ) -> OptimizationRunDetailResponse:
        # Retrieve existing run and remaining pending stops
        run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Optimization run with ID {run_id} not found.",
            )

        pending_stops = (
            db.query(RouteStop)
            .join(Route)
            .filter(
                Route.optimization_run_id == run_id,
                RouteStop.status == StopStatus.PENDING,
            )
            .all()
        )

        if not pending_stops:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending collection stops found to re-optimize. All stops are completed or processed.",
            )

        pending_point_ids = list({s.collection_point_id for s in pending_stops})

        gen_request = OptimizationGenerateRequest(
            vehicle_ids=request.vehicle_ids,
            collection_point_ids=pending_point_ids,
            persist=True,
            time_limit_seconds=request.time_limit_seconds,
        )

        return OptimizationService.generate_and_persist_optimization(db, gen_request)


optimization_service = OptimizationService()

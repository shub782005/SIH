import logging
from typing import List, Tuple, Dict, Any, Optional
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.services.osrm_service import osrm_service, haversine_matrix
from app.optimization.schemas import (
    OptimizationInput,
    OptimizationOutput,
    VehicleRoute,
    RouteStop,
    UnassignedPoint,
    CollectionPointNode,
)

logger = logging.getLogger(__name__)


class CVRPSolver:
    """
    Google OR-Tools Capacitated Vehicle Routing Problem (CVRP) Optimization Engine.
    Respects strict vehicle capacity constraints, depot start/end, and priority-based weighting.
    """

    def solve(self, input_data: OptimizationInput) -> OptimizationOutput:
        warnings: List[str] = []

        # Validation 1: Vehicles check
        if not input_data.vehicles:
            return OptimizationOutput(
                status="NO_VEHICLES_AVAILABLE",
                routes=[],
                unassigned_points=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                total_waste_collected_kg=0.0,
                fleet_utilization_percentage=0.0,
                warnings=["No vehicles were provided for optimization."],
            )

        # Validation 2: Collection points check
        if not input_data.collection_points:
            return OptimizationOutput(
                status="NO_COLLECTION_POINTS",
                routes=[],
                unassigned_points=[],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                total_waste_collected_kg=0.0,
                fleet_utilization_percentage=0.0,
                warnings=["No collection points were provided for optimization."],
            )

        # Rule 16 Check: Infeasible single point demand > max single vehicle capacity
        max_vehicle_capacity = max(v.capacity_kg for v in input_data.vehicles)
        total_fleet_capacity = sum(v.capacity_kg for v in input_data.vehicles)

        valid_collection_points: List[CollectionPointNode] = []
        unassigned_points: List[UnassignedPoint] = []

        for cp in input_data.collection_points:
            if cp.estimated_waste_kg > max_vehicle_capacity:
                unassigned_points.append(
                    UnassignedPoint(
                        point_id=cp.id,
                        name=cp.name,
                        estimated_waste_kg=cp.estimated_waste_kg,
                        priority_score=cp.priority_score,
                        reason=(
                            f"Waste quantity ({cp.estimated_waste_kg:.1f} kg) exceeds "
                            f"maximum single vehicle capacity ({max_vehicle_capacity:.1f} kg)."
                        ),
                    )
                )
                warnings.append(
                    f"Collection point '{cp.name}' (ID: {cp.id}, {cp.estimated_waste_kg} kg) marked infeasible "
                    f"due to exceeding max single vehicle capacity ({max_vehicle_capacity} kg)."
                )
            else:
                valid_collection_points.append(cp)

        if not valid_collection_points:
            return OptimizationOutput(
                status="INFEASIBLE",
                routes=[],
                unassigned_points=unassigned_points,
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                total_waste_collected_kg=0.0,
                fleet_utilization_percentage=0.0,
                warnings=warnings or ["All collection points exceed vehicle capacity."],
            )

        total_demand = sum(cp.estimated_waste_kg for cp in valid_collection_points)
        if total_demand > total_fleet_capacity:
            warnings.append(
                f"Total collection demand ({total_demand:.1f} kg) exceeds total fleet capacity "
                f"({total_fleet_capacity:.1f} kg). Lower-priority stops may be unassigned."
            )

        # Build coordinate list: Node 0 is Depot, Nodes 1..N are valid collection points
        all_coords: List[Tuple[float, float]] = [
            (input_data.depot.latitude, input_data.depot.longitude)
        ] + [
            (cp.latitude, cp.longitude) for cp in valid_collection_points
        ]

        num_nodes = len(all_coords)
        num_vehicles = len(input_data.vehicles)

        # Distance and Duration matrices
        distance_matrix_km = input_data.distance_matrix_km
        duration_matrix_min = input_data.duration_matrix_min

        if not distance_matrix_km or not duration_matrix_min:
            dist_mat, dur_mat, is_fallback, source = osrm_service.get_table_matrix(all_coords)
            distance_matrix_km = dist_mat
            duration_matrix_min = dur_mat
            if is_fallback:
                warnings.append("Road distance calculation used Haversine fallback.")

        # Scale values to integers for OR-Tools
        # Distances scaled to meters (integer)
        dist_scale = 1000
        distance_matrix_int = [
            [int(round(d * dist_scale)) for d in row]
            for row in distance_matrix_km
        ]

        # Demands scaled by 10 (100g resolution)
        demand_scale = 10
        demands_int = [0] + [
            int(round(cp.estimated_waste_kg * demand_scale))
            for cp in valid_collection_points
        ]
        vehicle_capacities_int = [
            int(round(v.capacity_kg * demand_scale))
            for v in input_data.vehicles
        ]

        # Initialize OR-Tools Routing Index Manager and Model
        manager = pywrapcp.RoutingIndexManager(num_nodes, num_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)

        # Register Transit Callback (Distance)
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix_int[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Capacity Constraint Dimension
        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return demands_int[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities_int,  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Add Disjunctions with Priority Weighting
        # Higher priority points receive significantly higher penalties for being dropped
        for node in range(1, num_nodes):
            cp = valid_collection_points[node - 1]
            # Priority penalty: Base (100M) + priority_score * 10M + demand * 10K
            priority_penalty = int(
                100_000_000
                + (cp.priority_score * 10_000_000)
                + (cp.estimated_waste_kg * 10_000)
            )
            routing.AddDisjunction([manager.NodeToIndex(node)], priority_penalty)

        # Search Parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = input_data.time_limit_seconds

        # Solve Model
        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            return OptimizationOutput(
                status="NO_SOLUTION",
                routes=[],
                unassigned_points=unassigned_points + [
                    UnassignedPoint(
                        point_id=cp.id,
                        name=cp.name,
                        estimated_waste_kg=cp.estimated_waste_kg,
                        priority_score=cp.priority_score,
                        reason="Solver could not find a feasible solution within time limits.",
                    )
                    for cp in valid_collection_points
                ],
                total_distance_km=0.0,
                total_duration_minutes=0.0,
                total_waste_collected_kg=0.0,
                fleet_utilization_percentage=0.0,
                warnings=warnings + ["No solution found by optimization solver."],
            )

        # Extract Solution Routes
        routes_output: List[VehicleRoute] = []
        visited_nodes = set()
        total_opt_distance_km = 0.0
        total_opt_duration_min = 0.0
        total_opt_waste_kg = 0.0

        for vehicle_idx in range(num_vehicles):
            vehicle_node = input_data.vehicles[vehicle_idx]
            index = routing.Start(vehicle_idx)

            stops: List[RouteStop] = []
            route_distance_km = 0.0
            route_duration_min = 0.0
            route_waste_kg = 0.0
            seq = 0

            # Initial depot stop
            stops.append(
                RouteStop(
                    sequence_number=seq,
                    point_id=None,
                    name=input_data.depot.name,
                    latitude=input_data.depot.latitude,
                    longitude=input_data.depot.longitude,
                    waste_kg=0.0,
                    accumulated_waste_kg=0.0,
                    accumulated_distance_km=0.0,
                    estimated_arrival_minutes=0.0,
                )
            )

            prev_node = 0

            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                curr_node = manager.IndexToNode(index)

                if curr_node == 0:
                    # Final depot return stop
                    step_dist = distance_matrix_km[prev_node][0]
                    step_dur = duration_matrix_min[prev_node][0]
                    route_distance_km += step_dist
                    route_duration_min += step_dur
                    seq += 1

                    stops.append(
                        RouteStop(
                            sequence_number=seq,
                            point_id=None,
                            name=f"{input_data.depot.name} (Return)",
                            latitude=input_data.depot.latitude,
                            longitude=input_data.depot.longitude,
                            waste_kg=0.0,
                            accumulated_waste_kg=round(route_waste_kg, 2),
                            accumulated_distance_km=round(route_distance_km, 2),
                            estimated_arrival_minutes=round(route_duration_min, 2),
                        )
                    )
                else:
                    visited_nodes.add(curr_node)
                    cp = valid_collection_points[curr_node - 1]
                    step_dist = distance_matrix_km[prev_node][curr_node]
                    step_dur = duration_matrix_min[prev_node][curr_node]

                    route_distance_km += step_dist
                    route_duration_min += step_dur
                    route_waste_kg += cp.estimated_waste_kg
                    seq += 1

                    stops.append(
                        RouteStop(
                            sequence_number=seq,
                            point_id=cp.id,
                            name=cp.name,
                            latitude=cp.latitude,
                            longitude=cp.longitude,
                            waste_kg=cp.estimated_waste_kg,
                            accumulated_waste_kg=round(route_waste_kg, 2),
                            accumulated_distance_km=round(route_distance_km, 2),
                            estimated_arrival_minutes=round(route_duration_min, 2),
                        )
                    )

                prev_node = curr_node

            utilization = (
                round((route_waste_kg / vehicle_node.capacity_kg) * 100.0, 2)
                if vehicle_node.capacity_kg > 0
                else 0.0
            )

            # Only include route if vehicle visited at least one collection point
            # or include empty route with depot stops
            has_collection_stops = len(stops) > 2

            routes_output.append(
                VehicleRoute(
                    vehicle_id=vehicle_node.id,
                    vehicle_number=vehicle_node.vehicle_number,
                    capacity_kg=vehicle_node.capacity_kg,
                    stops=stops if has_collection_stops else [stops[0]],
                    total_distance_km=round(route_distance_km, 2) if has_collection_stops else 0.0,
                    total_duration_minutes=round(route_duration_min, 2) if has_collection_stops else 0.0,
                    total_waste_kg=round(route_waste_kg, 2) if has_collection_stops else 0.0,
                    utilization_percentage=utilization if has_collection_stops else 0.0,
                )
            )

            if has_collection_stops:
                total_opt_distance_km += route_distance_km
                total_opt_duration_min += route_duration_min
                total_opt_waste_kg += route_waste_kg

        # Check for unassigned valid collection points (dropped by solver)
        for node in range(1, num_nodes):
            if node not in visited_nodes:
                cp = valid_collection_points[node - 1]
                unassigned_points.append(
                    UnassignedPoint(
                        point_id=cp.id,
                        name=cp.name,
                        estimated_waste_kg=cp.estimated_waste_kg,
                        priority_score=cp.priority_score,
                        reason="Fleet capacity limit reached or route infeasible within constraints.",
                    )
                )

        fleet_utilization = (
            round((total_opt_waste_kg / total_fleet_capacity) * 100.0, 2)
            if total_fleet_capacity > 0
            else 0.0
        )

        final_status = (
            "OPTIMAL" if not unassigned_points else "FEASIBLE"
        )
        if unassigned_points and total_demand > total_fleet_capacity:
            final_status = "INSUFFICIENT_CAPACITY"

        return OptimizationOutput(
            status=final_status,
            routes=routes_output,
            unassigned_points=unassigned_points,
            total_distance_km=round(total_opt_distance_km, 2),
            total_duration_minutes=round(total_opt_duration_min, 2),
            total_waste_collected_kg=round(total_opt_waste_kg, 2),
            fleet_utilization_percentage=fleet_utilization,
            warnings=warnings,
        )


cvrp_solver = CVRPSolver()

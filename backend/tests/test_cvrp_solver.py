import pytest
from app.optimization import (
    CVRPSolver,
    cvrp_solver,
    OptimizationInput,
    DepotNode,
    CollectionPointNode,
    VehicleNode,
)
from app.services.osrm_service import haversine_matrix


@pytest.fixture
def swargate_depot():
    return DepotNode(
        id=1,
        name="Swargate Central Depot",
        latitude=18.5018,
        longitude=73.8636,
    )


def test_single_vehicle_single_route(swargate_depot):
    vehicles = [
        VehicleNode(id=1, vehicle_number="MH-12-PQ-1001", capacity_kg=1000.0)
    ]
    points = [
        CollectionPointNode(id=1, name="Baner Point", latitude=18.5590, longitude=73.7868, estimated_waste_kg=220.0, priority_score=75.0),
        CollectionPointNode(id=2, name="Wakad Point", latitude=18.5987, longitude=73.7621, estimated_waste_kg=310.0, priority_score=85.0),
        CollectionPointNode(id=3, name="Aundh Point", latitude=18.5602, longitude=73.8078, estimated_waste_kg=180.0, priority_score=50.0),
    ]

    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=points,
        vehicles=vehicles,
        time_limit_seconds=3,
    )

    result = cvrp_solver.solve(opt_input)

    assert result.status == "OPTIMAL"
    assert len(result.routes) == 1
    route = result.routes[0]

    # Starts at depot and ends at depot
    assert route.stops[0].name == swargate_depot.name
    assert route.stops[-1].name == f"{swargate_depot.name} (Return)"
    assert len(route.stops) == 5  # Depot -> 3 points -> Depot
    assert route.total_waste_kg == 710.0
    assert route.total_waste_kg <= route.capacity_kg
    assert route.total_distance_km > 0.0
    assert len(result.unassigned_points) == 0


def test_multi_vehicle_capacity_partitioning(swargate_depot):
    vehicles = [
        VehicleNode(id=1, vehicle_number="V1", capacity_kg=500.0),
        VehicleNode(id=2, vehicle_number="V2", capacity_kg=500.0),
    ]
    points = [
        CollectionPointNode(id=1, name="P1", latitude=18.5590, longitude=73.7868, estimated_waste_kg=260.0, priority_score=70.0),
        CollectionPointNode(id=2, name="P2", latitude=18.5987, longitude=73.7621, estimated_waste_kg=240.0, priority_score=80.0),
        CollectionPointNode(id=3, name="P3", latitude=18.5602, longitude=73.8078, estimated_waste_kg=250.0, priority_score=60.0),
        CollectionPointNode(id=4, name="P4", latitude=18.5074, longitude=73.8077, estimated_waste_kg=200.0, priority_score=65.0),
    ]

    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=points,
        vehicles=vehicles,
        time_limit_seconds=3,
    )

    result = cvrp_solver.solve(opt_input)

    assert result.status in ["OPTIMAL", "FEASIBLE"]
    assert len(result.routes) == 2

    for r in result.routes:
        # Strict capacity check
        assert r.total_waste_kg <= r.capacity_kg
        assert r.utilization_percentage <= 100.0

    assert result.total_waste_collected_kg == 950.0
    assert len(result.unassigned_points) == 0


def test_rule_16_infeasible_point_exceeding_max_capacity(swargate_depot):
    vehicles = [
        VehicleNode(id=1, vehicle_number="V1", capacity_kg=500.0),
        VehicleNode(id=2, vehicle_number="V2", capacity_kg=400.0),
    ]
    # Point 1 is 700 kg which exceeds maximum single vehicle capacity of 500 kg
    points = [
        CollectionPointNode(id=1, name="Massive Point", latitude=18.5590, longitude=73.7868, estimated_waste_kg=700.0, priority_score=90.0),
        CollectionPointNode(id=2, name="Feasible Point 1", latitude=18.5987, longitude=73.7621, estimated_waste_kg=200.0, priority_score=70.0),
        CollectionPointNode(id=3, name="Feasible Point 2", latitude=18.5602, longitude=73.8078, estimated_waste_kg=250.0, priority_score=60.0),
    ]

    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=points,
        vehicles=vehicles,
        time_limit_seconds=3,
    )

    result = cvrp_solver.solve(opt_input)

    # Infeasible point must be reported in unassigned_points with clear reason
    assert len(result.unassigned_points) == 1
    unassigned = result.unassigned_points[0]
    assert unassigned.point_id == 1
    assert "exceeds maximum single vehicle capacity" in unassigned.reason

    # Feasible points should still be solved and routed
    assert result.total_waste_collected_kg == 450.0
    for r in result.routes:
        assert r.total_waste_kg <= r.capacity_kg


def test_insufficient_total_capacity_priority_handling(swargate_depot):
    # Fleet capacity: 500 kg
    vehicles = [
        VehicleNode(id=1, vehicle_number="V1", capacity_kg=500.0)
    ]
    # Total demand: 250 + 250 + 400 = 900 kg (> 500 kg)
    points = [
        CollectionPointNode(id=1, name="Critical Point 1", latitude=18.5590, longitude=73.7868, estimated_waste_kg=250.0, priority_score=95.0),
        CollectionPointNode(id=2, name="Critical Point 2", latitude=18.5602, longitude=73.8078, estimated_waste_kg=250.0, priority_score=90.0),
        CollectionPointNode(id=3, name="Low Priority Point", latitude=18.5987, longitude=73.7621, estimated_waste_kg=400.0, priority_score=15.0),
    ]

    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=points,
        vehicles=vehicles,
        time_limit_seconds=3,
    )

    result = cvrp_solver.solve(opt_input)

    assert result.status == "INSUFFICIENT_CAPACITY"
    # The 500kg capacity vehicle should pick Critical Points 1 & 2 (total 500kg)
    assert result.total_waste_collected_kg == 500.0
    assert result.routes[0].total_waste_kg == 500.0

    # Low priority point should be in unassigned_points
    assert len(result.unassigned_points) == 1
    assert result.unassigned_points[0].point_id == 3


def test_no_vehicles_available(swargate_depot):
    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=[
            CollectionPointNode(id=1, name="P1", latitude=18.55, longitude=73.78, estimated_waste_kg=100.0)
        ],
        vehicles=[],
    )
    result = cvrp_solver.solve(opt_input)
    assert result.status == "NO_VEHICLES_AVAILABLE"
    assert len(result.routes) == 0


def test_no_collection_points(swargate_depot):
    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=[],
        vehicles=[
            VehicleNode(id=1, vehicle_number="V1", capacity_kg=500.0)
        ],
    )
    result = cvrp_solver.solve(opt_input)
    assert result.status == "NO_COLLECTION_POINTS"
    assert len(result.routes) == 0


def test_cvrp_with_full_pune_demo_dataset(swargate_depot):
    # 5 Vehicles with capacities ranging from 800 to 1500 kg (Total 5500 kg)
    vehicles = [
        VehicleNode(id=1, vehicle_number="MH-12-PQ-1001", capacity_kg=1200.0),
        VehicleNode(id=2, vehicle_number="MH-12-PQ-1002", capacity_kg=1000.0),
        VehicleNode(id=3, vehicle_number="MH-12-PQ-1003", capacity_kg=800.0),
        VehicleNode(id=4, vehicle_number="MH-14-AZ-2004", capacity_kg=1500.0),
        VehicleNode(id=5, vehicle_number="MH-14-AZ-2005", capacity_kg=1000.0),
    ]

    # Sample 15 distinct collection points across Pune
    points_raw = [
        ("Baner Plastic Bin #1", 18.5590, 73.7868, 220.0, 75.0),
        ("Wakad IT Park Collection", 18.5987, 73.7621, 310.0, 85.0),
        ("Hinjewadi Phase 1 Bin", 18.5912, 73.7389, 450.0, 95.0),
        ("Aundh Commercial Hub", 18.5602, 73.8078, 180.0, 50.0),
        ("Kothrud Depot Yard", 18.5074, 73.8077, 260.0, 70.0),
        ("Viman Nagar Mall Bin", 18.5679, 73.9143, 380.0, 88.0),
        ("Kalyani Nagar Recycling", 18.5463, 73.9034, 150.0, 25.0),
        ("Hadapsar Industrial Bin", 18.5158, 73.9272, 420.0, 92.0),
        ("Shivajinagar Station Point", 18.5308, 73.8475, 200.0, 55.0),
        ("FC Road Commercial Bin", 18.5236, 73.8412, 290.0, 78.0),
        ("Deccan Gymkhana Stop", 18.5167, 73.8415, 170.0, 45.0),
        ("Camp MG Road Center", 18.5165, 73.8762, 240.0, 68.0),
        ("Swargate Bus Stand Yard", 18.5005, 73.8580, 310.0, 82.0),
        ("Bibwewadi Market Yard", 18.4735, 73.8643, 210.0, 52.0),
        ("Katraj Zoo Recycling Point", 18.4529, 73.8569, 280.0, 72.0),
    ]

    collection_points = [
        CollectionPointNode(
            id=i + 1,
            name=name,
            latitude=lat,
            longitude=lng,
            estimated_waste_kg=qty,
            priority_score=prio,
        )
        for i, (name, lat, lng, qty, prio) in enumerate(points_raw)
    ]

    opt_input = OptimizationInput(
        depot=swargate_depot,
        collection_points=collection_points,
        vehicles=vehicles,
        time_limit_seconds=4,
    )

    result = cvrp_solver.solve(opt_input)

    assert result.status in ["OPTIMAL", "FEASIBLE"]
    assert result.total_waste_collected_kg == sum(p.estimated_waste_kg for p in collection_points)
    assert len(result.unassigned_points) == 0

    # Ensure all vehicle routes respect capacity constraints
    for route in result.routes:
        assert route.total_waste_kg <= route.capacity_kg
        assert route.utilization_percentage <= 100.0
        if len(route.stops) > 1:
            assert route.stops[0].name == swargate_depot.name
            assert "Return" in route.stops[-1].name

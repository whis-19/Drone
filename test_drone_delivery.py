import pytest
from models.package import Package
from models.drone import Drone
from delivery_planner import DeliveryPlanner
from algorithms.shortest_path import ShortestPathFinder

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear path cache before each test."""
    ShortestPathFinder.clear_cache()

def test_basic_delivery():
    """Test Case 1: Basic Functionality Test
    Tests basic delivery functionality with a small map and simple routes."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 4.0, 200, "CityC")
    ]
    drones = [Drone(1, 20.0, 100.0)]  # Generous limits
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    assert all(isinstance(plan, dict) for plan in delivery_plans)
    assert all('drone_id' in plan for plan in delivery_plans)
    assert all('packages' in plan for plan in delivery_plans)
    assert all('route' in plan for plan in delivery_plans)
    assert all('total_distance' in plan for plan in delivery_plans)
    assert all('total_value' in plan for plan in delivery_plans)

def test_constraint_handling():
    """Test Case 2: Constraint Handling Test
    Tests handling of weight and distance constraints with a larger map."""
    planner = DeliveryPlanner()
    # Create a larger map
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    planner.add_route("CityC", "CityD", 25)
    planner.add_route("CityD", "CityE", 30)
    
    packages = [
        Package(1, 8.0, 100, "CityA"),   # Heavy package
        Package(2, 2.0, 200, "CityB"),   # Light but valuable
        Package(3, 12.0, 150, "CityC"),  # Very heavy
        Package(4, 3.0, 180, "CityD"),   # Medium weight, high value
        Package(5, 5.0, 120, "CityE")    # Medium weight, medium value
    ]
    
    drones = [
        Drone(1, 10.0, 40.0),  # Limited weight and distance
        Drone(2, 15.0, 60.0)   # Higher limits
    ]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    for plan in delivery_plans:
        # Check weight constraints
        total_weight = sum(p.weight for p in plan['packages'])
        drone = next(d for d in drones if d.id == plan['drone_id'])
        assert total_weight <= drone.max_weight
        
        # Check distance constraints
        assert plan['total_distance'] <= drone.max_distance

def test_optimization_and_edge_cases():
    """Test Case 3: Optimization & Edge Case Test
    Tests optimization and handling of complex scenarios."""
    planner = DeliveryPlanner()
    # Create a map with potential dead ends
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    planner.add_route("CityC", "CityD", 25)
    planner.add_route("CityD", "CityE", 30)
    planner.add_route("CityE", "CityF", 35)  # Dead end
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 4.0, 200, "CityC"),
        Package(4, 6.0, 180, "CityD"),
        Package(5, 7.0, 160, "CityE"),
        Package(6, 8.0, 140, "CityF")  # Package to dead end
    ]
    
    drones = [Drone(1, 15.0, 50.0)]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    # Check that high-value packages are prioritized
    first_plan = delivery_plans[0]
    first_plan_packages = first_plan['packages']
    
    # Verify that the selected packages have high value-to-weight ratio
    for package in first_plan_packages:
        value_weight_ratio = package.value_weight_ratio
        assert value_weight_ratio >= 20  # Assuming good value-to-weight ratio

def test_no_feasible_trips():
    """Test Case: No Feasible Trips
    Tests handling of scenarios where no valid delivery is possible."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    
    packages = [
        Package(1, 20.0, 100, "CityA"),  # Too heavy
        Package(2, 15.0, 150, "CityA")   # Too heavy
    ]
    
    drones = [Drone(1, 10.0, 5.0)]  # Very limited capacity
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) == 0  # No feasible trips should be found

def test_route_deactivation():
    """Test route deactivation functionality."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    
    packages = [Package(1, 5.0, 100, "CityB")]
    drones = [Drone(1, 10.0, 50.0)]
    
    # Plan with active route
    initial_plans = planner.plan_delivery(packages, drones)
    assert len(initial_plans) > 0
    
    # Deactivate route and replan
    planner.deactivate_route("CityA", "CityB")
    new_plans = planner.plan_delivery(packages, drones)
    
    # After deactivating the route, there should be no feasible path
    assert len(new_plans) == 0

def test_delivery_statistics():
    """Test delivery statistics calculation."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityA")
    ]
    drones = [Drone(1, 10.0, 50.0)]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    statistics = planner.get_delivery_statistics(delivery_plans)
    
    assert statistics['total_packages'] == 2
    assert statistics['total_value'] == 250
    assert statistics['total_distance'] == 20.0  # Single trip: 10 there + 10 back
    assert statistics['average_packages_per_trip'] == 2
    assert statistics['average_value_per_trip'] == 250
    assert statistics['average_distance_per_trip'] == 20.0

def test_multiple_drones():
    """Test Case: Multiple Drones with Different Capabilities
    Tests how the system handles multiple drones with varying capacities."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    
    packages = [
        Package(1, 8.0, 100, "CityA"),   # Heavy package
        Package(2, 3.0, 150, "CityB"),   # Light but valuable
        Package(3, 12.0, 150, "CityC"),  # Very heavy
        Package(4, 4.0, 180, "CityA"),   # Medium weight, high value
        Package(5, 5.0, 120, "CityB")    # Medium weight, medium value
    ]
    
    drones = [
        Drone(1, 10.0, 30.0),   # Light drone
        Drone(2, 15.0, 50.0),   # Medium drone
        Drone(3, 20.0, 70.0)    # Heavy drone
    ]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    # Verify that drones are used according to their capabilities
    for plan in delivery_plans:
        drone = next(d for d in drones if d.id == plan['drone_id'])
        total_weight = sum(p.weight for p in plan['packages'])
        assert total_weight <= drone.max_weight
        assert plan['total_distance'] <= drone.max_distance

def test_charging_stations():
    """Test Case: Charging Station Functionality
    Tests how the system handles cities with charging stations."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    
    # Add charging stations
    planner.add_city("CityA", has_charging_station=True)
    planner.add_city("CityB", has_charging_station=True)
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 4.0, 200, "CityC")
    ]
    
    drones = [Drone(1, 15.0, 30.0)]  # Limited range
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    # Verify that routes include charging stations when needed
    for plan in delivery_plans:
        route = plan['route']
        # Check if route includes charging stations
        assert "CityA" in route or "CityB" in route

def test_package_priority():
    """Test Case: Package Priority Handling
    Tests how the system handles packages with different priorities."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    
    packages = [
        Package(1, 5.0, 100, "CityA", priority=1),  # High priority
        Package(2, 3.0, 150, "CityB", priority=2),  # Medium priority
        Package(3, 4.0, 200, "CityA", priority=3)   # Low priority
    ]
    
    drones = [Drone(1, 10.0, 50.0)]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    # Verify that high priority packages are delivered first
    first_plan = delivery_plans[0]
    first_plan_packages = first_plan['packages']
    assert any(p.priority == 1 for p in first_plan_packages)

def test_complex_route_optimization():
    """Test Case: Complex Route Optimization
    Tests how the system optimizes routes in complex scenarios."""
    planner = DeliveryPlanner()
    # Create a complex network
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("Warehouse", "CityB", 15)
    planner.add_route("CityA", "CityB", 12)
    planner.add_route("CityA", "CityC", 20)
    planner.add_route("CityB", "CityC", 18)
    planner.add_route("CityC", "CityD", 25)
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 4.0, 200, "CityC"),
        Package(4, 6.0, 180, "CityD")
    ]
    
    drones = [Drone(1, 15.0, 60.0)]
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 0
    # Verify that routes are optimized
    for plan in delivery_plans:
        route = plan['route']
        # Check that the route doesn't contain unnecessary detours
        assert len(route) <= len(packages) * 2 + 1  # Maximum reasonable route length

def test_error_handling():
    """Test Case: Error Handling
    Tests how the system handles invalid inputs and edge cases."""
    planner = DeliveryPlanner()
    
    # Test invalid package
    with pytest.raises(ValueError):
        Package(1, -5.0, 100, "CityA")  # Negative weight
    
    # Test invalid drone
    with pytest.raises(ValueError):
        Drone(1, -10.0, 50.0)  # Negative max weight
    
    # Test invalid route
    with pytest.raises(ValueError):
        planner.add_route("Warehouse", "CityA", -10)  # Negative distance
    
    # Test non-existent city
    packages = [Package(1, 5.0, 100, "NonExistentCity")]
    drones = [Drone(1, 10.0, 50.0)]
    delivery_plans = planner.plan_delivery(packages, drones)
    assert len(delivery_plans) == 0  # No feasible trips for non-existent city

def test_multiple_trips():
    """Test Case: Multiple Trips per Drone
    Tests how the system handles multiple trips for a single drone."""
    planner = DeliveryPlanner()
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 4.0, 200, "CityA"),
        Package(4, 6.0, 180, "CityB")
    ]
    
    drones = [Drone(1, 8.0, 30.0)]  # Limited capacity
    
    delivery_plans = planner.plan_delivery(packages, drones)
    
    assert len(delivery_plans) > 1  # Should require multiple trips
    # Verify that each trip respects drone limits
    for plan in delivery_plans:
        total_weight = sum(p.weight for p in plan['packages'])
        assert total_weight <= drones[0].max_weight
        assert plan['total_distance'] <= drones[0].max_distance

if __name__ == "__main__":
    pytest.main([__file__]) 
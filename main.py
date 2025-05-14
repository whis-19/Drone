from models.package import Package
from models.drone import Drone
from delivery_planner import DeliveryPlanner

def main():
    # Create delivery planner
    planner = DeliveryPlanner()
    
    # Add cities and routes
    planner.add_route("Warehouse", "CityA", 10)
    planner.add_route("CityA", "CityB", 15)
    planner.add_route("CityB", "CityC", 20)
    planner.add_route("CityA", "CityC", 25)
    planner.add_route("CityC", "CityD", 30)
    planner.add_route("CityD", "CityE", 35)

    # Create packages
    packages = [
        Package(1, 5.0, 100, "CityA"),
        Package(2, 3.0, 150, "CityB"),
        Package(3, 7.0, 200, "CityC"),
        Package(4, 2.0, 80, "CityA"),
        Package(5, 4.0, 120, "CityD"),
        Package(6, 6.0, 180, "CityE")
    ]

    # Create drones
    drones = [
        Drone(1, 10.0, 50.0),
        Drone(2, 15.0, 75.0)
    ]

    # Plan deliveries
    delivery_plans = planner.plan_delivery(packages, drones)

    # Print delivery plans
    for plan in delivery_plans:
        planner.print_delivery_plan(plan)

    # Print statistics
    statistics = planner.get_delivery_statistics(delivery_plans)
    planner.print_delivery_statistics(statistics)

    # Demonstrate route deactivation
    print("\nDeactivating route between CityA and CityB...")
    planner.deactivate_route("CityA", "CityB")
    
    # Replan deliveries
    print("\nReplanning deliveries with deactivated route...")
    delivery_plans = planner.plan_delivery(packages, drones)
    
    # Print new delivery plans
    for plan in delivery_plans:
        planner.print_delivery_plan(plan)
    
    # Print new statistics
    statistics = planner.get_delivery_statistics(delivery_plans)
    planner.print_delivery_statistics(statistics)

if __name__ == "__main__":
    main() 
from typing import List, Dict, Optional
from models.city import City
from models.package import Package
from models.drone import Drone
from algorithms.shortest_path import ShortestPathFinder
from algorithms.package_selector import PackageSelector

class DeliveryPlanner:
    def __init__(self):
        self.cities: Dict[str, City] = {}
        self.warehouse: str = "Warehouse"
        self.cities[self.warehouse] = City(self.warehouse)

    def add_city(self, name: str, has_charging_station: bool = False) -> None:
        """Add a city to the delivery network."""
        if name not in self.cities:
            self.cities[name] = City(name)
            self.cities[name].has_charging_station = has_charging_station

    def add_route(self, city1: str, city2: str, distance: float) -> None:
        """Add a route between two cities."""
        self.add_city(city1)
        self.add_city(city2)
        self.cities[city1].add_connection(city2, distance)
        self.cities[city2].add_connection(city1, distance)

    def deactivate_route(self, city1: str, city2: str) -> None:
        """Deactivate a route between two cities."""
        if city1 in self.cities and city2 in self.cities:
            self.cities[city1].deactivate_route(city2)
            self.cities[city2].deactivate_route(city1)
            # Clear path cache when routes change
            ShortestPathFinder.clear_cache()

    def activate_route(self, city1: str, city2: str) -> None:
        """Activate a route between two cities."""
        if city1 in self.cities and city2 in self.cities:
            self.cities[city1].activate_route(city2)
            self.cities[city2].activate_route(city1)
            # Clear path cache when routes change
            ShortestPathFinder.clear_cache()

    def plan_delivery(self, packages: List[Package], drones: List[Drone]) -> List[Dict]:
        """
        Plan delivery routes for all drones.
        
        Args:
            packages: List of packages to deliver
            drones: List of available drones
            
        Returns:
            List of delivery plans
        """
        delivery_plans = []
        remaining_packages = packages.copy()

        for drone in drones:
            while remaining_packages:
                # Select packages for this trip
                selected_packages = PackageSelector.select_packages(
                    remaining_packages, drone, self.cities, self.warehouse
                )
                
                if not selected_packages:
                    break

                # Optimize delivery order
                ordered_packages = PackageSelector.optimize_delivery_order(
                    selected_packages, self.cities, self.warehouse
                )

                # Plan route for selected packages
                route = [self.warehouse]
                total_distance = 0
                current_city = self.warehouse

                # Visit each destination in order
                for package in ordered_packages:
                    path, distance = ShortestPathFinder.dijkstra(
                        self.cities, current_city, package.destination
                    )
                    
                    if distance == float('inf'):
                        break
                    
                    if total_distance + distance > drone.max_distance:
                        break
                        
                    route.extend(path[1:])  # Skip first city as it's already in route
                    total_distance += distance
                    current_city = package.destination

                # Return to warehouse
                path, distance = ShortestPathFinder.dijkstra(
                    self.cities, current_city, self.warehouse
                )
                
                if distance == float('inf') or total_distance + distance > drone.max_distance:
                    break

                route.extend(path[1:])
                total_distance += distance

                # Create delivery plan
                plan = {
                    'drone_id': drone.id,
                    'packages': selected_packages,
                    'route': route,
                    'total_distance': total_distance,
                    'total_value': sum(p.value for p in selected_packages)
                }
                delivery_plans.append(plan)

                # Remove delivered packages
                for package in selected_packages:
                    remaining_packages.remove(package)

        return delivery_plans

    def get_delivery_statistics(self, delivery_plans: List[Dict]) -> Dict:
        """
        Calculate statistics for the delivery plans.
        
        Args:
            delivery_plans: List of delivery plans
            
        Returns:
            Dictionary containing delivery statistics
        """
        if not delivery_plans:
            return {
                'total_packages': 0,
                'total_value': 0,
                'total_distance': 0,
                'average_packages_per_trip': 0,
                'average_value_per_trip': 0,
                'average_distance_per_trip': 0
            }

        total_packages = sum(len(plan['packages']) for plan in delivery_plans)
        total_value = sum(plan['total_value'] for plan in delivery_plans)
        total_distance = sum(plan['total_distance'] for plan in delivery_plans)
        num_trips = len(delivery_plans)

        return {
            'total_packages': total_packages,
            'total_value': total_value,
            'total_distance': total_distance,
            'average_packages_per_trip': total_packages / num_trips,
            'average_value_per_trip': total_value / num_trips,
            'average_distance_per_trip': total_distance / num_trips
        }

    def print_delivery_plan(self, plan: Dict) -> None:
        """Print a single delivery plan in a readable format."""
        print(f"\nDrone {plan['drone_id']} Delivery Plan:")
        print("Packages to deliver:")
        for package in plan['packages']:
            print(f"  - Package {package.id}: {package.weight}kg, ${package.value} to {package.destination}")
        print(f"Route: {' -> '.join(plan['route'])}")
        print(f"Total distance: {plan['total_distance']:.2f}")
        print(f"Total value: ${plan['total_value']:.2f}")

    def print_delivery_statistics(self, statistics: Dict) -> None:
        """Print delivery statistics in a readable format."""
        print("\nDelivery Statistics:")
        print(f"Total packages delivered: {statistics['total_packages']}")
        print(f"Total value delivered: ${statistics['total_value']:.2f}")
        print(f"Total distance traveled: {statistics['total_distance']:.2f}")
        print(f"Average packages per trip: {statistics['average_packages_per_trip']:.2f}")
        print(f"Average value per trip: ${statistics['average_value_per_trip']:.2f}")
        print(f"Average distance per trip: {statistics['average_distance_per_trip']:.2f}") 
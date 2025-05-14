from typing import List, Dict, Tuple
from models.package import Package
from models.drone import Drone
from algorithms.shortest_path import ShortestPathFinder

class PackageSelector:
    @staticmethod
    def select_packages(
        packages: List[Package],
        drone: Drone,
        cities: Dict[str, 'City'],
        start_city: str = "Warehouse"
    ) -> List[Package]:
        """
        Select packages using a modified knapsack approach that considers both
        value-to-weight ratio and delivery distance.
        
        Args:
            packages: List of available packages
            drone: Drone to carry packages
            cities: Dictionary of cities
            start_city: Starting city (usually warehouse)
            
        Returns:
            List of selected packages
        """
        if not packages or not drone.is_valid():
            return []

        # Calculate value-to-weight ratios and distances for all packages
        package_info = []
        for package in packages:
            if not package.is_valid():
                continue
                
            # Get distance to package destination
            path, distance = ShortestPathFinder.dijkstra(cities, start_city, package.destination)
            if distance == float('inf'):
                continue
                
            # Calculate return distance
            return_path, return_distance = ShortestPathFinder.dijkstra(
                cities, package.destination, start_city
            )
            if return_distance == float('inf'):
                continue
                
            total_distance = distance + return_distance
            
            # Skip if total distance exceeds drone's range
            if total_distance > drone.max_distance:
                continue
                
            package_info.append({
                'package': package,
                'value_weight_ratio': package.value_weight_ratio,
                'total_distance': total_distance,
                'score': package.value_weight_ratio / (total_distance + 1)  # Avoid division by zero
            })

        # Sort packages by score (value-weight ratio / distance)
        package_info.sort(key=lambda x: x['score'], reverse=True)

        # Select packages using modified knapsack
        selected_packages = []
        remaining_weight = drone.max_weight
        total_distance = 0

        for info in package_info:
            package = info['package']
            if package.weight <= remaining_weight:
                # Check if adding this package would exceed drone's range
                if total_distance + info['total_distance'] <= drone.max_distance:
                    selected_packages.append(package)
                    remaining_weight -= package.weight
                    total_distance += info['total_distance']

        return selected_packages

    @staticmethod
    def optimize_delivery_order(
        packages: List[Package],
        cities: Dict[str, 'City'],
        start_city: str = "Warehouse"
    ) -> List[Package]:
        """
        Optimize the delivery order of packages to minimize total distance.
        Uses a simple nearest neighbor approach.
        
        Args:
            packages: List of packages to deliver
            cities: Dictionary of cities
            start_city: Starting city (usually warehouse)
            
        Returns:
            List of packages in optimized delivery order
        """
        if not packages:
            return []

        # Group packages by destination
        packages_by_destination: Dict[str, List[Package]] = {}
        for package in packages:
            if package.destination not in packages_by_destination:
                packages_by_destination[package.destination] = []
            packages_by_destination[package.destination].append(package)

        # Find optimal order of destinations
        current_city = start_city
        ordered_destinations = []
        remaining_destinations = set(packages_by_destination.keys())

        while remaining_destinations:
            nearest_destination = None
            min_distance = float('inf')

            for destination in remaining_destinations:
                path, distance = ShortestPathFinder.dijkstra(cities, current_city, destination)
                if distance < min_distance:
                    min_distance = distance
                    nearest_destination = destination

            if nearest_destination is None:
                break

            ordered_destinations.append(nearest_destination)
            remaining_destinations.remove(nearest_destination)
            current_city = nearest_destination

        # Create ordered package list
        ordered_packages = []
        for destination in ordered_destinations:
            ordered_packages.extend(packages_by_destination[destination])

        return ordered_packages 
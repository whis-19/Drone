from typing import Dict, List, Tuple, Set
import heapq
from models.city import City
from functools import lru_cache

class ShortestPathFinder:
    _path_cache: Dict[Tuple[str, str], Tuple[List[str], float]] = {}
    
    @staticmethod
    def clear_cache():
        """Clear the path cache."""
        ShortestPathFinder._path_cache.clear()
    
    @staticmethod
    def dijkstra(cities: Dict[str, City], start: str, end: str) -> Tuple[List[str], float]:
        """
        Find shortest path using Dijkstra's algorithm with caching.
        
        Args:
            cities: Dictionary of cities
            start: Starting city name
            end: Destination city name
            
        Returns:
            Tuple of (path, total_distance)
        """
        # Check cache first
        cache_key = (start, end)
        if cache_key in ShortestPathFinder._path_cache:
            return ShortestPathFinder._path_cache[cache_key]

        if start not in cities or end not in cities:
            return [], float('inf')

        distances = {city: float('inf') for city in cities}
        distances[start] = 0
        previous = {city: None for city in cities}
        pq = [(0, start)]
        visited: Set[str] = set()

        while pq:
            current_distance, current_city = heapq.heappop(pq)
            
            if current_city == end:
                break

            if current_city in visited:
                continue
                
            visited.add(current_city)

            for neighbor, route in cities[current_city].connections.items():
                if not route.is_active:
                    continue
                    
                if neighbor in visited:
                    continue

                new_distance = current_distance + route.distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_city
                    heapq.heappush(pq, (new_distance, neighbor))

        if distances[end] == float('inf'):
            return [], float('inf')

        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        
        result = (path[::-1], distances[end])
        
        # Cache the result
        ShortestPathFinder._path_cache[cache_key] = result
        return result

    @staticmethod
    def find_all_shortest_paths(cities: Dict[str, City], start: str) -> Dict[str, Tuple[List[str], float]]:
        """
        Find shortest paths from start city to all other cities.
        Uses caching for efficiency.
        
        Args:
            cities: Dictionary of cities
            start: Starting city name
            
        Returns:
            Dictionary mapping destination cities to (path, distance) tuples
        """
        if start not in cities:
            return {}

        paths = {}
        for city in cities:
            if city == start:
                continue
            path, distance = ShortestPathFinder.dijkstra(cities, start, city)
            if distance != float('inf'):
                paths[city] = (path, distance)

        return paths 
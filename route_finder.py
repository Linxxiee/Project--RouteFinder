import json
import heapq
import os


def _process_route_finder_logic(route_finder_instance, start, end, metric):
    """
    Thin wrapper used for integration testing.
    """
    return route_finder_instance.find_route(start, end, metric)


class RouteFinder:
    def __init__(self, graph=None):
        """
        graph is expected in this format:
        {
            'A': {'B': {'distance': 10, 'time': 5}},
            ...
        }
        """
        self.graph = graph if graph else {}

    # -------------------------------------------------------------
    # Core Shortest Path Function (Dijkstra)
    # -------------------------------------------------------------
    def find_route(self, start, end, metric="distance"):
        if metric not in ["distance", "time"]:
            raise ValueError("Unsupported metric. Use 'distance' or 'time'.")

        if start not in self.graph or end not in self.graph:
            return {"total_distance": float("inf"), "path": []}

        if start == end:
            return {"total_distance": 0, "path": [start]}

        pq = [(0, start, [start])]
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)

            if node == end:
                return {"total_distance": cost, "path": path}

            for neighbor, info in self.graph.get(node, {}).items():
                weight = info.get(metric, float("inf"))
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))

        return {"total_distance": float("inf"), "path": []}

    # -------------------------------------------------------------
    # Load new nodes and edges dynamically
    # -------------------------------------------------------------
    def load_new_data(self, filepath):
        """Loads a JSON file and merges nodes/edges into the current graph."""
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "r") as file:
                new_data = json.load(file)

            for node, edges in new_data.items():
                if node not in self.graph:
                    self.graph[node] = {}
                for neighbor, attrs in edges.items():
                    self.graph[node][neighbor] = attrs

            return True
        except Exception:
            return False

import json
import heapq

class RouteFinder:
    def __init__(self, graph=None):
        # Graph format: {'A': {'B': {'distance': 5, 'time': 2}, ...}, ...}
        self.graph = graph if graph else {}

    def find_route(self, start, end, metric="distance"):
        if start == end:
            return {"path": [start], "total_distance": 0}

        if start not in self.graph or end not in self.graph:
            return {"path": [], "total_distance": float("inf")}

        # Dijkstra's algorithm
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            total, node, path = heapq.heappop(queue)
            if node == end:
                return {"path": path, "total_distance": total}

            if node in visited:
                continue
            visited.add(node)

            for neighbor, props in self.graph.get(node, {}).items():
                if neighbor not in visited:
                    heapq.heappush(queue, (total + props[metric], neighbor, path + [neighbor]))

        return {"path": [], "total_distance": float("inf")}

    def load_new_data(self, json_file):
        try:
            with open(json_file, "r") as f:
                new_graph = json.load(f)
            self.graph.update(new_graph)
            return True
        except Exception:
            return False

# Optional wrapper for testing integration logic
def _process_route_finder_logic(route_finder_instance, start, end, metric):
    return route_finder_instance.find_route(start, end, metric)

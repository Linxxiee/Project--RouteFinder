import json
import heapq


class RouteFinder:
    def __init__(self, graph=None):
        self.graph = dict(graph) if graph else {}

    def load_new_data(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                new_data = json.load(f)

            if not isinstance(new_data, dict):
                return False

            for node, edges in new_data.items():
                if node not in self.graph:
                    self.graph[node] = {}

                if isinstance(edges, dict):
                    self.graph[node].update(edges)

                    # Ensure neighbor nodes exist as keys
                    for neighbor in edges:
                        if neighbor not in self.graph:
                            self.graph[neighbor] = {}

            return True
        except Exception:
            return False

    def find_route(self, start, end, mode="distance"):
        return _process_route_finder_logic(self, start, end, mode)


def _process_route_finder_logic(route_finder, start, end, mode):
    graph = route_finder.graph

    if start == end:
        return {"path": [start], "total_distance": 0}

    if start not in graph or end not in graph:
        return {"path": [], "total_distance": float("inf")}

    pq = [(0, start, [start])]
    visited = {}

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node == end:
            return {"path": path, "total_distance": cost}

        if node in visited and visited[node] <= cost:
            continue

        visited[node] = cost

        for neighbor, data in graph.get(node, {}).items():
            weight = data.get(mode, float("inf"))
            new_cost = cost + weight

            if neighbor not in visited or new_cost < visited.get(neighbor, float("inf")):
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    return {"path": [], "total_distance": float("inf")}

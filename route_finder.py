# route_finder.py
import json
import heapq
from typing import Dict, Any, Tuple


class RouteFinder:
    """
    Lightweight graph route finder supporting 'distance' and 'time' weights.
    Graph format:
    {
      "A": {"B": {"distance": 5, "time": 2}, "C": {...}},
      "B": {"C": {"distance": 7, "time": 3}},
      ...
    }
    """

    def __init__(self, graph: Dict[str, Dict[str, Dict[str, float]]] = None):
        # Ensure we have a shallow copy so tests that mutate graph won't surprise callers
        self.graph = dict(graph) if graph else {}

    def load_new_data(self, file_path: str) -> bool:
        """
        Load new graph data from a JSON file and merge into self.graph.

        Guarantees:
        - Adds new nodes and edges.
        - Ensures that every neighbor referenced exists as a key in self.graph
          (with an empty dict if no outgoing edges were provided). This matches
          tests that expect 'F' to be present as a key after loading neighbors.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                new_data = json.load(f)

            # Validate format is mapping-like
            if not isinstance(new_data, dict):
                return False

            for node, edges in new_data.items():
                if node not in self.graph:
                    self.graph[node] = {}

                # Merge/overwrite edges for the node
                if isinstance(edges, dict):
                    self.graph[node].update(edges)
                else:
                    # If malformed, skip this node
                    continue

                # Ensure every neighbor exists as a key (possibly with empty dict)
                for neighbor in edges.keys():
                    if neighbor not in self.graph:
                        self.graph[neighbor] = {}

            return True
        except Exception:
            return False

    def find_route(self, start: str, end: str, mode: str = "distance") -> dict:
        """
        Public wrapper that calls the shared algorithm.
        """
        return _process_route_finder_logic(self, start, end, mode)


def _process_route_finder_logic(route_finder: RouteFinder, start: str, end: str, mode: str = "distance") -> dict:
    """
    Dijkstra's algorithm over the directed weighted graph stored in route_finder.graph.

    Returns:
        {"path": [...], "total_distance": cost}
        - If unreachable: path=[], total_distance=float('inf')
        - If start == end: path=[start], total_distance=0
    Note: The key name "total_distance" is kept because your tests assert this key.
    """
    graph = route_finder.graph

    # If start equals end, return immediately with cost 0 (even if node has no outgoing edges)
    if start == end:
        return {"path": [start], "total_distance": 0}

    # End must exist in graph as a key to be considered reachable
    if start not in graph or end not in graph:
        return {"path": [], "total_distance": float("inf")}

    # Priority queue entries: (cost_so_far, current_node, path_list)
    pq: list[Tuple[float, str, list]] = [(0.0, start, [start])]
    best_costs: Dict[str, float] = {}

    while pq:
        cost, node, path = heapq.heappop(pq)

        # If we reach destination, return result
        if node == end:
            return {"path": path, "total_distance": cost}

        # Skip if we already have a better cost recorded
        if node in best_costs and best_costs[node] <= cost:
            continue
        best_costs[node] = cost

        # Traverse neighbors
        for neighbor, attrs in graph.get(node, {}).items():
            # attrs is expected to be a dict with e.g. {"distance": 5, "time": 2}
            weight = attrs.get(mode, float("inf"))
            if weight is None:
                weight = float("inf")

            new_cost = cost + weight
            # Only push if we haven't seen a better path to neighbor
            if neighbor not in best_costs or new_cost < best_costs.get(neighbor, float("inf")):
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    # No route found
    return {"path": [], "total_distance": float("inf")}

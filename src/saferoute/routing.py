import heapq
import math


class RoadNetwork:
    """Directed weighted graph representing Ridgeview's road network and intersections."""

    def __init__(self) -> None:
        self._adj: dict[str, list[tuple[str, float]]] = {}
        self._coords: dict[str, tuple[float, float]] = {}

    def add_location(self, name: str, x: float = 0.0, y: float = 0.0) -> None:
        """Register an intersection, depot, or suburb node with optional (x, y) coordinates."""
        self._adj.setdefault(name, [])
        self._coords[name] = (x, y)

    def add_road(
        self, source: str, destination: str, travel_minutes: float, one_way: bool = False
    ) -> None:
        """Add a weighted road segment (directed if one_way=True, bidirectional otherwise)."""
        if travel_minutes < 0:
            raise ValueError("Road travel time cannot be negative.")
        self._adj.setdefault(source, [])
        self._adj.setdefault(destination, [])
        self._adj[source].append((destination, travel_minutes))
        if not one_way:
            self._adj[destination].append((source, travel_minutes))

    def has_path_dfs(
        self, start: str, goal: str, visited: set[str] | None = None
    ) -> list[str] | None:
        """Recursive Depth-First Search returning a valid path from start to goal, or None."""
        if start not in self._adj or goal not in self._adj:
            return None

        if visited is None:
            visited = set()

        # Base case: reached destination
        if start == goal:
            return [start]

        visited.add(start)

        # Recursive case: explore unvisited outgoing roads
        for neighbor, _ in self._adj[start]:
            if neighbor not in visited:
                sub_path = self.has_path_dfs(neighbor, goal, visited)
                if sub_path is not None:
                    return [start] + sub_path

        return None

    def _heuristic(self, node: str, goal: str) -> float:
        """Euclidean distance heuristic between two nodes with known coordinates."""
        if node not in self._coords or goal not in self._coords:
            return 0.0
        x1, y1 = self._coords[node]
        x2, y2 = self._coords[goal]
        return math.hypot(x2 - x1, y2 - y1)

    def shortest_path_dijkstra(self, start: str, goal: str) -> tuple[float, list[str]]:
        """Compute fastest route using Dijkstra's algorithm in O((V + E) log V) time."""
        return self._best_first_search(start, goal, use_heuristic=False)

    def shortest_path_astar(self, start: str, goal: str) -> tuple[float, list[str]]:
        """Compute fastest route using A* search guided by Euclidean distance heuristic."""
        return self._best_first_search(start, goal, use_heuristic=True)

    def _best_first_search(
        self, start: str, goal: str, use_heuristic: bool
    ) -> tuple[float, list[str]]:
        if start not in self._adj or goal not in self._adj:
            raise ValueError(f"Unknown start '{start}' or goal '{goal}' location.")

        # Priority queue stores (f_score, g_score, current_node)
        open_heap: list[tuple[float, float, str]] = [(0.0, 0.0, start)]
        best_g: dict[str, float] = {start: 0.0}
        came_from: dict[str, str | None] = {start: None}

        while open_heap:
            _, current_g, current = heapq.heappop(open_heap)

            if current == goal:
                path: list[str] = []
                node: str | None = goal
                while node is not None:
                    path.append(node)
                    node = came_from[node]
                return current_g, path[::-1]

            # Skip stale queue entries
            if current_g > best_g.get(current, float("inf")):
                continue

            for neighbor, weight in self._adj[current]:
                tentative_g = current_g + weight
                if tentative_g < best_g.get(neighbor, float("inf")):
                    best_g[neighbor] = tentative_g
                    came_from[neighbor] = current
                    h_score = self._heuristic(neighbor, goal) if use_heuristic else 0.0
                    heapq.heappush(open_heap, (tentative_g + h_score, tentative_g, neighbor))

        return float("inf"), []
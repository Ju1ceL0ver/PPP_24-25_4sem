from app.schemas.graph import Graph, PathResult

def solve_tsp(graph: Graph) -> PathResult:
    path = [graph.nodes[0]]
    remaining = set(graph.nodes[1:])
    while remaining:
        current = path[-1]
        next_node = min(remaining, key=lambda x: 1 if [current, x] in graph.edges or [x, current] in graph.edges else float('inf'))
        path.append(next_node)
        remaining.remove(next_node)
    total_distance = len(path) - 1
    return PathResult(path=path, total_distance=total_distance)
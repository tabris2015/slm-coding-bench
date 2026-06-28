from solution import topological_sort


def _is_valid(n, edges, order):
    if sorted(order) != list(range(n)):
        return False
    pos = {node: i for i, node in enumerate(order)}
    return all(pos[u] < pos[v] for u, v in edges)


def test_simple_chain():
    assert topological_sort(2, [[0, 1]]) == [0, 1]


def test_branching_valid():
    order = topological_sort(3, [[0, 1], [0, 2]])
    assert _is_valid(3, [[0, 1], [0, 2]], order)


def test_cycle_two_nodes():
    assert topological_sort(2, [[0, 1], [1, 0]]) == []


def test_self_loop_is_cycle():
    assert topological_sort(1, [[0, 0]]) == []


def test_no_edges_is_permutation():
    order = topological_sort(4, [])
    assert sorted(order) == [0, 1, 2, 3]


def test_single_node():
    assert topological_sort(1, []) == [0]


def test_larger_dag_valid():
    edges = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4]]
    order = topological_sort(5, edges)
    assert _is_valid(5, edges, order)


def test_cycle_in_larger_graph():
    edges = [[0, 1], [1, 2], [2, 3], [3, 1]]
    assert topological_sort(4, edges) == []


def test_disconnected_components():
    edges = [[0, 1], [2, 3]]
    order = topological_sort(4, edges)
    assert _is_valid(4, edges, order)

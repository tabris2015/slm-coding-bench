from collections import deque


def topological_sort(num_nodes, edges):
    indeg = [0] * num_nodes
    adj = [[] for _ in range(num_nodes)]
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(node for node in range(num_nodes) if indeg[node] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    if len(order) != num_nodes:
        return []
    return order

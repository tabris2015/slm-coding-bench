import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        num = r.randint(1, 8)
        edges = []
        # forward edges only -> acyclic so far
        for u in range(num):
            for v in range(u + 1, num):
                if r.random() < 0.35:
                    edges.append([u, v])
        # sometimes inject a back edge to force a cycle
        if r.random() < 0.4 and num >= 2:
            a = r.randint(0, num - 1)
            b = r.randint(0, num - 1)
            if a == b:
                edges.append([a, a])  # self-loop cycle
            else:
                lo, hi = min(a, b), max(a, b)
                edges.append([hi, lo])  # back edge
        r.shuffle(edges)
        cases.append({"n": num, "edges": [list(e) for e in edges]})
    return cases


def _has_cycle(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    for start in range(n):
        if color[start] != WHITE:
            continue
        stack = [(start, 0)]
        color[start] = GRAY
        while stack:
            node, idx = stack[-1]
            if idx < len(adj[node]):
                stack[-1] = (node, idx + 1)
                nxt = adj[node][idx]
                if color[nxt] == GRAY:
                    return True
                if color[nxt] == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, 0))
            else:
                color[node] = BLACK
                stack.pop()
    return False


def _classify(n, edges, order):
    if order == []:
        return "cycle" if _has_cycle(n, edges) or n == 0 else "invalid_empty"
    if sorted(order) != list(range(n)):
        return "invalid_perm"
    pos = {node: i for i, node in enumerate(order)}
    for u, v in edges:
        if pos[u] >= pos[v]:
            return "invalid_order"
    return "valid"


def run_case(impl, case):
    n = case["n"]
    edges = [list(e) for e in case["edges"]]
    order = impl(n, [list(e) for e in edges])
    return _classify(n, edges, order)

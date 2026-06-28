import random


def run_once(impl, size):
    r = random.Random(size)
    edges = []
    target = 2 * size
    for _ in range(target):
        u = r.randint(0, size - 2)
        v = r.randint(u + 1, size - 1)  # forward only -> acyclic
        edges.append([u, v])
    return impl(size, edges)

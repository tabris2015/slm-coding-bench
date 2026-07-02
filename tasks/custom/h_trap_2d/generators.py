import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        rows = r.randint(2, 6)
        cols = r.randint(2, 6)
        grid = [[r.randint(0, 9) for _ in range(cols)] for _ in range(rows)]
        cases.append(grid)
    return cases


def run_case(impl, case):
    return impl(case)

import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        length = r.randint(1, 7)
        cases.append([r.randint(1, 30) for _ in range(length)])
    return cases


def run_case(impl, case):
    return impl(case)

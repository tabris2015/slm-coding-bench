import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        choice = r.random()
        if choice < 0.10:
            cases.append(0)
        elif choice < 0.55:
            cases.append(r.randint(1, 1000))
        else:
            cases.append(r.randint(1000, 10**18))
    return cases


def run_case(impl, case):
    return impl(case)

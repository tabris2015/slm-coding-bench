import random


def make_inputs(seed, n):
    r = random.Random(seed)
    alpha = "abcd"
    cases = []
    for _ in range(n):
        la = r.randint(0, 8)
        lb = r.randint(0, 8)
        a = "".join(r.choice(alpha) for _ in range(la))
        b = "".join(r.choice(alpha) for _ in range(lb))
        cases.append([a, b])
    return cases


def run_case(impl, case):
    return impl(case[0], case[1])

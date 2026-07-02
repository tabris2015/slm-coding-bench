import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        if r.random() < 0.05:
            cases.append([])
            continue
        k = r.randint(1, 12)
        ivs = []
        for _ in range(k):
            s = r.randint(0, 15)
            e = s + r.randint(1, 8)
            w = r.randint(0, 10)
            ivs.append([s, e, w])
        cases.append(ivs)
    return cases


def run_case(impl, case):
    return impl(case)

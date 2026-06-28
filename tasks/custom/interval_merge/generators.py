import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        if r.random() < 0.08:
            cases.append([])
            continue
        m = r.randint(1, 12)
        intervals = []
        for _ in range(m):
            a = r.randint(0, 20)
            b = a + r.randint(0, 6)
            intervals.append([a, b])
        cases.append(intervals)
    return cases


def run_case(impl, case):
    intervals = [list(iv) for iv in case]
    out = impl(intervals)
    return [list(iv) for iv in out]

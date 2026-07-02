import random


def make_inputs(seed, n):
    r = random.Random(seed)
    base = ["a", "aa", "b", "ab", "ba", "aba"]
    cases = []
    for _ in range(n):
        k = r.randint(1, len(base))
        words = r.sample(base, k)
        m = r.randint(0, 5)
        s = "".join(r.choice(base) for _ in range(m))
        cases.append([s, words])
    return cases


def run_case(impl, case):
    return impl(case[0], case[1])

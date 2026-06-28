import random

ALPHABET = "abc"


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        la = r.randint(0, 8)
        lb = r.randint(0, 8)
        a = "".join(r.choice(ALPHABET) for _ in range(la))
        b = "".join(r.choice(ALPHABET) for _ in range(lb))
        cases.append({"a": a, "b": b})
    return cases


def run_case(impl, case):
    return impl(case["a"], case["b"])

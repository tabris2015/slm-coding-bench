import random


def run_once(impl, size):
    r = random.Random(size)
    out = "0"
    for _ in range(size):
        out = impl(r.randint(0, 10**18))
    return out

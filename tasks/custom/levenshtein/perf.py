import random

ALPHABET = "abcd"


def run_once(impl, size):
    r = random.Random(size)
    a = "".join(r.choice(ALPHABET) for _ in range(size))
    b = "".join(r.choice(ALPHABET) for _ in range(size))
    return impl(a, b)

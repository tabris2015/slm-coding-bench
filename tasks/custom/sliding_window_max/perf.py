import random


def run_once(impl, size):
    r = random.Random(size)
    data = [r.randint(-size, size) for _ in range(size)]
    k = max(1, size // 10)
    return impl(data, k)

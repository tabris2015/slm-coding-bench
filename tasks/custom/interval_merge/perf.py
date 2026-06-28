import random


def run_once(impl, size):
    r = random.Random(size)
    intervals = []
    for _ in range(size):
        a = r.randint(0, size)
        b = a + r.randint(0, 50)
        intervals.append([a, b])
    return impl(intervals)

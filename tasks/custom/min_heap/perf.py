import random


def run_once(impl, size):
    r = random.Random(size)
    obj = impl()
    for _ in range(size):
        obj.push(r.randint(-size, size))
    total = 0
    while len(obj):
        total += obj.pop()
    return total

import random


def run_once(impl, size):
    r = random.Random(size)
    capacity = max(1, size // 100)
    obj = impl(capacity)
    key_space = capacity * 2
    total = 0
    for _ in range(size):
        key = r.randint(0, key_space)
        if r.random() < 0.5:
            obj.put(key, r.randint(0, 1000))
        else:
            total += obj.get(key)
    return total

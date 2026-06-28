import random


def run_once(impl, size):
    r = random.Random(size)
    alphabet = "abc"
    chars = []
    while len(chars) < size:
        ch = r.choice(alphabet)
        run = r.randint(1, 6)
        chars.extend([ch] * run)
    return impl("".join(chars[:size]))

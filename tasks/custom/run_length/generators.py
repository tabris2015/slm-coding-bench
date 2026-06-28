import random


def make_inputs(seed, n):
    r = random.Random(seed)
    alphabet = "aabbc"
    cases = []
    for _ in range(n):
        if r.random() < 0.08:
            cases.append("")
            continue
        length = r.randint(1, 30)
        chars = []
        while len(chars) < length:
            ch = r.choice(alphabet)
            run = r.randint(1, 5)
            chars.extend([ch] * run)
        cases.append("".join(chars[:length]))
    return cases


def run_case(impl, case):
    return impl(case)

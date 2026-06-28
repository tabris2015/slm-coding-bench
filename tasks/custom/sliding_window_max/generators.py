import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        choice = r.random()
        if choice < 0.10:
            # edge: empty list
            cases.append({"nums": [], "k": r.randint(1, 3)})
            continue
        if choice < 0.20:
            # edge: k larger than length (invalid -> [])
            length = r.randint(1, 5)
            nums = [r.randint(-20, 20) for _ in range(length)]
            cases.append({"nums": nums, "k": length + r.randint(1, 3)})
            continue
        if choice < 0.30:
            # edge: k <= 0
            length = r.randint(1, 6)
            nums = [r.randint(-20, 20) for _ in range(length)]
            cases.append({"nums": nums, "k": r.randint(-2, 0)})
            continue
        # normal: valid k in 1..len(nums)
        length = r.randint(1, 12)
        nums = [r.randint(-20, 20) for _ in range(length)]
        k = r.randint(1, length)
        cases.append({"nums": nums, "k": k})
    return cases


def run_case(impl, case):
    return impl(list(case["nums"]), case["k"])

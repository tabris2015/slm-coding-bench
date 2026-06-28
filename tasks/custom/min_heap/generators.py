import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        num_ops = r.randint(20, 40)
        ops = []
        size = 0  # simulated heap size, so we never emit invalid pop/peek
        for _ in range(num_ops):
            if size == 0:
                # only push is valid
                ops.append(["push", r.randint(-50, 50)])
                size += 1
                continue
            choice = r.random()
            if choice < 0.5:
                ops.append(["push", r.randint(-50, 50)])
                size += 1
            elif choice < 0.8:
                ops.append(["pop"])
                size -= 1
            else:
                ops.append(["peek"])
        cases.append({"ops": ops})
    return cases


def run_case(impl, case):
    obj = impl()
    out = []
    for op in case["ops"]:
        if op[0] == "push":
            obj.push(op[1])
        elif op[0] == "pop":
            out.append(obj.pop())
        else:  # peek
            out.append(obj.peek())
    return out

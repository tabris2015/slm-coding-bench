import random


def make_inputs(seed, n):
    r = random.Random(seed)
    cases = []
    for _ in range(n):
        capacity = r.randint(1, 5)
        num_ops = r.randint(20, 40)
        ops = []
        for _ in range(num_ops):
            key = r.randint(0, 6)
            if r.random() < 0.5:
                ops.append(["put", key, r.randint(0, 100)])
            else:
                ops.append(["get", key])
        cases.append({"capacity": capacity, "ops": ops})
    return cases


def run_case(impl, case):
    obj = impl(case["capacity"])
    out = []
    for op in case["ops"]:
        if op[0] == "put":
            obj.put(op[1], op[2])
        else:  # get
            out.append(obj.get(op[1]))
    return out

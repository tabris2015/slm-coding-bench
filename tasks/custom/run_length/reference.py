from itertools import groupby


def rle_encode(s):
    parts = []
    for ch, group in groupby(s):
        parts.append(ch + str(sum(1 for _ in group)))
    return "".join(parts)

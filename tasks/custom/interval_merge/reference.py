def merge_intervals(intervals):
    if not intervals:
        return []
    ordered = sorted((list(iv) for iv in intervals), key=lambda iv: (iv[0], iv[1]))
    out = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = out[-1]
        if start <= last[1]:
            if end > last[1]:
                last[1] = end
        else:
            out.append([start, end])
    return out

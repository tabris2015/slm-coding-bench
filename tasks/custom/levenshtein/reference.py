def edit_distance(a, b):
    m, n = len(a), len(b)
    # prev[j] = edit distance between a[:i-1] and b[:j]
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        ai = a[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ai == b[j - 1] else 1
            cur[j] = min(
                prev[j] + 1,        # deletion
                cur[j - 1] + 1,     # insertion
                prev[j - 1] + cost, # substitution / match
            )
        prev = cur
    return prev[n]

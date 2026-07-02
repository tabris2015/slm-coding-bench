import bisect


def max_interval_weight(intervals):
    if not intervals:
        return 0
    items = sorted(intervals, key=lambda x: x[1])  # sort by end
    ends = [it[1] for it in items]
    n = len(items)
    dp = [0] * (n + 1)  # dp[i]: best weight using the first i (end-sorted) intervals
    for i in range(1, n + 1):
        s, _e, w = items[i - 1]
        # count of earlier intervals whose end <= this start (all compatible with it)
        j = bisect.bisect_right(ends, s, 0, i - 1)
        dp[i] = max(dp[i - 1], dp[j] + w)
    return dp[n]

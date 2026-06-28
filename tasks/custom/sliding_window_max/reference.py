from collections import deque


def max_sliding_window(nums, k):
    if not nums or k <= 0 or k > len(nums):
        return []
    dq = deque()  # holds indices, values decreasing front->back
    out = []
    for i, x in enumerate(nums):
        # drop indices whose value is <= current (they can never be max again)
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        # drop the front if it's outside the window
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

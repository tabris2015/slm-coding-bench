def max_circular_subarray(nums):
    def kadane_max(a):
        best = cur = a[0]
        for x in a[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best

    def kadane_min(a):
        best = cur = a[0]
        for x in a[1:]:
            cur = min(x, cur + x)
            best = min(best, cur)
        return best

    total = sum(nums)
    max_lin = kadane_max(nums)
    if max_lin < 0:  # all elements negative: best is the single largest element
        return max_lin
    return max(max_lin, total - kadane_min(nums))

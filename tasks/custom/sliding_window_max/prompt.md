# Sliding window maximum

Write a function `max_sliding_window(nums, k)` that, given a list of integers
`nums` and an integer window size `k`, returns a list containing the maximum
value of every contiguous window of size `k` as the window slides from the left
of the list to the right.

The returned list has length `len(nums) - k + 1`, where the `i`-th element is
`max(nums[i], nums[i+1], ..., nums[i+k-1])`.

## Edge cases

If `nums` is empty, or `k <= 0`, or `k > len(nums)`, return an empty list `[]`.

## Examples

```
max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
max_sliding_window([4, 2], 1) == [4, 2]
max_sliding_window([9], 1) == [9]
max_sliding_window([1, 2, 3], 5) == []
max_sliding_window([], 3) == []
```

## Notes

- Aim for an efficient solution. A correct algorithm runs in O(n) time overall,
  not O(n*k).

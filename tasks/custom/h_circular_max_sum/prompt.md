# Maximum circular subarray sum

Given a non-empty integer list `nums` arranged in a **circle** (the last element is adjacent to the
first), write `max_circular_subarray(nums)` returning the maximum possible sum of a **non-empty**
contiguous subarray that may wrap around the end back to the beginning. Each element may be used at
most once (a wrapping subarray must not overlap itself).

## Examples

```
max_circular_subarray([1, -2, 3, -2]) == 3
max_circular_subarray([5, -3, 5]) == 10
max_circular_subarray([-3, -2, -3]) == -2
max_circular_subarray([3, -1, 2, -1]) == 4
```

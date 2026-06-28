# Merge overlapping intervals

Write a function `merge_intervals(intervals)` that takes a list of intervals,
where each interval is a two-element list `[start, end]` with `start <= end`,
and returns a new list of non-overlapping intervals that cover exactly the same
set of points. The returned intervals must be sorted in ascending order by their
start value.

Two intervals overlap if they share any point. Intervals that merely touch at an
endpoint (for example `[1, 2]` and `[2, 3]`) are considered overlapping and must
be merged (into `[1, 3]`).

## Edge cases

If `intervals` is empty, return an empty list `[]`. Do not mutate the input.

## Examples

```
merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
merge_intervals([[1, 4], [2, 3]]) == [[1, 4]]
merge_intervals([]) == []
merge_intervals([[5, 7]]) == [[5, 7]]
```

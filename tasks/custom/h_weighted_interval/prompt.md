# Weighted interval scheduling

You are given a list of `intervals`, each `[start, end, weight]` with `start < end` and
`weight >= 0` (all integers). Two intervals are **compatible** iff they do not overlap in more
than a single point — i.e. `[s1, e1]` and `[s2, e2]` are compatible iff `e1 <= s2` or `e2 <= s1`
(touching endpoints is allowed).

Write `max_interval_weight(intervals)` returning the **maximum total weight** of a subset of
pairwise-compatible intervals. Return `0` for an empty list.

## Examples

```
max_interval_weight([[1, 3, 5], [2, 5, 6], [4, 6, 5]]) == 10
max_interval_weight([[1, 2, 1], [2, 3, 1], [3, 4, 1]]) == 3
max_interval_weight([[1, 10, 5], [2, 3, 4], [4, 5, 4]]) == 8
max_interval_weight([]) == 0
```

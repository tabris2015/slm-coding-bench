# Count word-break segmentations

Given a string `s` and a list of dictionary `words` (each non-empty; words may be reused any number
of times), write `count_segmentations(s, words)` returning the **number of distinct ways** to split
`s` into a sequence of dictionary words. The empty string has exactly one segmentation (the empty
sequence).

## Examples

```
count_segmentations("catsanddog", ["cat", "cats", "and", "sand", "dog"]) == 2
count_segmentations("aaa", ["a", "aa"]) == 3
count_segmentations("", ["a"]) == 1
count_segmentations("abc", ["a", "b"]) == 0
```

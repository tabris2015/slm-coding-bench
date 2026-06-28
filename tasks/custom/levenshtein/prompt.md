# Levenshtein edit distance

Write a function `edit_distance(a, b)` that returns the **Levenshtein distance**
between two strings `a` and `b`: the minimum number of single-character edits
required to turn `a` into `b`. The allowed edits are:

- **insertion** of a single character,
- **deletion** of a single character,
- **substitution** of one character for another.

Each edit costs 1.

## Edge cases

- If both strings are empty, the distance is `0`.
- If one string is empty, the distance equals the length of the other string.

## Examples

```
edit_distance("kitten", "sitting") == 3
edit_distance("flaw", "lawn") == 2
edit_distance("", "") == 0
edit_distance("", "abc") == 3
edit_distance("abc", "abc") == 0
```

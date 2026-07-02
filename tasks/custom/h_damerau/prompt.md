# Edit distance with transpositions

Compute the **restricted Damerau–Levenshtein distance** (optimal string alignment) between strings
`a` and `b`: the minimum number of single-character **insertions**, **deletions**,
**substitutions**, and **transpositions of two adjacent characters** (each costing 1) to turn `a`
into `b`. Under the "restricted" (OSA) rule, no substring is edited more than once.

Write `edit_distance_transpose(a, b)` returning that distance as an int.

## Examples

```
edit_distance_transpose("ca", "ac") == 1
edit_distance_transpose("abcd", "abdc") == 1
edit_distance_transpose("kitten", "sitting") == 3
edit_distance_transpose("", "abc") == 3
```

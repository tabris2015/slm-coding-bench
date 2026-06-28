# Valid anagram

Write a function `is_anagram(a, b)` that returns `True` if and only if `a` and
`b` are anagrams of each other — that is, they contain **exactly the same
multiset of characters**.

Comparison is **case-sensitive** and considers **all characters** (including
spaces and punctuation). In particular, `a` and `b` must have the same length to
be anagrams.

## Edge cases

- Two empty strings are anagrams -> `True`.

## Examples

```
is_anagram("listen", "silent") == True
is_anagram("rat", "car") == False
is_anagram("anagram", "nagaram") == True
is_anagram("Tea", "tea") == False   # case-sensitive
is_anagram("", "") == True
```

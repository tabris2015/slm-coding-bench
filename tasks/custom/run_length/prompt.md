# Run-length encoding

Write a function `rle_encode(s)` that run-length encodes the string `s`. Scan the
string left to right; each maximal run of a single character `c` repeated `k`
times is encoded as the character `c` followed immediately by the decimal count
`k`. The count is **always** included, even when `k == 1`.

The concatenation of all encoded runs, in order, is the returned string.

## Edge cases

If `s` is empty, return the empty string `""`.

## Examples

```
rle_encode("aaabbc") == "a3b2c1"
rle_encode("abc")    == "a1b1c1"
rle_encode("aaaa")   == "a4"
rle_encode("")       == ""
rle_encode("aab")    == "a2b1"
```

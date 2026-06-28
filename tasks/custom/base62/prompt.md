# Base62 encode

Write a function `base62_encode(n)` that encodes a non-negative integer `n` into
its base-62 string representation, most-significant digit first.

The 62-character alphabet, in order of increasing digit value, is:

```
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

That is: digit values `0`–`9` map to characters `'0'`–`'9'`, values `10`–`35`
map to `'A'`–`'Z'`, and values `36`–`61` map to `'a'`–`'z'`.

## Edge cases

- `base62_encode(0)` must return `"0"` (not the empty string).
- The result must never have a leading zero except for the single-character
  result `"0"` itself.

## Examples

```
base62_encode(0)    == "0"
base62_encode(1)    == "1"
base62_encode(61)   == "z"
base62_encode(62)   == "10"
base62_encode(3843) == "zz"
base62_encode(3844) == "100"
```

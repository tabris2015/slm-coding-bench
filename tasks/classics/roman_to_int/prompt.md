# Roman numeral to integer

Write a function `roman_to_int(s)` that converts a valid Roman numeral string `s`
into its integer value.

The seven symbols and their values are:

```
I = 1     V = 5     X = 10    L = 50
C = 100   D = 500   M = 1000
```

Roman numerals are usually written largest to smallest from left to right, but
**subtractive notation** is used for six cases, where a smaller symbol placed
before a larger one is subtracted:

- `IV` = 4, `IX` = 9
- `XL` = 40, `XC` = 90
- `CD` = 400, `CM` = 900

You may assume `s` is a valid Roman numeral.

## Examples

```
roman_to_int("III") == 3
roman_to_int("IV") == 4
roman_to_int("IX") == 9
roman_to_int("LVIII") == 58
roman_to_int("MCMXCIV") == 1994
```

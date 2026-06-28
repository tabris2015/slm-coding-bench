# FizzBuzz

Write a function `fizzbuzz(n)` that returns a list of strings for the integers
from `1` to `n` (inclusive). For each integer `i`:

- if `i` is divisible by both 3 and 5, the entry is `"FizzBuzz"`,
- else if `i` is divisible by 3, the entry is `"Fizz"`,
- else if `i` is divisible by 5, the entry is `"Buzz"`,
- otherwise the entry is the decimal string of `i`, e.g. `str(i)`.

The returned list has length `n`.

## Edge cases

- `fizzbuzz(0)` returns the empty list `[]`.

## Examples

```
fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
fizzbuzz(15)[-1] == "FizzBuzz"
fizzbuzz(0) == []
fizzbuzz(1) == ["1"]
```

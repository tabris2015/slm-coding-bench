# Valid palindrome

Write a function `is_palindrome(s)` that returns `True` if `s` reads the same
forwards and backwards, considering **only alphanumeric characters** and
**ignoring case**. All other characters (spaces, punctuation, etc.) are ignored.

## Edge cases

- The empty string `""` is a palindrome -> `True`.
- A string with no alphanumeric characters (e.g. `",.!"`) is a palindrome -> `True`.

## Examples

```
is_palindrome("A man, a plan, a canal: Panama") == True
is_palindrome("race a car") == False
is_palindrome("") == True
is_palindrome("0P") == False
```

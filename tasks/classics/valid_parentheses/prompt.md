# Valid parentheses

Write a function `valid_parentheses(s)` that returns `True` if the string `s`,
containing only the characters `()[]{}`, is **balanced and correctly nested**.

A string is valid when:

- every opening bracket is closed by a matching closing bracket of the same type, and
- brackets are closed in the correct order.

## Edge cases

- The empty string `""` is valid -> `True`.

## Examples

```
valid_parentheses("()") == True
valid_parentheses("()[]{}") == True
valid_parentheses("(]") == False
valid_parentheses("([)]") == False
valid_parentheses("{[]}") == True
valid_parentheses("") == True
valid_parentheses("(") == False
```

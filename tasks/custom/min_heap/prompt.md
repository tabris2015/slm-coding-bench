# Min heap

Implement a class `MinHeap`, a binary min-heap of integers.

## Interface

- `MinHeap()` — construct an empty heap.
- `push(x)` — add the integer `x` to the heap. Returns `None`.
- `pop()` — remove and return the smallest element in the heap.
- `peek()` — return the smallest element without removing it.
- `__len__()` — return the number of elements currently in the heap (so that
  `len(heap)` works).

## Behavior details

- `pop` always returns the current minimum and removes exactly that one element.
- `peek` returns the current minimum but leaves the heap unchanged.
- Calling `pop` or `peek` on an empty heap raises `IndexError`.

## Example

```
h = MinHeap()
h.push(5)
h.push(1)
h.push(3)
len(h)      # -> 3
h.peek()    # -> 1
h.pop()     # -> 1
h.pop()     # -> 3
h.peek()    # -> 5
len(h)      # -> 1
```

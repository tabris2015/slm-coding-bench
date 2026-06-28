# LRU cache

Implement a class `LRUCache` that behaves as a least-recently-used cache with a
fixed positive capacity.

## Interface

- `LRUCache(capacity)` — construct a cache that holds at most `capacity` entries.
  `capacity` is a positive integer.
- `get(key)` — return the value associated with `key`, or `-1` if the key is not
  present. Accessing a key with `get` counts as using it (it becomes the most
  recently used entry).
- `put(key, value)` — insert or update the value for `key`. This counts as using
  the key (it becomes the most recently used entry). If inserting a new key would
  exceed the capacity, evict the least-recently-used entry first.

## Behavior details

- Both `get` (when the key exists) and `put` mark the key as most recently used.
- When the cache is full and a brand-new key is inserted, exactly one entry — the
  least recently used — is removed to make room.
- Updating the value of an existing key never triggers an eviction; it just
  refreshes the value and the recency.

## Example

```
c = LRUCache(2)
c.put(1, 1)
c.put(2, 2)
c.get(1)      # -> 1  (1 is now most recently used)
c.put(3, 3)   # evicts key 2 (least recently used)
c.get(2)      # -> -1
c.put(4, 4)   # evicts key 1
c.get(1)      # -> -1
c.get(3)      # -> 3
c.get(4)      # -> 4
```

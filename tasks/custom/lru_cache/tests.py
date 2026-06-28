from solution import LRUCache


def test_basic_sequence():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)  # evicts key 2
    assert c.get(2) == -1
    c.put(4, 4)  # evicts key 1
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4


def test_missing_returns_minus_one():
    c = LRUCache(1)
    assert c.get(99) == -1


def test_update_existing_no_eviction():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 10)  # update, not insert -> no eviction
    assert c.get(1) == 10
    assert c.get(2) == 2


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1  # 1 now MRU, 2 is LRU
    c.put(3, 3)  # evicts 2
    assert c.get(2) == -1
    assert c.get(1) == 1


def test_capacity_one():
    c = LRUCache(1)
    c.put(1, 1)
    assert c.get(1) == 1
    c.put(2, 2)  # evicts 1
    assert c.get(1) == -1
    assert c.get(2) == 2


def test_put_returns_none():
    c = LRUCache(2)
    assert c.put(1, 1) is None

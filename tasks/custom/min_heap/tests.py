from solution import MinHeap


def test_basic_order():
    h = MinHeap()
    for x in [5, 1, 3]:
        h.push(x)
    assert len(h) == 3
    assert h.peek() == 1
    assert h.pop() == 1
    assert h.pop() == 3
    assert h.peek() == 5
    assert len(h) == 1


def test_single_element():
    h = MinHeap()
    h.push(42)
    assert h.peek() == 42
    assert h.pop() == 42
    assert len(h) == 0


def test_duplicates():
    h = MinHeap()
    for x in [2, 2, 1, 1, 3]:
        h.push(x)
    assert [h.pop() for _ in range(5)] == [1, 1, 2, 2, 3]


def test_negatives_and_sorted_output():
    h = MinHeap()
    data = [4, -2, 7, 0, -5, 3]
    for x in data:
        h.push(x)
    out = [h.pop() for _ in range(len(data))]
    assert out == sorted(data)


def test_len_tracks_size():
    h = MinHeap()
    assert len(h) == 0
    h.push(1)
    h.push(2)
    assert len(h) == 2
    h.pop()
    assert len(h) == 1


def test_push_returns_none():
    h = MinHeap()
    assert h.push(1) is None


def test_empty_pop_raises():
    h = MinHeap()
    try:
        h.pop()
    except IndexError:
        pass
    else:
        assert False, "pop on empty heap should raise IndexError"


def test_empty_peek_raises():
    h = MinHeap()
    try:
        h.peek()
    except IndexError:
        pass
    else:
        assert False, "peek on empty heap should raise IndexError"

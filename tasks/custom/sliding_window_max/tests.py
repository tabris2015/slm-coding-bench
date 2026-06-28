from solution import max_sliding_window


def test_basic():
    assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]


def test_window_one():
    assert max_sliding_window([4, 2, 7, 1], 1) == [4, 2, 7, 1]


def test_full_window():
    assert max_sliding_window([2, 5, 1, 8, 3], 5) == [8]


def test_single_element():
    assert max_sliding_window([9], 1) == [9]


def test_duplicates():
    assert max_sliding_window([5, 5, 5, 5], 2) == [5, 5, 5]


def test_empty_nums():
    assert max_sliding_window([], 3) == []


def test_k_too_large():
    assert max_sliding_window([1, 2, 3], 5) == []


def test_k_zero_or_negative():
    assert max_sliding_window([1, 2, 3], 0) == []
    assert max_sliding_window([1, 2, 3], -1) == []


def test_negatives():
    assert max_sliding_window([-7, -8, -1, -3], 2) == [-7, -1, -1]

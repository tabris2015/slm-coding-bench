from solution import merge_intervals


def test_basic():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_touching_merges():
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_contained():
    assert merge_intervals([[1, 4], [2, 3]]) == [[1, 4]]


def test_empty():
    assert merge_intervals([]) == []


def test_single():
    assert merge_intervals([[5, 7]]) == [[5, 7]]


def test_unsorted_input():
    assert merge_intervals([[8, 10], [1, 3], [2, 6], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_no_overlap():
    assert merge_intervals([[1, 2], [4, 5], [7, 8]]) == [[1, 2], [4, 5], [7, 8]]


def test_all_merge_into_one():
    assert merge_intervals([[1, 5], [2, 6], [3, 7], [0, 1]]) == [[0, 7]]


def test_zero_length_intervals():
    assert merge_intervals([[3, 3], [3, 3], [1, 1]]) == [[1, 1], [3, 3]]


def test_input_not_mutated():
    data = [[1, 3], [2, 6]]
    snapshot = [list(iv) for iv in data]
    merge_intervals(data)
    assert data == snapshot

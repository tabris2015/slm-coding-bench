from solution import max_interval_weight


def test_pick_two_short():
    assert max_interval_weight([[1, 3, 5], [2, 5, 6], [4, 6, 5]]) == 10


def test_touching_allowed():
    assert max_interval_weight([[1, 2, 1], [2, 3, 1], [3, 4, 1]]) == 3


def test_skip_long():
    assert max_interval_weight([[1, 10, 5], [2, 3, 4], [4, 5, 4]]) == 8


def test_empty():
    assert max_interval_weight([]) == 0


def test_single():
    assert max_interval_weight([[0, 5, 7]]) == 7


def test_prefer_one_heavy():
    assert max_interval_weight([[0, 10, 100], [1, 2, 1], [3, 4, 1]]) == 100

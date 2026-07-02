from solution import max_circular_subarray


def test_no_wrap():
    assert max_circular_subarray([1, -2, 3, -2]) == 3


def test_wrap():
    assert max_circular_subarray([5, -3, 5]) == 10


def test_all_negative():
    assert max_circular_subarray([-3, -2, -3]) == -2


def test_mixed():
    assert max_circular_subarray([3, -1, 2, -1]) == 4


def test_known_example():
    assert max_circular_subarray([-2, 4, -5, 4, -5, 9, 4]) == 15


def test_single():
    assert max_circular_subarray([5]) == 5

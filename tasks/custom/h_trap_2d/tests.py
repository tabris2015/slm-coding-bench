from solution import trap_water_2d


def test_small_hole():
    assert trap_water_2d([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) == 1


def test_deep_hole():
    assert trap_water_2d([[9, 9, 9], [9, 0, 9], [9, 9, 9]]) == 9


def test_two_holes():
    assert trap_water_2d([[3, 3, 3, 3], [3, 0, 0, 3], [3, 3, 3, 3]]) == 6


def test_too_small():
    assert trap_water_2d([[1, 2], [3, 4]]) == 0


def test_lc_example():
    assert trap_water_2d([[1, 4, 3, 1, 3, 2], [3, 2, 1, 3, 2, 4], [2, 3, 3, 2, 3, 1]]) == 4


def test_flat():
    assert trap_water_2d([[5, 5, 5], [5, 5, 5], [5, 5, 5]]) == 0

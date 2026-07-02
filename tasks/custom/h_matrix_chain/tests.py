from solution import min_matrix_mult


def test_two_matrices():
    assert min_matrix_mult([10, 20, 30]) == 6000


def test_three_matrices():
    assert min_matrix_mult([10, 20, 30, 40]) == 18000


def test_symmetric_triple():
    assert min_matrix_mult([2, 3, 2]) == 12


def test_single_matrix():
    assert min_matrix_mult([5, 10]) == 0


def test_zero_matrices():
    assert min_matrix_mult([5]) == 0

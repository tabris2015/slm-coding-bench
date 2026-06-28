from solution import gcd


def test_common_factor():
    assert gcd(12, 8) == 4


def test_coprime():
    assert gcd(17, 5) == 1


def test_both_zero():
    assert gcd(0, 0) == 0


def test_one_zero():
    assert gcd(0, 7) == 7
    assert gcd(7, 0) == 7


def test_divisible():
    assert gcd(100, 10) == 10


def test_equal():
    assert gcd(9, 9) == 9


def test_order_independent():
    assert gcd(8, 12) == gcd(12, 8)

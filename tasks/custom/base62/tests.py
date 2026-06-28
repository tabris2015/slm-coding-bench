from solution import base62_encode


def test_zero():
    assert base62_encode(0) == "0"


def test_single_digits():
    assert base62_encode(1) == "1"
    assert base62_encode(9) == "9"


def test_letter_boundaries():
    assert base62_encode(10) == "A"
    assert base62_encode(35) == "Z"
    assert base62_encode(36) == "a"
    assert base62_encode(61) == "z"


def test_two_digit_rollover():
    assert base62_encode(62) == "10"
    assert base62_encode(63) == "11"


def test_three_digit():
    assert base62_encode(3843) == "zz"
    assert base62_encode(3844) == "100"


def test_large_value():
    n = 10**18
    s = base62_encode(n)
    # decode back to verify round-trip
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    val = 0
    for ch in s:
        val = val * 62 + alphabet.index(ch)
    assert val == n


def test_no_leading_zero():
    assert not base62_encode(62).startswith("0")

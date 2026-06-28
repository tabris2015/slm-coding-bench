from solution import roman_to_int


def test_simple_additive():
    assert roman_to_int("III") == 3


def test_subtractive_four():
    assert roman_to_int("IV") == 4


def test_subtractive_nine():
    assert roman_to_int("IX") == 9


def test_fifty_eight():
    assert roman_to_int("LVIII") == 58


def test_complex():
    assert roman_to_int("MCMXCIV") == 1994


def test_single_symbol():
    assert roman_to_int("M") == 1000


def test_forty_and_ninety():
    assert roman_to_int("XL") == 40
    assert roman_to_int("XC") == 90

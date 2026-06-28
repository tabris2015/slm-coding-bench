from solution import rle_encode


def test_basic():
    assert rle_encode("aaabbc") == "a3b2c1"


def test_all_singles():
    assert rle_encode("abc") == "a1b1c1"


def test_single_run():
    assert rle_encode("aaaa") == "a4"


def test_empty():
    assert rle_encode("") == ""


def test_count_always_present():
    assert rle_encode("aab") == "a2b1"


def test_single_char():
    assert rle_encode("z") == "z1"


def test_alternating():
    assert rle_encode("ababab") == "a1b1a1b1a1b1"


def test_long_run_multi_digit():
    assert rle_encode("a" * 12 + "b" * 3) == "a12b3"


def test_runs_of_digit_chars():
    # digit characters in the input are encoded like any other character:
    # "1"x2 -> "12", "2"x2 -> "22", "3"x3 -> "33"
    assert rle_encode("1122333") == "122233"

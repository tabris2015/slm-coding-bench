from solution import edit_distance_transpose


def test_transpose_pair():
    assert edit_distance_transpose("ca", "ac") == 1


def test_transpose_last_two():
    assert edit_distance_transpose("abcd", "abdc") == 1


def test_kitten_sitting():
    assert edit_distance_transpose("kitten", "sitting") == 3


def test_empty_a():
    assert edit_distance_transpose("", "abc") == 3


def test_empty_b():
    assert edit_distance_transpose("abc", "") == 3


def test_equal():
    assert edit_distance_transpose("hello", "hello") == 0


def test_swap():
    assert edit_distance_transpose("ab", "ba") == 1

from solution import edit_distance


def test_classic_kitten():
    assert edit_distance("kitten", "sitting") == 3


def test_flaw_lawn():
    assert edit_distance("flaw", "lawn") == 2


def test_both_empty():
    assert edit_distance("", "") == 0


def test_one_empty():
    assert edit_distance("", "abc") == 3
    assert edit_distance("abc", "") == 3


def test_identical():
    assert edit_distance("abc", "abc") == 0


def test_single_substitution():
    assert edit_distance("a", "b") == 1


def test_symmetry():
    assert edit_distance("sunday", "saturday") == edit_distance("saturday", "sunday")


def test_known_value():
    assert edit_distance("sunday", "saturday") == 3

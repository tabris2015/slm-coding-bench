from solution import count_segmentations


def test_cats():
    assert count_segmentations("catsanddog", ["cat", "cats", "and", "sand", "dog"]) == 2


def test_aaa():
    assert count_segmentations("aaa", ["a", "aa"]) == 3


def test_empty_string():
    assert count_segmentations("", ["a"]) == 1


def test_unsegmentable():
    assert count_segmentations("abc", ["a", "b"]) == 0


def test_ababa():
    assert count_segmentations("ababa", ["a", "b", "ab", "ba"]) == 8


def test_no_words():
    assert count_segmentations("a", []) == 0

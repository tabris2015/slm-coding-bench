from solution import is_anagram


def test_basic_anagram():
    assert is_anagram("listen", "silent") is True


def test_not_anagram():
    assert is_anagram("rat", "car") is False


def test_anagram_words():
    assert is_anagram("anagram", "nagaram") is True


def test_case_sensitive():
    assert is_anagram("Tea", "tea") is False


def test_both_empty():
    assert is_anagram("", "") is True


def test_different_length():
    assert is_anagram("abc", "ab") is False


def test_spaces_count():
    assert is_anagram("a b", "ab ") is True
    assert is_anagram("ab", "a b") is False

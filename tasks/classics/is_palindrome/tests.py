from solution import is_palindrome


def test_classic_panama():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_not_palindrome():
    assert is_palindrome("race a car") is False


def test_empty():
    assert is_palindrome("") is True


def test_only_punctuation():
    assert is_palindrome(",.!?") is True


def test_alphanumeric_mismatch():
    assert is_palindrome("0P") is False


def test_digits_palindrome():
    assert is_palindrome("12321") is True


def test_mixed_case_single_word():
    assert is_palindrome("Madam") is True

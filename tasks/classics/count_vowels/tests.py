from solution import count_vowels


def test_basic():
    assert count_vowels("hello") == 2


def test_uppercase():
    assert count_vowels("HELLO") == 2


def test_no_vowels():
    assert count_vowels("xyz") == 0


def test_all_vowels_both_cases():
    assert count_vowels("AEIOUaeiou") == 10


def test_empty():
    assert count_vowels("") == 0


def test_y_not_vowel():
    assert count_vowels("rhythm") == 0


def test_with_spaces_and_punctuation():
    assert count_vowels("a e i o u!") == 5

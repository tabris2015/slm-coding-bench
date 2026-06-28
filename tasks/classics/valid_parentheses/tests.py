from solution import valid_parentheses


def test_simple_pair():
    assert valid_parentheses("()") is True


def test_all_types():
    assert valid_parentheses("()[]{}") is True


def test_mismatched():
    assert valid_parentheses("(]") is False


def test_wrong_order():
    assert valid_parentheses("([)]") is False


def test_nested():
    assert valid_parentheses("{[]}") is True


def test_empty():
    assert valid_parentheses("") is True


def test_unclosed():
    assert valid_parentheses("(") is False


def test_extra_close():
    assert valid_parentheses("())") is False

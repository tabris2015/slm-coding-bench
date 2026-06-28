"""Tests for code extraction from chatty / reasoning model output."""

from __future__ import annotations

from slm_coding_bench.extract import extract_code


def test_simple_python_fence():
    text = "Here you go:\n```python\ndef add(a, b):\n    return a + b\n```\nHope that helps!"
    code, ok = extract_code(text, "add")
    assert ok
    assert "def add" in code
    assert "Hope that helps" not in code


def test_prefers_block_defining_entrypoint():
    text = (
        "First a helper:\n```python\ndef helper():\n    return 1\n```\n"
        "Now the answer:\n```python\ndef solve(x):\n    return x * 2\n```\n"
    )
    code, ok = extract_code(text, "solve")
    assert ok and "def solve" in code


def test_strips_think_block():
    text = (
        "<think>I should add the numbers. Let me reconsider... yes add.</think>\n"
        "```python\ndef add(a, b):\n    return a + b\n```"
    )
    code, ok = extract_code(text, "add")
    assert ok
    assert "reconsider" not in code
    assert "def add" in code


def test_untagged_fence():
    text = "```\ndef f():\n    return 42\n```"
    code, ok = extract_code(text, "f")
    assert ok and "def f" in code


def test_no_fence_whole_text_parses():
    text = "def g(n):\n    return n + 1\n"
    code, ok = extract_code(text, "g")
    assert ok and "def g" in code


def test_unparseable_returns_not_ok():
    text = "I cannot solve this problem."
    code, ok = extract_code(text, "h")
    assert not ok


def test_suffix_recovery_after_prose():
    text = "Sure, here's the code without fences:\nimport math\n\ndef area(r):\n    return math.pi * r * r\n"
    code, ok = extract_code(text, "area")
    assert ok and "def area" in code

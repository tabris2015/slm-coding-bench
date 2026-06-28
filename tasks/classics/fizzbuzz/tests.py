from solution import fizzbuzz


def test_first_five():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_fizzbuzz_at_fifteen():
    assert fizzbuzz(15)[-1] == "FizzBuzz"


def test_zero():
    assert fizzbuzz(0) == []


def test_one():
    assert fizzbuzz(1) == ["1"]


def test_length():
    assert len(fizzbuzz(100)) == 100


def test_full_first_fifteen():
    assert fizzbuzz(15) == [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8",
        "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz",
    ]

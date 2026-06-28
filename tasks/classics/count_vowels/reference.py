def count_vowels(s):
    vowels = set("aeiou")
    return sum(1 for c in s.lower() if c in vowels)

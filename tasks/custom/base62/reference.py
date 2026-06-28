_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_encode(n):
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        n, rem = divmod(n, 62)
        digits.append(_ALPHABET[rem])
    return "".join(reversed(digits))

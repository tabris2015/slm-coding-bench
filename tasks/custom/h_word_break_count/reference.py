def count_segmentations(s, words):
    wordset = set(words)
    if not wordset:
        return 1 if s == "" else 0
    maxlen = max(len(w) for w in wordset)
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for length in range(1, min(maxlen, i) + 1):
            if s[i - length:i] in wordset:
                dp[i] += dp[i - length]
    return dp[n]

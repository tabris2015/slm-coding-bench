import math


def min_matrix_mult(dims):
    m = len(dims) - 1  # number of matrices
    if m <= 1:
        return 0
    dp = [[0] * (m + 1) for _ in range(m + 1)]  # 1-indexed over matrices
    for length in range(2, m + 1):
        for i in range(1, m - length + 2):
            j = i + length - 1
            best = math.inf
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if cost < best:
                    best = cost
            dp[i][j] = best
    return dp[1][m]

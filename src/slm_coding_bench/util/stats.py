"""Small statistical helpers used across the harness."""

from __future__ import annotations

import math
from collections.abc import Sequence


def percentile(values: Sequence[float], q: float) -> float | None:
    """Linear-interpolation percentile (q in [0, 100]). Returns None for empty input."""
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    rank = (q / 100.0) * (len(xs) - 1)
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return xs[lo]
    frac = rank - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def geomean(values: Sequence[float]) -> float | None:
    """Geometric mean of positive values. Returns None for empty input."""
    xs = [v for v in values if v is not None and v > 0]
    if not xs:
        return None
    return math.exp(sum(math.log(v) for v in xs) / len(xs))


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator of pass@k given ``n`` samples with ``c`` correct (Chen et al. 2021).

    pass@k = 1 - C(n-c, k) / C(n, k).
    """
    if k <= 0 or n <= 0:
        return 0.0
    if c <= 0:
        return 0.0
    if n - c < k:
        return 1.0
    # Numerically stable product form.
    prob_all_fail = 1.0
    for i in range(k):
        prob_all_fail *= (n - c - i) / (n - i)
    return 1.0 - prob_all_fail

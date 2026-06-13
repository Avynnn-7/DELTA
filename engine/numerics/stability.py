from __future__ import annotations

import numpy as np

_LOG2 = float(np.log(2.0))


def log1mexp(x):
    x = np.asarray(x, dtype=float)
    if np.any(x > 0.0):
        raise ValueError("log1mexp requires x <= 0")
    return np.where(x < -_LOG2, np.log1p(-np.exp(x)), np.log(-np.expm1(x)))

from __future__ import annotations

import numpy as np

from engine.conventions.returns import annualize_variance, annualize_volatility


def realized_variance(returns):
    r = np.asarray(returns, dtype=float)
    return float(np.sum(r**2))


def sample_variance(returns):
    r = np.asarray(returns, dtype=float)
    n = r.shape[0]
    if n < 2:
        raise ValueError("sample_variance requires at least two returns")
    deviations = r - r.mean()
    return float(np.sum(deviations**2) / (n - 1))


def annualized_variance(returns, periods_per_year):
    return float(annualize_variance(sample_variance(returns), periods_per_year))


def annualized_volatility(returns, periods_per_year):
    return float(annualize_volatility(np.sqrt(sample_variance(returns)), periods_per_year))

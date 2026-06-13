from __future__ import annotations

import numpy as np

from .constants import PERIODS_PER_YEAR


def log_return(price_next, price_prev):
    return np.log(np.asarray(price_next, dtype=float) / np.asarray(price_prev, dtype=float))


def periods_per_year(frequency: str) -> int:
    try:
        return PERIODS_PER_YEAR[frequency]
    except KeyError as exc:
        raise ValueError(f"unknown sampling frequency: {frequency!r}") from exc


def annualize_variance(variance_period, n_per_year):
    return np.asarray(variance_period, dtype=float) * float(n_per_year)


def annualize_volatility(sigma_period, n_per_year):
    return np.asarray(sigma_period, dtype=float) * np.sqrt(float(n_per_year))

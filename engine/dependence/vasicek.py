from __future__ import annotations

import numpy as np

from engine.numerics import normal


def conditional_default_probability(pd, rho, z):
    threshold = normal.ppf(pd)
    return normal.cdf((threshold - np.sqrt(rho) * np.asarray(z, dtype=float)) / np.sqrt(1.0 - rho))


def loss_cdf(x, pd, rho):
    x = np.asarray(x, dtype=float)
    threshold = normal.ppf(pd)
    return normal.cdf((np.sqrt(1.0 - rho) * normal.ppf(x) - threshold) / np.sqrt(rho))


def loss_quantile(level, pd, rho):
    threshold = normal.ppf(pd)
    return normal.cdf((threshold + np.sqrt(rho) * normal.ppf(level)) / np.sqrt(1.0 - rho))

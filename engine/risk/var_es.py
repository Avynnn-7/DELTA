from __future__ import annotations

import numpy as np


def value_at_risk(losses, alpha):
    losses = np.asarray(losses, dtype=float)
    return float(np.quantile(losses, alpha, method="inverted_cdf"))


def expected_shortfall_integral(losses, alpha, nodes=1024):
    losses = np.asarray(losses, dtype=float)
    levels = alpha + (1.0 - alpha) * (np.arange(nodes) + 0.5) / nodes
    quantiles = np.quantile(losses, levels, method="inverted_cdf")
    return float(quantiles.mean())


def expected_shortfall_conditional(losses, alpha):
    losses = np.asarray(losses, dtype=float)
    var = value_at_risk(losses, alpha)
    tail = losses[losses >= var]
    if tail.size == 0:
        return var
    return float(tail.mean())


def spectral_risk(losses, spectrum, nodes=1024):
    losses = np.asarray(losses, dtype=float)
    levels = (np.arange(nodes) + 0.5) / nodes
    quantiles = np.quantile(losses, levels, method="inverted_cdf")
    weights = np.asarray(spectrum(levels), dtype=float)
    return float(np.mean(weights * quantiles))


def expected_shortfall_spectrum(alpha):
    def spectrum(u):
        u = np.asarray(u, dtype=float)
        return np.where(u >= alpha, 1.0 / (1.0 - alpha), 0.0)

    return spectrum

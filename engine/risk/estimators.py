from __future__ import annotations

import numpy as np

from engine.numerics import normal


def _kernel_density(losses, point, bandwidth):
    losses = np.asarray(losses, dtype=float)
    n = losses.shape[0]
    if bandwidth is None:
        bandwidth = 1.06 * np.std(losses, ddof=1) * n ** (-0.2)
    if bandwidth <= 0.0:
        return np.inf
    z = (point - losses) / bandwidth
    return float(np.mean(np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi)) / bandwidth)


def var_estimator(losses, alpha):
    losses = np.asarray(losses, dtype=float)
    ordered = np.sort(losses)
    n = ordered.shape[0]
    index = int(np.ceil(alpha * n))
    index = min(max(index, 1), n)
    return float(ordered[index - 1])


def es_estimator(losses, alpha):
    losses = np.asarray(losses, dtype=float)
    ordered = np.sort(losses)
    n = ordered.shape[0]
    cutoff = int(np.ceil(alpha * n))
    tail = ordered[cutoff:]
    if tail.size == 0:
        return float(ordered[-1])
    return float(tail.mean())


def var_standard_error(losses, alpha, bandwidth=None):
    losses = np.asarray(losses, dtype=float)
    n = losses.shape[0]
    var = var_estimator(losses, alpha)
    density = _kernel_density(losses, var, bandwidth)
    if not np.isfinite(density) or density == 0.0:
        return np.inf
    return float(np.sqrt(alpha * (1.0 - alpha) / n) / density)


def es_standard_error(losses, alpha):
    losses = np.asarray(losses, dtype=float)
    n = losses.shape[0]
    var = var_estimator(losses, alpha)
    tail = losses[losses >= var]
    if tail.size <= 1:
        return np.inf
    tail_variance = np.var(tail, ddof=1)
    return float(np.sqrt(tail_variance / tail.size))


def weighted_var_estimator(losses, weights, alpha):
    losses = np.asarray(losses, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(losses)
    ordered_losses = losses[order]
    ordered_weights = weights[order]
    cumulative = np.cumsum(ordered_weights) / np.sum(ordered_weights)
    index = int(np.searchsorted(cumulative, alpha, side="left"))
    index = min(index, ordered_losses.shape[0] - 1)
    return float(ordered_losses[index])


def weighted_es_estimator(losses, weights, alpha):
    losses = np.asarray(losses, dtype=float)
    weights = np.asarray(weights, dtype=float)
    var = weighted_var_estimator(losses, weights, alpha)
    mask = losses >= var
    tail_weight = weights[mask]
    if tail_weight.sum() == 0.0:
        return var
    return float(np.sum(losses[mask] * tail_weight) / tail_weight.sum())


def asymptotic_normal_quantile(level):
    return float(normal.ppf(level))

from __future__ import annotations

import numpy as np

from engine.numerics import rng


def log_return_mean(mu, sigma, t):
    return (mu - 0.5 * sigma**2) * t


def log_return_variance(sigma, t):
    return sigma**2 * t


def expected_price(p0, mu, t):
    return p0 * np.exp(mu * t)


def price_variance(p0, mu, sigma, t):
    return p0**2 * np.exp(2.0 * mu * t) * np.expm1(sigma**2 * t)


def sample_terminal(p0, mu, sigma, t, generator, size=None):
    z = rng.standard_normal(generator, size=size)
    return p0 * np.exp((mu - 0.5 * sigma**2) * t + sigma * np.sqrt(t) * z)


def sample_path(p0, mu, sigma, times, generator, paths=1):
    times = np.asarray(times, dtype=float)
    if np.any(np.diff(times) <= 0.0) or times[0] <= 0.0:
        raise ValueError("times must be strictly increasing and positive")
    dt = np.diff(np.concatenate(([0.0], times)))
    z = rng.standard_normal(generator, size=(paths, dt.shape[0]))
    increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    return np.exp(np.log(p0) + np.cumsum(increments, axis=1))


def short_horizon_drift(reference_rate=0.0):
    return reference_rate

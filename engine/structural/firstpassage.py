from __future__ import annotations

import numpy as np

from engine.numerics import normal


def barrier(health):
    return -np.log(np.asarray(health, dtype=float))


def first_passage_cdf(health, drift, sigma, horizon):
    horizon = np.asarray(horizon, dtype=float)
    b = barrier(health)
    m = drift - 0.5 * sigma**2
    root = sigma * np.sqrt(horizon)
    terminal = normal.cdf((b - m * horizon) / root)
    log_reflection = 2.0 * m * b / sigma**2 + normal.log_cdf((b + m * horizon) / root)
    return terminal + np.exp(log_reflection)


def terminal_cdf(health, drift, sigma, horizon):
    horizon = np.asarray(horizon, dtype=float)
    b = barrier(health)
    m = drift - 0.5 * sigma**2
    return normal.cdf((b - m * horizon) / (sigma * np.sqrt(horizon)))


def first_passage_density(health, drift, sigma, t):
    t = np.asarray(t, dtype=float)
    b = barrier(health)
    m = drift - 0.5 * sigma**2
    coefficient = np.abs(b) / (sigma * np.sqrt(2.0 * np.pi * t**3))
    return coefficient * np.exp(-((b - m * t) ** 2) / (2.0 * sigma**2 * t))


def defect_mass(health, drift, sigma):
    b = barrier(health)
    m = drift - 0.5 * sigma**2
    return np.where(m > 0.0, np.exp(2.0 * m * b / sigma**2), 1.0)

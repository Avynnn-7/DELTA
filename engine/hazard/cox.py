from __future__ import annotations

import numpy as np

from engine.numerics import rng


def cox_survival(cumulative_hazard_paths):
    paths = np.asarray(cumulative_hazard_paths, dtype=float)
    return np.exp(-paths).mean(axis=0)


def exponential_thresholds(generator, size):
    u = rng.uniform_open(generator, size=size)
    return -np.log(u)


def default_time(times, cumulative_hazard, threshold):
    times = np.asarray(times, dtype=float)
    cumulative_hazard = np.asarray(cumulative_hazard, dtype=float)
    if np.any(np.diff(cumulative_hazard) < 0.0):
        raise ValueError("cumulative hazard must be non-decreasing")
    if threshold > cumulative_hazard[-1]:
        return np.inf
    index = int(np.searchsorted(cumulative_hazard, threshold, side="left"))
    if index == 0:
        lambda_0 = cumulative_hazard[0] / times[0] if times[0] > 0.0 else np.inf
        return threshold / lambda_0 if np.isfinite(lambda_0) else 0.0
    lower_h = cumulative_hazard[index - 1]
    upper_h = cumulative_hazard[index]
    lower_t = times[index - 1]
    upper_t = times[index]
    if upper_h == lower_h:
        return upper_t
    fraction = (threshold - lower_h) / (upper_h - lower_h)
    return lower_t + fraction * (upper_t - lower_t)


def sample_default_times(generator, times, cumulative_hazard, size):
    thresholds = exponential_thresholds(generator, size)
    return np.array([default_time(times, cumulative_hazard, e) for e in thresholds])

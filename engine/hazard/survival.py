from __future__ import annotations

import numpy as np


def survival_from_cumulative_hazard(cumulative_hazard):
    return np.exp(-np.asarray(cumulative_hazard, dtype=float))


def default_probability(cumulative_hazard):
    return -np.expm1(-np.asarray(cumulative_hazard, dtype=float))


def constant_survival(intensity, t):
    return np.exp(-intensity * np.asarray(t, dtype=float))


def constant_mean_time(intensity):
    return 1.0 / intensity


def piecewise_cumulative_hazard(intensities, durations):
    intensities = np.asarray(intensities, dtype=float)
    durations = np.asarray(durations, dtype=float)
    if intensities.shape != durations.shape:
        raise ValueError("intensities and durations must have equal length")
    return np.cumsum(intensities * durations)


def piecewise_survival(intensities, durations):
    return np.exp(-piecewise_cumulative_hazard(intensities, durations))


def bootstrap_intensities(survival_targets, durations):
    survival_targets = np.asarray(survival_targets, dtype=float)
    durations = np.asarray(durations, dtype=float)
    if survival_targets.shape != durations.shape:
        raise ValueError("survival_targets and durations must have equal length")
    if np.any(np.diff(survival_targets) > 0.0):
        raise ValueError("survival targets must be non-increasing")
    log_survival = np.log(survival_targets)
    increments = -np.diff(np.concatenate(([0.0], log_survival)))
    return increments / durations

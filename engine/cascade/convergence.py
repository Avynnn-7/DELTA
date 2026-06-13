from __future__ import annotations

import numpy as np

from engine.numerics import normal


def mean_estimate(samples):
    return float(np.mean(samples))


def sample_variance(samples):
    return float(np.var(samples, ddof=1))


def standard_error(samples):
    samples = np.asarray(samples, dtype=float)
    return float(np.std(samples, ddof=1) / np.sqrt(samples.shape[0]))


def confidence_interval(samples, level=0.95):
    samples = np.asarray(samples, dtype=float)
    mean = float(np.mean(samples))
    error = float(np.std(samples, ddof=1) / np.sqrt(samples.shape[0]))
    z = normal.ppf(0.5 * (1.0 + level))
    return mean - z * error, mean + z * error


def running_mean(samples):
    samples = np.asarray(samples, dtype=float)
    count = np.arange(1, samples.shape[0] + 1)
    return np.cumsum(samples) / count


def running_standard_error(samples):
    samples = np.asarray(samples, dtype=float)
    count = np.arange(1, samples.shape[0] + 1)
    cumulative = np.cumsum(samples)
    cumulative_square = np.cumsum(samples**2)
    mean = cumulative / count
    variance = (cumulative_square - count * mean**2) / np.maximum(count - 1, 1)
    return np.sqrt(variance / count)


def tail_probability(samples, level):
    samples = np.asarray(samples, dtype=float)
    return float(np.mean(samples > level))


def tail_probability_standard_error(samples, level):
    samples = np.asarray(samples, dtype=float)
    p = float(np.mean(samples > level))
    return float(np.sqrt(p * (1.0 - p) / samples.shape[0]))


def effective_sample_size(crude_variance, reduced_variance, n_samples):
    return n_samples * crude_variance / reduced_variance

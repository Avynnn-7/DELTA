from __future__ import annotations

import numpy as np
from scipy.special import gammaln

_SQRT_2_OVER_PI = np.sqrt(2.0 / np.pi)


def expected_abs_normal():
    return _SQRT_2_OVER_PI


def expected_abs_standard_t(nu):
    return np.sqrt((nu - 2.0) / np.pi) * np.exp(gammaln((nu - 1.0) / 2.0) - gammaln(nu / 2.0))


def garch_variance(innovations, omega, alpha, beta, initial):
    eps = np.asarray(innovations, dtype=float)
    n = eps.shape[0]
    sigma2 = np.empty(n, dtype=float)
    sigma2[0] = float(initial)
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
    return sigma2


def gjr_variance(innovations, omega, alpha, gamma, beta, initial):
    eps = np.asarray(innovations, dtype=float)
    n = eps.shape[0]
    sigma2 = np.empty(n, dtype=float)
    sigma2[0] = float(initial)
    for t in range(1, n):
        shock = eps[t - 1] ** 2
        leverage = gamma * shock if eps[t - 1] < 0.0 else 0.0
        sigma2[t] = omega + alpha * shock + leverage + beta * sigma2[t - 1]
    return sigma2


def egarch_variance(innovations, omega, alpha, gamma, beta, expected_abs_z, initial):
    eps = np.asarray(innovations, dtype=float)
    n = eps.shape[0]
    log_sigma2 = np.empty(n, dtype=float)
    log_sigma2[0] = float(initial)
    for t in range(1, n):
        sigma_prev = np.sqrt(np.exp(log_sigma2[t - 1]))
        z = eps[t - 1] / sigma_prev
        log_sigma2[t] = (
            omega
            + beta * log_sigma2[t - 1]
            + alpha * (np.abs(z) - expected_abs_z)
            + gamma * z
        )
    return np.exp(log_sigma2)


def long_run_variance(omega, persistence):
    if persistence >= 1.0:
        raise ValueError("long-run variance requires persistence < 1")
    return omega / (1.0 - persistence)


def garch_persistence(alpha, beta):
    return alpha + beta


def gjr_persistence(alpha, gamma, beta):
    return alpha + beta + 0.5 * gamma


def forecast_variance(one_step_variance, long_run, persistence, horizon):
    h = np.arange(1, horizon + 1, dtype=float)
    return long_run + persistence ** (h - 1.0) * (one_step_variance - long_run)


def aggregated_forecast_variance(one_step_variance, long_run, persistence, horizon):
    if persistence == 1.0:
        geometric = float(horizon)
    else:
        geometric = (1.0 - persistence**horizon) / (1.0 - persistence)
    return horizon * long_run + (one_step_variance - long_run) * geometric


def average_forecast_variance(one_step_variance, long_run, persistence, horizon):
    return aggregated_forecast_variance(one_step_variance, long_run, persistence, horizon) / horizon


def term_structure_volatility(one_step_variance, long_run, persistence, horizon, periods_per_year):
    average = average_forecast_variance(one_step_variance, long_run, persistence, horizon)
    return float(np.sqrt(average * periods_per_year))

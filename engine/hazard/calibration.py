from __future__ import annotations

import numpy as np
from scipy.special import expit, xlog1py, xlogy

from engine.numerics.optimize import minimize


def credit_triangle_intensity(spread, recovery):
    if np.any(np.asarray(recovery, dtype=float) >= 1.0):
        raise ValueError("recovery must be strictly less than 1")
    return np.asarray(spread, dtype=float) / (1.0 - np.asarray(recovery, dtype=float))


def poisson_mle_intensity(event_count, exposure_time):
    if exposure_time <= 0.0:
        raise ValueError("exposure_time must be positive")
    return event_count / exposure_time


def _gpd_negloglik(theta, exceedances):
    shape = theta[0]
    scale = np.exp(theta[1])
    n = exceedances.shape[0]
    if abs(shape) < 1e-8:
        return n * np.log(scale) + np.sum(exceedances) / scale
    z = 1.0 + shape * exceedances / scale
    if np.any(z <= 0.0):
        return np.inf
    return n * np.log(scale) + (1.0 / shape + 1.0) * np.sum(np.log(z))


def fit_gpd(exceedances, max_iter=20000):
    exceedances = np.asarray(exceedances, dtype=float)
    if np.any(exceedances <= 0.0):
        raise ValueError("exceedances must be positive")
    mean = float(exceedances.mean())
    variance = float(exceedances.var())
    shape0 = 0.5 * (1.0 - mean**2 / variance) if variance > 0.0 else 0.1
    scale0 = 0.5 * mean * (mean**2 / variance + 1.0) if variance > 0.0 else mean
    theta0 = np.array([shape0, np.log(max(scale0, 1e-6))])

    def objective(theta):
        return _gpd_negloglik(theta, exceedances)

    theta, neg_loglik, _ = minimize(objective, theta0, max_iter=max_iter)
    return {"shape": float(theta[0]), "scale": float(np.exp(theta[1])), "loglik": -neg_loglik}


def gpd_tail_exceedance_probability(level, threshold, shape, scale, exceedance_rate):
    excess = np.asarray(level, dtype=float) - threshold
    if abs(shape) < 1e-8:
        conditional = np.exp(-excess / scale)
    else:
        conditional = np.power(1.0 + shape * excess / scale, -1.0 / shape)
    return exceedance_rate * conditional


def _logistic_negloglik(beta, design, outcomes):
    eta = design @ beta
    p = expit(eta)
    return -np.sum(xlogy(outcomes, p) + xlog1py(1.0 - outcomes, -p))


def fit_logistic_hazard(design, outcomes, max_iter=20000):
    design = np.asarray(design, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    if design.ndim != 2 or design.shape[0] != outcomes.shape[0]:
        raise ValueError("design must be (n, k) aligned with outcomes")
    beta0 = np.zeros(design.shape[1], dtype=float)

    def objective(beta):
        return _logistic_negloglik(beta, design, outcomes)

    beta, neg_loglik, _ = minimize(objective, beta0, method="BFGS", max_iter=max_iter)
    return {"coefficients": beta, "loglik": -neg_loglik}


def logistic_hazard_probability(design, coefficients):
    return expit(np.asarray(design, dtype=float) @ np.asarray(coefficients, dtype=float))

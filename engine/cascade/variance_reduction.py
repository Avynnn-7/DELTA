from __future__ import annotations

import numpy as np
from scipy.stats import qmc

from engine.dependence.vasicek import conditional_default_probability
from engine.numerics import normal, rng, special


def antithetic_factors(z, epsilon):
    return -np.asarray(z, dtype=float), -np.asarray(epsilon, dtype=float)


def antithetic_average(primary, antithetic):
    return 0.5 * (np.asarray(primary, dtype=float) + np.asarray(antithetic, dtype=float))


def control_variate_estimator(samples, control, control_mean):
    samples = np.asarray(samples, dtype=float)
    control = np.asarray(control, dtype=float)
    covariance = np.cov(samples, control, ddof=1)
    coefficient = covariance[0, 1] / covariance[1, 1]
    adjusted = samples - coefficient * (control - control_mean)
    return adjusted, float(coefficient)


def vasicek_conditional_loss(common_factor, pd, rho, lgd, ead):
    common_factor = np.asarray(common_factor, dtype=float)
    probability = conditional_default_probability(pd, rho, common_factor[:, None])
    weights = np.asarray(lgd, dtype=float) * np.asarray(ead, dtype=float)
    return (probability * weights).sum(axis=1)


def vasicek_expected_loss(pd, rho, lgd, ead):
    weights = np.asarray(lgd, dtype=float) * np.asarray(ead, dtype=float)
    return float((np.asarray(pd, dtype=float) * weights).sum())


def conditional_monte_carlo_estimate(common_factor, pd, rho, lgd, ead):
    conditional = vasicek_conditional_loss(common_factor, pd, rho, lgd, ead)
    estimate = float(np.mean(conditional))
    error = float(np.std(conditional, ddof=1) / np.sqrt(conditional.shape[0]))
    return estimate, error


def exponential_tilt(generator, tilt, n_samples):
    z = rng.standard_normal(generator, size=n_samples) + tilt
    likelihood_ratio = np.exp(-tilt * z + 0.5 * tilt**2)
    return z, likelihood_ratio


def importance_sampling_estimate(functional, likelihood_ratio):
    weighted = np.asarray(functional, dtype=float) * np.asarray(likelihood_ratio, dtype=float)
    estimate = float(np.mean(weighted))
    error = float(np.std(weighted, ddof=1) / np.sqrt(weighted.shape[0]))
    return estimate, error


def sobol_factors(n_assets, n_samples, nu, seed):
    sampler = qmc.Sobol(d=n_assets + 2, scramble=True, seed=seed)
    points = sampler.random(n_samples)
    z = normal.ppf(points[:, 0])
    epsilon = normal.ppf(points[:, 1 : 1 + n_assets])
    mixing = special.chi2_ppf(points[:, -1], nu)
    return z, epsilon, mixing

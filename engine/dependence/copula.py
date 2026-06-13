from __future__ import annotations

import numpy as np
from scipy.special import stdtr, stdtrit

from engine.numerics import normal, special


def student_t_ppf(u, nu):
    return stdtrit(nu, np.asarray(u, dtype=float))


def student_t_cdf(x, nu):
    return stdtr(nu, np.asarray(x, dtype=float))


def gaussian_copula_cdf(u, corr, samples=20000, seed=0):
    u = np.asarray(u, dtype=float)
    thresholds = normal.ppf(u)
    estimate, error = special.mvn_cdf(thresholds, corr, samples=samples, seed=seed)
    return estimate, error


def student_t_copula_cdf(u, corr, nu, samples=20000, seed=0):
    u = np.asarray(u, dtype=float)
    thresholds = student_t_ppf(u, nu)
    estimate, error = special.mvt_cdf(thresholds, corr, df=nu, samples=samples, seed=seed)
    return estimate, error


def gaussian_lower_tail_dependence(rho):
    rho = np.asarray(rho, dtype=float)
    return np.where(rho >= 1.0, 1.0, 0.0)


def student_t_lower_tail_dependence(rho, nu):
    rho = np.asarray(rho, dtype=float)
    argument = -np.sqrt(nu + 1.0) * np.sqrt((1.0 - rho) / (1.0 + rho))
    return 2.0 * stdtr(nu + 1.0, argument)

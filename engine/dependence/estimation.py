from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau

from engine.dependence.copula import student_t_lower_tail_dependence
from engine.numerics import linalg
from engine.numerics.optimize import brentq


def kendall_tau_matrix(returns):
    returns = np.asarray(returns, dtype=float)
    d = returns.shape[1]
    tau = np.ones((d, d), dtype=float)
    for i in range(d):
        for j in range(i + 1, d):
            value = kendalltau(returns[:, i], returns[:, j]).statistic
            tau[i, j] = value
            tau[j, i] = value
    return tau


def correlation_from_kendall(tau):
    tau = np.asarray(tau, dtype=float)
    corr = np.sin(np.pi / 2.0 * tau)
    np.fill_diagonal(corr, 1.0)
    eigenvalues = np.linalg.eigvalsh(corr)
    if eigenvalues.min() < 0.0:
        corr = linalg.nearest_correlation(corr)
    return corr


def factor_loadings(corr, max_iter=200, tol=1e-12):
    corr = np.asarray(corr, dtype=float)
    d = corr.shape[0]
    off_diagonal = np.abs(corr - np.eye(d))
    communality = off_diagonal.max(axis=1) ** 2
    reduced = corr.copy()
    beta = np.zeros(d)
    for _ in range(max_iter):
        np.fill_diagonal(reduced, communality)
        values, vectors = np.linalg.eigh(reduced)
        beta = np.sqrt(max(values[-1], 0.0)) * vectors[:, -1]
        if np.sum(beta) < 0.0:
            beta = -beta
        new_communality = np.clip(beta**2, 0.0, 1.0)
        if np.max(np.abs(new_communality - communality)) < tol:
            communality = new_communality
            break
        communality = new_communality
    return np.clip(beta**2, 0.0, 1.0)


def empirical_lower_tail_dependence(u, threshold):
    u = np.asarray(u, dtype=float)
    first = u[:, 0] <= threshold
    joint = first & (u[:, 1] <= threshold)
    count_first = np.count_nonzero(first)
    if count_first == 0:
        return 0.0
    return np.count_nonzero(joint) / count_first


def fit_nu_method_of_moments(empirical_lambda, rho, nu_bounds=(2.01, 200.0)):
    if empirical_lambda <= 0.0:
        return float(nu_bounds[1])

    def objective(nu):
        return student_t_lower_tail_dependence(rho, nu) - empirical_lambda

    low, high = nu_bounds
    if objective(low) < 0.0:
        return float(low)
    if objective(high) > 0.0:
        return float(high)
    return brentq(objective, low, high)

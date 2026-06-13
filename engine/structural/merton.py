from __future__ import annotations

import numpy as np

from engine.numerics import normal


def distance_to_default(v0, debt, drift, sigma, horizon):
    v0 = np.asarray(v0, dtype=float)
    debt = np.asarray(debt, dtype=float)
    denom = sigma * np.sqrt(horizon)
    return (np.log(v0 / debt) + (drift - 0.5 * sigma**2) * horizon) / denom


def probability_of_default(v0, debt, drift, sigma, horizon):
    return normal.cdf(-distance_to_default(v0, debt, drift, sigma, horizon))


def _d1_d2(v0, debt, rate, sigma, horizon):
    root = sigma * np.sqrt(horizon)
    d1 = (np.log(v0 / debt) + (rate + 0.5 * sigma**2) * horizon) / root
    d2 = d1 - root
    return d1, d2


def equity_value(v0, sigma, debt, rate, horizon):
    d1, d2 = _d1_d2(v0, debt, rate, sigma, horizon)
    return v0 * normal.cdf(d1) - debt * np.exp(-rate * horizon) * normal.cdf(d2)


def _residual(v0, sigma, equity, equity_vol, debt, rate, horizon):
    d1, _ = _d1_d2(v0, debt, rate, sigma, horizon)
    f1 = equity_value(v0, sigma, debt, rate, horizon) - equity
    f2 = normal.cdf(d1) * sigma * v0 - equity_vol * equity
    return np.array([f1, f2]), d1


def _jacobian(v0, sigma, debt, rate, horizon, d1):
    root = np.sqrt(horizon)
    phi = normal.pdf(d1)
    cdf = normal.cdf(d1)
    a = np.log(v0 / debt) + rate * horizon
    j11 = cdf
    j12 = v0 * phi * root
    j21 = sigma * cdf + phi / root
    j22 = v0 * cdf + sigma * v0 * phi * (0.5 * root - a / (sigma**2 * root))
    return np.array([[j11, j12], [j21, j22]])


def invert_assets(equity, equity_vol, debt, rate, horizon, max_iter=100, tol=1e-12):
    v0 = equity + debt * np.exp(-rate * horizon)
    sigma = equity_vol * equity / v0
    for _ in range(max_iter):
        residual, d1 = _residual(v0, sigma, equity, equity_vol, debt, rate, horizon)
        if np.linalg.norm(residual) < tol:
            break
        jacobian = _jacobian(v0, sigma, debt, rate, horizon, d1)
        step = np.linalg.solve(jacobian, residual)
        v0 = v0 - step[0]
        sigma = sigma - step[1]
        if v0 <= 0.0 or sigma <= 0.0:
            raise ValueError("inversion left the economic domain")
    else:
        raise ValueError("inversion did not converge")
    return float(v0), float(sigma)


def inversion_jacobian_determinant(v0, sigma, debt, rate, horizon):
    d1, _ = _d1_d2(v0, debt, rate, sigma, horizon)
    return float(np.linalg.det(_jacobian(v0, sigma, debt, rate, horizon, d1)))

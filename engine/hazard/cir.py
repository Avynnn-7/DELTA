from __future__ import annotations

import numpy as np


def feller_condition(kappa, theta, nu):
    return 2.0 * kappa * theta >= nu**2


def _gamma(kappa, nu):
    return np.sqrt(kappa**2 + 2.0 * nu**2)


def riccati_b(t, kappa, nu):
    t = np.asarray(t, dtype=float)
    gamma = _gamma(kappa, nu)
    expm1_gamma = np.expm1(gamma * t)
    denom = (gamma + kappa) * expm1_gamma + 2.0 * gamma
    return 2.0 * expm1_gamma / denom


def riccati_a(t, kappa, theta, nu):
    t = np.asarray(t, dtype=float)
    gamma = _gamma(kappa, nu)
    expm1_gamma = np.expm1(gamma * t)
    denom = (gamma + kappa) * expm1_gamma + 2.0 * gamma
    numerator = 2.0 * gamma * np.exp((kappa + gamma) * t / 2.0)
    exponent = 2.0 * kappa * theta / nu**2
    return (numerator / denom) ** exponent


def survival(t, kappa, theta, nu, lambda_0):
    if not feller_condition(kappa, theta, nu):
        raise ValueError("Feller condition 2*kappa*theta >= nu**2 violated")
    return riccati_a(t, kappa, theta, nu) * np.exp(-riccati_b(t, kappa, nu) * lambda_0)


def cumulative_hazard(t, kappa, theta, nu, lambda_0):
    return -np.log(survival(t, kappa, theta, nu, lambda_0))

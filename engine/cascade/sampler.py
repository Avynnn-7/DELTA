from __future__ import annotations

import numpy as np
from scipy.special import stdtr, stdtrit

from engine.hazard import cox
from engine.numerics import rng


def draw_factors(generator, n_samples, n_assets, nu):
    z = rng.standard_normal(generator, size=n_samples)
    epsilon = rng.standard_normal(generator, size=(n_samples, n_assets))
    mixing = generator.standard_gamma(nu / 2.0, size=n_samples) * 2.0
    return z, epsilon, mixing


def latent_factor(z, epsilon, mixing, loadings, nu):
    loadings = np.asarray(loadings, dtype=float)
    z = np.asarray(z, dtype=float)
    epsilon = np.asarray(epsilon, dtype=float)
    gaussian = np.sqrt(loadings) * z[:, None] + np.sqrt(1.0 - loadings) * epsilon
    scale = np.sqrt(nu / np.asarray(mixing, dtype=float))
    return scale[:, None] * gaussian


def copula_uniform(latent, nu):
    return stdtr(nu, np.asarray(latent, dtype=float))


def marginal_return(uniform, mu, sigma, nu_marginal):
    uniform = np.asarray(uniform, dtype=float)
    nu_marginal = np.asarray(nu_marginal, dtype=float)
    standardized = stdtrit(nu_marginal, uniform) * np.sqrt((nu_marginal - 2.0) / nu_marginal)
    return np.asarray(mu, dtype=float) + np.asarray(sigma, dtype=float) * standardized


def price_multiplier(returns):
    return np.exp(np.asarray(returns, dtype=float))


def price_shock(z, epsilon, mixing, loadings, nu, mu, sigma, nu_marginal):
    latent = latent_factor(z, epsilon, mixing, loadings, nu)
    uniform = copula_uniform(latent, nu)
    returns = marginal_return(uniform, mu, sigma, nu_marginal)
    return price_multiplier(returns)


def pegged_default_time(uniform, times, cumulative_hazard):
    uniform = np.atleast_1d(np.asarray(uniform, dtype=float))
    thresholds = -np.log1p(-uniform)
    return np.array([cox.default_time(times, cumulative_hazard, e) for e in thresholds])

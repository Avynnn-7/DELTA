from __future__ import annotations

import numpy as np

from engine.numerics import linalg, normal, rng


def default_threshold(pd):
    return normal.ppf(np.asarray(pd, dtype=float))


def one_factor_gaussian(generator, loadings, samples):
    loadings = np.asarray(loadings, dtype=float)
    d = loadings.shape[0]
    z = rng.standard_normal(generator, size=samples)
    epsilon = rng.standard_normal(generator, size=(samples, d))
    return np.sqrt(loadings) * z[:, None] + np.sqrt(1.0 - loadings) * epsilon


def one_factor_student_t(generator, loadings, nu, samples):
    loadings = np.asarray(loadings, dtype=float)
    gaussian = one_factor_gaussian(generator, loadings, samples)
    mixing = generator.standard_gamma(nu / 2.0, size=samples) * 2.0
    scale = np.sqrt(nu / mixing)
    return scale[:, None] * gaussian


def full_matrix_gaussian(generator, corr, samples):
    chol = linalg.cholesky(corr)
    z = rng.standard_normal(generator, size=(samples, corr.shape[0]))
    return z @ chol.T


def full_matrix_student_t(generator, corr, nu, samples):
    gaussian = full_matrix_gaussian(generator, corr, samples)
    mixing = generator.standard_gamma(nu / 2.0, size=samples) * 2.0
    scale = np.sqrt(nu / mixing)
    return scale[:, None] * gaussian


def default_indicator(latent, thresholds):
    return np.asarray(latent, dtype=float) < np.asarray(thresholds, dtype=float)

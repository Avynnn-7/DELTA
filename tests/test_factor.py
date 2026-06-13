import numpy as np

from engine.dependence import factor
from engine.numerics import normal, rng


def test_one_factor_gaussian_correlation_structure():
    loadings = np.array([0.2, 0.5, 0.8])
    generator = rng.generator(seed=10)
    samples = factor.one_factor_gaussian(generator, loadings, 400000)
    variances = samples.var(axis=0)
    np.testing.assert_allclose(variances, 1.0, atol=2e-2)
    corr = np.corrcoef(samples, rowvar=False)
    expected_01 = np.sqrt(loadings[0] * loadings[1])
    expected_02 = np.sqrt(loadings[0] * loadings[2])
    expected_12 = np.sqrt(loadings[1] * loadings[2])
    assert abs(corr[0, 1] - expected_01) < 1e-2
    assert abs(corr[0, 2] - expected_02) < 1e-2
    assert abs(corr[1, 2] - expected_12) < 1e-2


def test_one_factor_gaussian_preserves_marginal_pd():
    loadings = np.array([0.4, 0.4])
    pd = np.array([0.05, 0.1])
    thresholds = factor.default_threshold(pd)
    generator = rng.generator(seed=11)
    samples = factor.one_factor_gaussian(generator, loadings, 600000)
    indicators = factor.default_indicator(samples, thresholds)
    empirical = indicators.mean(axis=0)
    np.testing.assert_allclose(empirical, pd, atol=3e-3)


def test_default_threshold_matches_ppf():
    pd = np.array([0.01, 0.2, 0.5])
    np.testing.assert_allclose(factor.default_threshold(pd), normal.ppf(pd))


def test_one_factor_student_t_unit_variance():
    loadings = np.array([0.3, 0.6])
    nu = 8.0
    generator = rng.generator(seed=12)
    samples = factor.one_factor_student_t(generator, loadings, nu, 400000)
    variances = samples.var(axis=0)
    expected = nu / (nu - 2.0)
    np.testing.assert_allclose(variances, expected, rtol=5e-2)


def test_full_matrix_gaussian_recovers_correlation():
    corr = np.array([[1.0, 0.3, 0.1], [0.3, 1.0, 0.4], [0.1, 0.4, 1.0]])
    generator = rng.generator(seed=13)
    samples = factor.full_matrix_gaussian(generator, corr, 400000)
    empirical = np.corrcoef(samples, rowvar=False)
    np.testing.assert_allclose(empirical, corr, atol=2e-2)


def test_full_matrix_student_t_correlation():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    nu = 10.0
    generator = rng.generator(seed=14)
    samples = factor.full_matrix_student_t(generator, corr, nu, 400000)
    empirical = np.corrcoef(samples, rowvar=False)
    np.testing.assert_allclose(empirical, corr, atol=2e-2)

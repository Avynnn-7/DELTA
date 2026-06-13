import numpy as np
from scipy import stats

from engine.dependence import copula


def test_gaussian_copula_uniform_margins():
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    value, error = copula.gaussian_copula_cdf([1.0, 0.7], corr, samples=200000, seed=3)
    assert abs(value - 0.7) < 5.0 * error + 1e-3


def test_gaussian_copula_matches_bivariate_normal():
    rho = 0.4
    corr = np.array([[1.0, rho], [rho, 1.0]])
    u = np.array([0.3, 0.6])
    value, error = copula.gaussian_copula_cdf(u, corr, samples=400000, seed=1)
    thresholds = stats.norm.ppf(u)
    reference = stats.multivariate_normal(mean=[0, 0], cov=corr).cdf(thresholds)
    assert abs(value - reference) < 5.0 * error + 2e-3


def test_student_t_copula_uniform_margins():
    corr = np.array([[1.0, 0.3], [0.3, 1.0]])
    value, error = copula.student_t_copula_cdf([1.0, 0.4], corr, nu=6.0, samples=200000, seed=4)
    assert abs(value - 0.4) < 5.0 * error + 1e-3


def test_student_t_copula_matches_multivariate_t():
    rho, nu = 0.5, 8.0
    corr = np.array([[1.0, rho], [rho, 1.0]])
    u = np.array([0.4, 0.7])
    value, error = copula.student_t_copula_cdf(u, corr, nu=nu, samples=400000, seed=2)
    thresholds = copula.student_t_ppf(u, nu)
    reference = stats.multivariate_t(loc=[0, 0], shape=corr, df=nu).cdf(thresholds)
    assert abs(value - reference) < 5.0 * error + 3e-3


def test_gaussian_zero_tail_dependence():
    assert copula.gaussian_lower_tail_dependence(0.6) == 0.0
    assert copula.gaussian_lower_tail_dependence(0.99) == 0.0


def test_student_t_positive_tail_dependence():
    lam = copula.student_t_lower_tail_dependence(0.5, 6.0)
    assert 0.0 < lam < 1.0


def test_student_t_tail_dependence_matches_formula():
    rho, nu = 0.5, 6.0
    arg = -np.sqrt(nu + 1.0) * np.sqrt((1.0 - rho) / (1.0 + rho))
    expected = 2.0 * stats.t.cdf(arg, nu + 1.0)
    assert np.isclose(copula.student_t_lower_tail_dependence(rho, nu), expected)


def test_tail_dependence_vanishes_as_nu_grows():
    high_nu = copula.student_t_lower_tail_dependence(0.5, 1000.0)
    low_nu = copula.student_t_lower_tail_dependence(0.5, 4.0)
    assert high_nu < low_nu
    assert high_nu < 1e-2


def test_univariate_t_roundtrip():
    nu = 7.0
    u = np.array([0.05, 0.3, 0.5, 0.8, 0.95])
    np.testing.assert_allclose(copula.student_t_cdf(copula.student_t_ppf(u, nu), nu), u, atol=1e-10)

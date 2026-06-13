import numpy as np

from engine.dependence import copula, estimation
from engine.numerics import rng


def test_correlation_from_kendall_formula():
    tau = np.array([[1.0, 0.3], [0.3, 1.0]])
    corr = estimation.correlation_from_kendall(tau)
    expected = np.sin(np.pi / 2.0 * 0.3)
    assert np.isclose(corr[0, 1], expected)
    assert np.isclose(corr[0, 0], 1.0)


def test_correlation_from_kendall_is_positive_definite():
    tau = np.array(
        [[1.0, 0.7, -0.6], [0.7, 1.0, 0.7], [-0.6, 0.7, 1.0]]
    )
    corr = estimation.correlation_from_kendall(tau)
    eigenvalues = np.linalg.eigvalsh(corr)
    assert eigenvalues.min() >= -1e-10
    np.testing.assert_allclose(np.diag(corr), 1.0)


def test_kendall_tau_matrix_recovers_dependence():
    rho = 0.6
    corr = np.array([[1.0, rho], [rho, 1.0]])
    generator = rng.generator(seed=31)
    chol = np.linalg.cholesky(corr)
    z = rng.standard_normal(generator, size=(20000, 2)) @ chol.T
    tau = estimation.kendall_tau_matrix(z)
    recovered = estimation.correlation_from_kendall(tau)
    assert abs(recovered[0, 1] - rho) < 5e-2


def test_factor_loadings_recover_rank_one_structure():
    loadings_true = np.array([0.3, 0.5, 0.8])
    beta = np.sqrt(loadings_true)
    corr = np.outer(beta, beta)
    np.fill_diagonal(corr, 1.0)
    loadings = estimation.factor_loadings(corr)
    np.testing.assert_allclose(loadings, loadings_true, atol=5e-2)


def test_fit_nu_method_of_moments_recovers_nu():
    rho, nu_true = 0.5, 6.0
    lam = copula.student_t_lower_tail_dependence(rho, nu_true)
    nu_fit = estimation.fit_nu_method_of_moments(lam, rho)
    assert abs(nu_fit - nu_true) < 1e-2


def test_fit_nu_zero_tail_dependence_returns_upper_bound():
    nu_fit = estimation.fit_nu_method_of_moments(0.0, 0.5)
    assert nu_fit == 200.0


def test_empirical_lower_tail_dependence_detects_dependence():
    rho, nu = 0.6, 5.0
    corr = np.array([[1.0, rho], [rho, 1.0]])
    generator = rng.generator(seed=32)
    samples = 200000
    gaussian = rng.standard_normal(generator, size=(samples, 2)) @ np.linalg.cholesky(corr).T
    mixing = generator.standard_gamma(nu / 2.0, size=samples) * 2.0
    t_samples = np.sqrt(nu / mixing)[:, None] * gaussian
    u = copula.student_t_cdf(t_samples, nu)
    lam = estimation.empirical_lower_tail_dependence(u, 0.01)
    theoretical = copula.student_t_lower_tail_dependence(rho, nu)
    assert abs(lam - theoretical) < 8e-2

import numpy as np
from scipy import stats

from engine.volatility import garch


def test_garch_long_run_variance():
    omega, alpha, beta = 1e-6, 0.05, 0.90
    persistence = garch.garch_persistence(alpha, beta)
    expected = omega / (1.0 - persistence)
    assert np.isclose(garch.long_run_variance(omega, persistence), expected)


def test_garch_recursion_matches_definition():
    eps = np.array([0.01, -0.02, 0.03, -0.015, 0.008])
    omega, alpha, beta = 1e-5, 0.08, 0.88
    seed = 1e-4
    sigma2 = garch.garch_variance(eps, omega, alpha, beta, seed)
    expected = np.empty(eps.shape[0])
    expected[0] = seed
    for t in range(1, eps.shape[0]):
        expected[t] = omega + alpha * eps[t - 1] ** 2 + beta * expected[t - 1]
    np.testing.assert_allclose(sigma2, expected)


def test_gjr_leverage_increases_variance_after_negative_shock():
    eps_neg = np.array([0.0, -0.05, 0.0])
    eps_pos = np.array([0.0, 0.05, 0.0])
    omega, alpha, gamma, beta = 1e-6, 0.03, 0.06, 0.90
    seed = 1e-4
    after_neg = garch.gjr_variance(eps_neg, omega, alpha, gamma, beta, seed)[2]
    after_pos = garch.gjr_variance(eps_pos, omega, alpha, gamma, beta, seed)[2]
    assert after_neg > after_pos


def test_forecast_variance_mean_reverts():
    omega, alpha, beta = 1e-6, 0.05, 0.90
    persistence = garch.garch_persistence(alpha, beta)
    long_run = garch.long_run_variance(omega, persistence)
    one_step = 4.0 * long_run
    path = garch.forecast_variance(one_step, long_run, persistence, 200)
    assert np.isclose(path[0], one_step)
    assert path[-1] < path[0]
    assert np.isclose(path[-1], long_run, atol=0.05 * long_run)


def test_aggregated_forecast_matches_explicit_sum():
    omega, alpha, beta = 1e-6, 0.07, 0.88
    persistence = garch.garch_persistence(alpha, beta)
    long_run = garch.long_run_variance(omega, persistence)
    one_step = 2.0 * long_run
    horizon = 50
    explicit = np.sum(garch.forecast_variance(one_step, long_run, persistence, horizon))
    aggregated = garch.aggregated_forecast_variance(one_step, long_run, persistence, horizon)
    assert np.isclose(aggregated, explicit)


def test_term_structure_volatility_annualizes_average():
    omega, alpha, beta = 1e-6, 0.05, 0.90
    persistence = garch.garch_persistence(alpha, beta)
    long_run = garch.long_run_variance(omega, persistence)
    one_step = long_run
    sigma_t = garch.term_structure_volatility(one_step, long_run, persistence, 24, 8760)
    assert np.isclose(sigma_t, np.sqrt(long_run * 8760))


def test_expected_abs_normal():
    assert np.isclose(garch.expected_abs_normal(), np.sqrt(2.0 / np.pi))


def test_expected_abs_standard_t_matches_simulation():
    nu = 8.0
    sample = stats.t.rvs(nu, size=4_000_000, random_state=0)
    standardized = sample / np.sqrt(nu / (nu - 2.0))
    np.testing.assert_allclose(
        garch.expected_abs_standard_t(nu), np.mean(np.abs(standardized)), rtol=5e-3
    )

import numpy as np
from scipy import stats

from engine.structural import dtl
from validation import probabilistic


def test_health_factor_definition():
    collateral, debt, ell = 200.0, 100.0, 0.8
    assert np.isclose(dtl.health_factor(collateral, debt, ell), ell * collateral / debt)


def test_dtl_is_standardized_log_health():
    h0, mu, sigma, T = 1.6, 0.0, 0.4, 0.5
    expected = (np.log(h0) + (mu - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    assert np.isclose(dtl.distance_to_liquidation(h0, mu, sigma, T), expected)


def test_pl_equals_phi_minus_dtl():
    h0, mu, sigma, T = 1.6, 0.0, 0.4, 0.5
    dist = dtl.distance_to_liquidation(h0, mu, sigma, T)
    assert np.isclose(dtl.probability_of_liquidation(h0, mu, sigma, T), stats.norm.cdf(-dist))


def test_pl_matches_monte_carlo():
    h0, mu, sigma, T = 1.5, 0.0, 0.6, 0.25
    gen = np.random.default_rng(1)
    z = gen.standard_normal(4_000_000)
    ht = h0 * np.exp((mu - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    empirical = np.mean(ht < 1.0)
    analytic = dtl.probability_of_liquidation(h0, mu, sigma, T)
    assert abs(analytic - empirical) < 2e-3


def test_drop_to_liquidation_is_model_free():
    h0 = np.array([1.0, 2.0, 4.0])
    np.testing.assert_allclose(dtl.drop_to_liquidation(h0), 1.0 - 1.0 / h0)
    assert dtl.drop_to_liquidation(1.0) == 0.0


def test_interest_adjusted_drift():
    assert np.isclose(dtl.interest_adjusted_drift(0.1, 0.04), 0.06)
    assert np.isclose(dtl.interest_adjusted_drift(0.04, 0.04), 0.0)


def test_interest_adjusted_drift_matches_ratio_process():
    h0, mu, r_b, sigma, T = 1.5, 0.1, 0.04, 0.4, 0.5
    gen = np.random.default_rng(2)
    z = gen.standard_normal(4_000_000)
    collateral_ret = np.exp((mu - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    debt_growth = np.exp(r_b * T)
    ht = h0 * collateral_ret / debt_growth
    empirical = np.mean(ht < 1.0)
    drift = dtl.interest_adjusted_drift(mu, r_b)
    analytic = dtl.probability_of_liquidation(h0, drift, sigma, T)
    assert abs(analytic - empirical) < 2e-3


def test_term_structure_monotone_in_horizon_for_unsafe_position():
    h0, mu, sigma = 1.2, 0.0, 0.5
    horizons = np.array([1.0, 7.0, 30.0, 90.0]) / 365.0
    pl = dtl.term_structure(h0, mu, sigma, horizons)
    probabilistic.assert_monotone_non_decreasing(pl)
    probabilistic.assert_in_unit_interval(pl)

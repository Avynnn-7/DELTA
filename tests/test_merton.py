import numpy as np
from scipy import stats

from engine.structural import merton


def test_distance_to_default_definition():
    v0, debt, mu, sigma, T = 120.0, 100.0, 0.05, 0.3, 1.0
    expected = (np.log(v0 / debt) + (mu - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    assert np.isclose(merton.distance_to_default(v0, debt, mu, sigma, T), expected)


def test_pd_equals_phi_minus_dd():
    v0, debt, mu, sigma, T = 120.0, 100.0, 0.05, 0.3, 1.0
    dd = merton.distance_to_default(v0, debt, mu, sigma, T)
    assert np.isclose(merton.probability_of_default(v0, debt, mu, sigma, T), stats.norm.cdf(-dd))


def test_pd_matches_monte_carlo():
    v0, debt, mu, sigma, T = 100.0, 90.0, 0.0, 0.5, 1.0
    gen = np.random.default_rng(0)
    z = gen.standard_normal(4_000_000)
    vt = v0 * np.exp((mu - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    empirical = np.mean(vt < debt)
    analytic = merton.probability_of_default(v0, debt, mu, sigma, T)
    assert abs(analytic - empirical) < 2e-3


def test_equity_value_is_black_scholes_call():
    v0, sigma, debt, r, T = 100.0, 0.25, 80.0, 0.03, 2.0
    d1 = (np.log(v0 / debt) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    expected = v0 * stats.norm.cdf(d1) - debt * np.exp(-r * T) * stats.norm.cdf(d2)
    assert np.isclose(merton.equity_value(v0, sigma, debt, r, T), expected)


def test_inversion_recovers_assets():
    v0_true, sigma_true, debt, r, T = 130.0, 0.28, 100.0, 0.04, 1.5
    equity = merton.equity_value(v0_true, sigma_true, debt, r, T)
    d1 = (np.log(v0_true / debt) + (r + 0.5 * sigma_true**2) * T) / (sigma_true * np.sqrt(T))
    equity_vol = stats.norm.cdf(d1) * sigma_true * v0_true / equity
    v0, sigma = merton.invert_assets(equity, equity_vol, debt, r, T)
    assert np.isclose(v0, v0_true, rtol=1e-8)
    assert np.isclose(sigma, sigma_true, rtol=1e-8)


def test_inversion_jacobian_non_singular():
    v0, sigma, debt, r, T = 130.0, 0.28, 100.0, 0.04, 1.5
    det = merton.inversion_jacobian_determinant(v0, sigma, debt, r, T)
    assert abs(det) > 1e-8


def test_dd_increasing_pd_decreasing_in_value():
    debt, mu, sigma, T = 100.0, 0.05, 0.3, 1.0
    values = np.array([105.0, 120.0, 150.0])
    dd = merton.distance_to_default(values, debt, mu, sigma, T)
    pd = merton.probability_of_default(values, debt, mu, sigma, T)
    assert np.all(np.diff(dd) > 0.0)
    assert np.all(np.diff(pd) < 0.0)

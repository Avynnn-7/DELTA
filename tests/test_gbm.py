import numpy as np

from engine.numerics import rng
from engine.process import gbm


def test_log_return_law_moments():
    mu, sigma, t = 0.1, 0.4, 2.0
    assert gbm.log_return_mean(mu, sigma, t) == (mu - 0.5 * sigma**2) * t
    assert gbm.log_return_variance(sigma, t) == sigma**2 * t


def test_expected_price_has_no_volatility_drag():
    p0, mu, sigma, t = 100.0, 0.2, 0.5, 1.5
    assert np.isclose(gbm.expected_price(p0, mu, t), p0 * np.exp(mu * t))


def test_price_variance_matches_lognormal():
    p0, mu, sigma, t = 100.0, 0.05, 0.3, 1.0
    expected = p0**2 * np.exp(2.0 * mu * t) * (np.exp(sigma**2 * t) - 1.0)
    assert np.isclose(gbm.price_variance(p0, mu, sigma, t), expected)


def test_terminal_sampler_reproduces_lognormal_moments():
    p0, mu, sigma, t = 100.0, 0.1, 0.4, 1.0
    gen = rng.generator(7)
    draws = gbm.sample_terminal(p0, mu, sigma, t, gen, size=2_000_000)
    np.testing.assert_allclose(draws.mean(), gbm.expected_price(p0, mu, t), rtol=2e-3)
    np.testing.assert_allclose(draws.var(), gbm.price_variance(p0, mu, sigma, t), rtol=5e-3)


def test_terminal_log_return_is_normal():
    p0, mu, sigma, t = 50.0, -0.05, 0.6, 0.75
    gen = rng.generator(11)
    draws = gbm.sample_terminal(p0, mu, sigma, t, gen, size=2_000_000)
    log_ret = np.log(draws / p0)
    np.testing.assert_allclose(log_ret.mean(), gbm.log_return_mean(mu, sigma, t), atol=2e-3)
    np.testing.assert_allclose(log_ret.var(), gbm.log_return_variance(sigma, t), rtol=5e-3)


def test_path_sampler_terminal_consistency():
    p0, mu, sigma = 100.0, 0.0, 0.5
    times = np.linspace(0.1, 1.0, 10)
    gen = rng.generator(3)
    paths = gbm.sample_path(p0, mu, sigma, times, gen, paths=500000)
    terminal = paths[:, -1]
    np.testing.assert_allclose(terminal.mean(), gbm.expected_price(p0, mu, 1.0), rtol=3e-3)
    log_ret = np.log(terminal / p0)
    np.testing.assert_allclose(log_ret.var(), sigma**2 * 1.0, rtol=1e-2)


def test_short_horizon_drift_default():
    assert gbm.short_horizon_drift() == 0.0
    assert gbm.short_horizon_drift(0.03) == 0.03

import numpy as np

from engine.dependence import factor, vasicek
from engine.numerics import normal, rng
from engine.numerics.optimize import brentq


def test_loss_cdf_valid_on_unit_interval():
    pd, rho = 0.05, 0.3
    x = np.linspace(0.001, 0.999, 50)
    values = vasicek.loss_cdf(x, pd, rho)
    assert np.all(values >= 0.0)
    assert np.all(values <= 1.0)
    assert np.all(np.diff(values) >= -1e-12)


def test_loss_cdf_matches_monte_carlo():
    pd, rho = 0.1, 0.25
    generator = rng.generator(seed=21)
    samples = 200000
    z = rng.standard_normal(generator, size=samples)
    conditional = vasicek.conditional_default_probability(pd, rho, z)
    loss = conditional
    x = 0.15
    empirical = np.mean(loss <= x)
    analytic = vasicek.loss_cdf(x, pd, rho)
    assert abs(empirical - analytic) < 5e-3


def test_conditional_default_probability_monotone_decreasing():
    pd, rho = 0.08, 0.4
    z = np.linspace(-4.0, 4.0, 100)
    p = vasicek.conditional_default_probability(pd, rho, z)
    assert np.all(np.diff(p) <= 1e-12)


def test_conditional_default_probability_mean_equals_pd():
    pd, rho = 0.06, 0.35
    generator = rng.generator(seed=22)
    z = rng.standard_normal(generator, size=400000)
    p = vasicek.conditional_default_probability(pd, rho, z)
    assert abs(p.mean() - pd) < 2e-3


def test_loss_quantile_inverts_loss_cdf():
    pd, rho = 0.05, 0.3
    level = 0.99
    quantile = vasicek.loss_quantile(level, pd, rho)
    assert np.isclose(vasicek.loss_cdf(quantile, pd, rho), level, atol=1e-8)


def test_loss_cdf_limit_zero_correlation():
    pd = 0.1
    rho = 1e-8
    x = 0.2
    value = vasicek.loss_cdf(x, pd, rho)
    assert value > 0.999

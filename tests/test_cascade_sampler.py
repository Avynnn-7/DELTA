import numpy as np
from scipy import stats

from engine.cascade import sampler
from engine.hazard import survival
from engine.numerics import rng


def test_marginal_return_moments():
    mu = np.array([0.0, 0.01])
    sigma = np.array([0.05, 0.1])
    nu_marginal = np.array([8.0, 10.0])
    generator = rng.generator(seed=40)
    n = 400000
    z, epsilon, mixing = sampler.draw_factors(generator, n, 2, nu=6.0)
    multipliers = sampler.price_shock(z, epsilon, mixing, np.array([0.3, 0.5]), 6.0, mu, sigma, nu_marginal)
    returns = np.log(multipliers)
    np.testing.assert_allclose(returns.mean(axis=0), mu, atol=5e-3)
    np.testing.assert_allclose(returns.std(axis=0), sigma, rtol=5e-2)


def test_copula_uniform_is_uniform():
    generator = rng.generator(seed=41)
    n = 200000
    z, epsilon, mixing = sampler.draw_factors(generator, n, 1, nu=7.0)
    latent = sampler.latent_factor(z, epsilon, mixing, np.array([0.4]), 7.0)
    u = sampler.copula_uniform(latent, 7.0)[:, 0]
    ks = stats.kstest(u, "uniform").statistic
    assert ks < 5e-3


def test_factor_correlation_structure():
    loadings = np.array([0.3, 0.7])
    generator = rng.generator(seed=42)
    n = 400000
    z, epsilon, mixing = sampler.draw_factors(generator, n, 2, nu=12.0)
    latent = sampler.latent_factor(z, epsilon, mixing, loadings, 12.0)
    corr = np.corrcoef(latent, rowvar=False)
    expected = np.sqrt(loadings[0] * loadings[1])
    assert abs(corr[0, 1] - expected) < 1e-2


def test_pegged_default_time_recovers_marginal_pd():
    times = np.linspace(0.0, 1.0, 51)
    intensity = 0.3
    cumulative_hazard = intensity * times
    horizon = 1.0
    pd = survival.default_probability(intensity * horizon)
    generator = rng.generator(seed=43)
    u = rng.uniform_open(generator, size=200000)
    tau = sampler.pegged_default_time(u, times, cumulative_hazard)
    empirical = np.mean(tau <= horizon)
    assert abs(empirical - pd) < 5e-3


def test_price_multiplier_positive():
    returns = np.array([-2.0, 0.0, 1.5])
    multipliers = sampler.price_multiplier(returns)
    assert np.all(multipliers > 0.0)

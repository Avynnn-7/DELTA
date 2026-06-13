import numpy as np
from scipy.special import stdtr

from engine.cascade import convergence, loop, loss, sampler, simulation, variance_reduction
from engine.dependence import vasicek
from engine.numerics import rng

BASE_PRICES = np.array([1.0])
LOADINGS = np.array([0.5])
NU_COPULA = 8.0
MU = np.array([0.0])
SIGMA = np.array([0.3])
NU_MARGINAL = np.array([10.0])
ASSET_INDEX = np.zeros(6, dtype=int)
QUANTITY = np.ones(6)
THRESHOLD = np.full(6, 0.9)
DEBT = np.linspace(0.5, 0.85, 6)
SLIP = np.full(6, 0.08)


def run_loss(z, epsilon, mixing):
    multipliers = sampler.price_shock(z, epsilon, mixing, LOADINGS, NU_COPULA, MU, SIGMA, NU_MARGINAL)
    prices = BASE_PRICES * multipliers
    liquidated, liquidation_price = loop.run_cascade(
        prices, ASSET_INDEX, QUANTITY, THRESHOLD, DEBT, SLIP
    )
    total, _ = loss.scenario_loss(liquidated, liquidation_price, QUANTITY, DEBT, SLIP, THRESHOLD)
    return total


def marginal_pd():
    barrier = np.log(DEBT / (THRESHOLD * QUANTITY * BASE_PRICES[0]))
    scale = np.sqrt(NU_MARGINAL / (NU_MARGINAL - 2.0))
    return stdtr(NU_MARGINAL, (barrier - MU) / SIGMA * scale)


PD = marginal_pd()
RHO = np.full(6, LOADINGS[0])
LGD_WEIGHT = SLIP
EAD_WEIGHT = DEBT / THRESHOLD


def test_control_variate_unbiased_and_reduces_variance():
    generator = rng.generator(seed=60)
    n = 200000
    z, epsilon, mixing = sampler.draw_factors(generator, n, 1, NU_COPULA)
    losses = run_loss(z, epsilon, mixing)
    control = variance_reduction.vasicek_conditional_loss(z, PD, RHO, LGD_WEIGHT, EAD_WEIGHT)
    control_mean = variance_reduction.vasicek_expected_loss(PD, RHO, LGD_WEIGHT, EAD_WEIGHT)
    adjusted, coefficient = variance_reduction.control_variate_estimator(losses, control, control_mean)
    assert abs(adjusted.mean() - losses.mean()) < 1e-3
    assert adjusted.var() < losses.var()
    assert coefficient > 0.0


def test_antithetic_unbiased_and_reduces_variance():
    generator = rng.generator(seed=61)
    n = 100000
    z, epsilon, mixing = sampler.draw_factors(generator, n, 1, NU_COPULA)
    primary = run_loss(z, epsilon, mixing)
    z_anti, epsilon_anti = variance_reduction.antithetic_factors(z, epsilon)
    antithetic = run_loss(z_anti, epsilon_anti, mixing)
    paired = variance_reduction.antithetic_average(primary, antithetic)
    assert abs(paired.mean() - primary.mean()) < 3.0 * convergence.standard_error(primary)
    assert paired.var() < primary.var()


def test_importance_sampling_unbiased_tail():
    n = 200000
    generator = rng.generator(seed=62)
    z_is, likelihood_ratio = variance_reduction.exponential_tilt(generator, -1.0, n)
    epsilon_is = rng.standard_normal(generator, size=(n, 1))
    mixing_is = generator.standard_gamma(NU_COPULA / 2.0, size=n) * 2.0
    losses_is = run_loss(z_is, epsilon_is, mixing_is)

    crude_generator = rng.generator(seed=63)
    z, epsilon, mixing = sampler.draw_factors(crude_generator, n, 1, NU_COPULA)
    crude = run_loss(z, epsilon, mixing)
    level = float(np.quantile(crude, 0.95))
    crude_probability = convergence.tail_probability(crude, level)

    indicator = (losses_is > level).astype(float)
    estimate, _ = variance_reduction.importance_sampling_estimate(indicator, likelihood_ratio)
    assert abs(estimate - crude_probability) < 1.5e-2


def test_conditional_monte_carlo_matches_analytic():
    generator = rng.generator(seed=64)
    n = 200000
    z, _, _ = sampler.draw_factors(generator, n, 1, NU_COPULA)
    estimate, error = variance_reduction.conditional_monte_carlo_estimate(
        z, PD, RHO, LGD_WEIGHT, EAD_WEIGHT
    )
    analytic = variance_reduction.vasicek_expected_loss(PD, RHO, LGD_WEIGHT, EAD_WEIGHT)
    assert abs(estimate - analytic) < 4.0 * error


def test_sobol_qmc_consistent_mean():
    z_q, epsilon_q, mixing_q = variance_reduction.sobol_factors(1, 4096, NU_COPULA, seed=65)
    losses_q = run_loss(z_q, epsilon_q, mixing_q)
    generator = rng.generator(seed=66)
    z, epsilon, mixing = sampler.draw_factors(generator, 4096, 1, NU_COPULA)
    crude = run_loss(z, epsilon, mixing)
    assert abs(losses_q.mean() - crude.mean()) < 2e-2


def test_homogeneous_default_fraction_matches_vasicek():
    d = 500
    rho = 0.4
    sigma = 0.3
    nu_marginal = 10.0
    nu_copula = 1.0e6
    threshold = 0.9
    debt = 0.7
    barrier = np.log(debt / threshold)
    scale = np.sqrt(nu_marginal / (nu_marginal - 2.0))
    pd = float(stdtr(nu_marginal, barrier / sigma * scale))

    loadings = np.full(d, rho)
    asset_index = np.arange(d)
    quantity = np.ones(d)
    thresholds = np.full(d, threshold)
    debts = np.full(d, debt)
    slip = np.zeros(d)
    base = np.ones(d)

    generator = rng.generator(seed=67)
    n = 20000
    z, epsilon, mixing = sampler.draw_factors(generator, n, d, nu_copula)
    multipliers = sampler.price_shock(
        z, epsilon, mixing, loadings, nu_copula, np.zeros(d), np.full(d, sigma), np.full(d, nu_marginal)
    )
    prices = base * multipliers
    liquidated, _ = loop.run_cascade(prices, asset_index, quantity, thresholds, debts, slip, max_rounds=1)
    fraction = liquidated.mean(axis=1)

    assert abs(fraction.mean() - pd) < 5e-3
    for x in (0.05, 0.1, 0.2):
        empirical = float(np.mean(fraction <= x))
        analytic = float(vasicek.loss_cdf(x, pd, rho))
        assert abs(empirical - analytic) < 3e-2


def test_simulation_reproducible():
    arguments = (
        BASE_PRICES, LOADINGS, NU_COPULA, MU, SIGMA, NU_MARGINAL,
        ASSET_INDEX, QUANTITY, THRESHOLD, DEBT, SLIP, 50000,
    )
    first = simulation.simulate(rng.generator(seed=70), *arguments)
    second = simulation.simulate(rng.generator(seed=70), *arguments)
    np.testing.assert_array_equal(first["loss"], second["loss"])


def test_simulation_substreams_independent():
    generators = rng.substreams(seed=71, count=2)
    arguments = (
        BASE_PRICES, LOADINGS, NU_COPULA, MU, SIGMA, NU_MARGINAL,
        ASSET_INDEX, QUANTITY, THRESHOLD, DEBT, SLIP, 50000,
    )
    first = simulation.simulate(generators[0], *arguments)
    second = simulation.simulate(generators[1], *arguments)
    assert not np.array_equal(first["loss"], second["loss"])

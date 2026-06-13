import numpy as np
from scipy import stats

from engine.risk import allocation, estimators


def test_var_estimator_order_statistic():
    losses = np.arange(1.0, 101.0)
    estimate = estimators.var_estimator(losses, 0.95)
    assert estimate == 95.0


def test_es_estimator_tail_average():
    losses = np.arange(1.0, 101.0)
    estimate = estimators.es_estimator(losses, 0.95)
    assert np.isclose(estimate, np.mean(np.arange(96.0, 101.0)))


def test_var_estimator_consistency():
    generator = np.random.default_rng(10)
    losses = generator.standard_normal(2000000)
    estimate = estimators.var_estimator(losses, 0.99)
    assert abs(estimate - stats.norm.ppf(0.99)) < 1e-2


def test_var_standard_error_decays():
    generator = np.random.default_rng(11)
    base = generator.standard_normal(800000)
    se_small = estimators.var_standard_error(base[:50000], 0.95)
    se_large = estimators.var_standard_error(base[:200000], 0.95)
    assert se_small > se_large
    assert abs(se_small / se_large - 2.0) < 0.3


def test_var_asymptotic_normality():
    alpha = 0.95
    n = 20000
    generators = np.random.default_rng(12)
    true_var = stats.norm.ppf(alpha)
    density = stats.norm.pdf(true_var)
    asymptotic_sd = np.sqrt(alpha * (1.0 - alpha) / n) / density
    estimates = np.array(
        [estimators.var_estimator(generators.standard_normal(n), alpha) for _ in range(400)]
    )
    standardized = (estimates - true_var) / asymptotic_sd
    assert abs(standardized.mean()) < 0.1
    assert abs(standardized.std() - 1.0) < 0.15


def test_weighted_es_matches_unweighted_uniform():
    generator = np.random.default_rng(13)
    losses = generator.standard_normal(200000)
    weights = np.ones_like(losses)
    weighted = estimators.weighted_es_estimator(losses, weights, 0.99)
    unweighted = estimators.es_estimator(losses, 0.99)
    assert abs(weighted - unweighted) < 1e-2


def test_euler_additivity():
    generator = np.random.default_rng(14)
    n = 400000
    d = 4
    common = generator.standard_normal((n, 1))
    idiosyncratic = generator.standard_normal((n, d))
    position_losses = np.maximum(0.6 * common + 0.4 * idiosyncratic, 0.0)
    alpha = 0.95
    contributions = allocation.es_contributions(position_losses, alpha)
    portfolio = position_losses.sum(axis=1)
    es = estimators.es_estimator(portfolio, alpha)
    tail_es = portfolio[portfolio >= estimators.var_estimator(portfolio, alpha)].mean()
    assert abs(allocation.euler_total(contributions) - tail_es) < 1e-6
    assert abs(allocation.euler_total(contributions) - es) < 5e-2


def test_concentration_ranking_orders_by_contribution():
    contributions = np.array([0.1, 0.5, 0.3])
    ranking = allocation.concentration_ranking(contributions)
    assert list(ranking) == [1, 2, 0]

import numpy as np
from scipy import stats

from engine.risk import backtest


def test_kupiec_accepts_correct_coverage():
    alpha = 0.99
    generator = np.random.default_rng(20)
    hits = generator.random(50000) < (1.0 - alpha)
    statistic, p_value = backtest.kupiec_pof(hits, alpha)
    assert p_value > 0.05


def test_kupiec_rejects_excess_exceedances():
    alpha = 0.99
    generator = np.random.default_rng(21)
    hits = generator.random(50000) < 0.05
    statistic, p_value = backtest.kupiec_pof(hits, alpha)
    assert p_value < 0.01


def test_christoffersen_accepts_independent_hits():
    alpha = 0.99
    generator = np.random.default_rng(22)
    hits = generator.random(50000) < (1.0 - alpha)
    statistic, p_value = backtest.christoffersen_conditional_coverage(hits, alpha)
    assert p_value > 0.05


def test_christoffersen_rejects_clustered_hits():
    alpha = 0.99
    block = np.concatenate([np.ones(40), np.zeros(960)])
    hits = np.tile(block, 50).astype(bool)
    statistic, p_value = backtest.christoffersen_independence(hits)
    assert p_value < 0.01


def test_acerbi_szekely_near_zero_under_correct_model():
    alpha = 0.95
    generator = np.random.default_rng(23)
    losses = generator.standard_normal(200000)
    var = stats.norm.ppf(alpha)
    es = stats.norm.pdf(var) / (1.0 - alpha)
    z2 = backtest.acerbi_szekely_z2(losses, np.full_like(losses, var), np.full_like(losses, es), alpha)
    assert abs(z2) < 0.05


def test_acerbi_szekely_flags_underestimated_es():
    alpha = 0.95
    generator = np.random.default_rng(24)
    losses = generator.standard_normal(200000)
    var = stats.norm.ppf(alpha)
    es_true = stats.norm.pdf(var) / (1.0 - alpha)
    z2 = backtest.acerbi_szekely_z2(
        losses, np.full_like(losses, var), np.full_like(losses, 0.5 * es_true), alpha
    )
    assert z2 > 0.5


def test_fissler_ziegel_minimized_at_truth():
    alpha = 0.95
    generator = np.random.default_rng(25)
    losses = generator.standard_normal(500000)
    var = stats.norm.ppf(alpha)
    es = stats.norm.pdf(var) / (1.0 - alpha)
    truth = backtest.fissler_ziegel_score(losses, var, es, alpha)
    high_var = backtest.fissler_ziegel_score(losses, var + 0.5, es, alpha)
    low_var = backtest.fissler_ziegel_score(losses, var - 0.5, es, alpha)
    high_es = backtest.fissler_ziegel_score(losses, var, es + 0.5, alpha)
    low_es = backtest.fissler_ziegel_score(losses, var, es - 0.5, alpha)
    assert truth < high_var
    assert truth < low_var
    assert truth < high_es
    assert truth < low_es


def test_exceedances_indicator():
    losses = np.array([0.5, 1.5, 2.5])
    hits = backtest.exceedances(losses, 1.0)
    assert list(hits) == [False, True, True]

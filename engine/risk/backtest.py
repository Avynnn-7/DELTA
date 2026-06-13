from __future__ import annotations

import numpy as np
from scipy.special import xlogy

from engine.numerics import special


def exceedances(losses, value_at_risk):
    return np.asarray(losses, dtype=float) >= np.asarray(value_at_risk, dtype=float)


def kupiec_pof(hits, alpha):
    hits = np.asarray(hits, dtype=bool)
    n = hits.shape[0]
    x = int(hits.sum())
    p = 1.0 - alpha
    pi_hat = x / n if n > 0 else 0.0
    log_null = xlogy(n - x, 1.0 - p) + xlogy(x, p)
    log_alt = xlogy(n - x, 1.0 - pi_hat) + xlogy(x, pi_hat)
    statistic = -2.0 * (log_null - log_alt)
    p_value = 1.0 - special.chi2_cdf(statistic, 1)
    return float(statistic), float(p_value)


def christoffersen_independence(hits):
    hits = np.asarray(hits, dtype=int)
    transitions = np.zeros((2, 2), dtype=float)
    for previous, current in zip(hits[:-1], hits[1:]):
        transitions[previous, current] += 1.0
    n00, n01 = transitions[0, 0], transitions[0, 1]
    n10, n11 = transitions[1, 0], transitions[1, 1]
    pi_01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0.0
    pi_11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)
    log_alt = (
        xlogy(n00, 1.0 - pi_01)
        + xlogy(n01, pi_01)
        + xlogy(n10, 1.0 - pi_11)
        + xlogy(n11, pi_11)
    )
    log_null = xlogy(n00 + n10, 1.0 - pi) + xlogy(n01 + n11, pi)
    statistic = -2.0 * (log_null - log_alt)
    p_value = 1.0 - special.chi2_cdf(statistic, 1)
    return float(statistic), float(p_value)


def christoffersen_conditional_coverage(hits, alpha):
    pof_statistic, _ = kupiec_pof(hits, alpha)
    independence_statistic, _ = christoffersen_independence(hits)
    statistic = pof_statistic + independence_statistic
    p_value = 1.0 - special.chi2_cdf(statistic, 2)
    return float(statistic), float(p_value)


def acerbi_szekely_z2(losses, value_at_risk, expected_shortfall, alpha):
    losses = np.asarray(losses, dtype=float)
    value_at_risk = np.asarray(value_at_risk, dtype=float)
    expected_shortfall = np.asarray(expected_shortfall, dtype=float)
    n = losses.shape[0]
    beta = 1.0 - alpha
    hits = losses >= value_at_risk
    contributions = hits * losses / expected_shortfall
    return float(contributions.sum() / (n * beta) - 1.0)


def fissler_ziegel_score(losses, value_at_risk, expected_shortfall, alpha):
    losses = np.asarray(losses, dtype=float)
    value_at_risk = np.asarray(value_at_risk, dtype=float)
    expected_shortfall = np.asarray(expected_shortfall, dtype=float)
    beta = 1.0 - alpha
    hits = losses >= value_at_risk
    tail_term = hits * (losses - value_at_risk) / (beta * expected_shortfall)
    score = tail_term + value_at_risk / expected_shortfall + np.log(expected_shortfall) - 1.0
    return float(score.mean())

from __future__ import annotations

import numpy as np

from engine.risk.estimators import var_estimator


def es_contributions(position_losses, alpha):
    position_losses = np.asarray(position_losses, dtype=float)
    portfolio = position_losses.sum(axis=1)
    var = var_estimator(portfolio, alpha)
    tail = portfolio >= var
    if not tail.any():
        return np.zeros(position_losses.shape[1])
    return position_losses[tail].mean(axis=0)


def euler_total(contributions):
    return float(np.sum(contributions))


def concentration_ranking(contributions):
    contributions = np.asarray(contributions, dtype=float)
    return np.argsort(contributions)[::-1]

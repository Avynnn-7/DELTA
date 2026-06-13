from __future__ import annotations

import numpy as np


def loss_given_default(slip, threshold):
    recovery = np.minimum(1.0, (1.0 - np.asarray(slip, dtype=float)) / np.asarray(threshold, dtype=float))
    return 1.0 - recovery


def scenario_loss(liquidated, liquidation_price, quantity, debt, slip, threshold):
    liquidated = np.asarray(liquidated, dtype=float)
    quantity = np.asarray(quantity, dtype=float)
    debt = np.asarray(debt, dtype=float)
    slip = np.asarray(slip, dtype=float)

    lgd = loss_given_default(slip, threshold)
    credit_loss = liquidated * (lgd * debt)
    collateral_value = quantity * np.asarray(liquidation_price, dtype=float)
    slippage_cost = liquidated * collateral_value * slip
    per_position = credit_loss + slippage_cost
    return per_position.sum(axis=1), per_position

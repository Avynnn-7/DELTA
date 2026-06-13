from __future__ import annotations

import numpy as np

from engine.structural.dtl import health_factor


def run_cascade(prices, asset_index, quantity, threshold, debt, slip, max_rounds=None):
    prices = np.array(prices, dtype=float, copy=True)
    asset_index = np.asarray(asset_index, dtype=int)
    quantity = np.asarray(quantity, dtype=float)
    threshold = np.asarray(threshold, dtype=float)
    debt = np.asarray(debt, dtype=float)
    slip = np.asarray(slip, dtype=float)

    n_samples = prices.shape[0]
    n_assets = prices.shape[1]
    n_positions = asset_index.shape[0]
    columns = [np.nonzero(asset_index == a)[0] for a in range(n_assets)]

    liquidated = np.zeros((n_samples, n_positions), dtype=bool)
    liquidation_price = np.zeros((n_samples, n_positions), dtype=float)
    rounds = n_positions if max_rounds is None else max_rounds

    for _ in range(rounds):
        collateral_price = prices[:, asset_index]
        health = health_factor(quantity * collateral_price, debt, threshold)
        new_liquidation = (health <= 1.0) & ~liquidated
        if not new_liquidation.any():
            break
        liquidation_price = np.where(new_liquidation, collateral_price, liquidation_price)
        liquidated |= new_liquidation
        retained = np.where(new_liquidation, 1.0 - slip, 1.0)
        factor = np.ones((n_samples, n_assets), dtype=float)
        for a in range(n_assets):
            cols = columns[a]
            if cols.size:
                factor[:, a] = np.prod(retained[:, cols], axis=1)
        prices *= factor

    return liquidated, liquidation_price

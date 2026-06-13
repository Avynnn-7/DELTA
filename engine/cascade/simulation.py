from __future__ import annotations

import numpy as np

from engine.cascade import loop, loss, sampler


def simulate(
    generator,
    base_prices,
    loadings,
    nu,
    mu,
    sigma,
    nu_marginal,
    asset_index,
    quantity,
    threshold,
    debt,
    slip,
    n_samples,
    max_rounds=None,
):
    base_prices = np.asarray(base_prices, dtype=float)
    z, epsilon, mixing = sampler.draw_factors(generator, n_samples, base_prices.shape[0], nu)
    multipliers = sampler.price_shock(z, epsilon, mixing, loadings, nu, mu, sigma, nu_marginal)
    prices = base_prices * multipliers
    liquidated, liquidation_price = loop.run_cascade(
        prices, asset_index, quantity, threshold, debt, slip, max_rounds
    )
    total, per_position = loss.scenario_loss(
        liquidated, liquidation_price, quantity, debt, slip, threshold
    )
    return {
        "loss": total,
        "position_loss": per_position,
        "common_factor": z,
        "liquidated": liquidated,
    }

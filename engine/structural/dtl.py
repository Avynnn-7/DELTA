from __future__ import annotations

import numpy as np

from engine.numerics import normal


def health_factor(collateral, debt, liquidation_threshold):
    return liquidation_threshold * np.asarray(collateral, dtype=float) / np.asarray(debt, dtype=float)


def interest_adjusted_drift(drift, borrow_rate):
    return drift - borrow_rate


def distance_to_liquidation(health, drift, sigma, horizon):
    health = np.asarray(health, dtype=float)
    horizon = np.asarray(horizon, dtype=float)
    return (np.log(health) + (drift - 0.5 * sigma**2) * horizon) / (sigma * np.sqrt(horizon))


def probability_of_liquidation(health, drift, sigma, horizon):
    return normal.cdf(-distance_to_liquidation(health, drift, sigma, horizon))


def drop_to_liquidation(health):
    return 1.0 - 1.0 / np.asarray(health, dtype=float)


def term_structure(health, drift, sigma, horizons):
    horizons = np.asarray(horizons, dtype=float)
    return probability_of_liquidation(health, drift, sigma, horizons)

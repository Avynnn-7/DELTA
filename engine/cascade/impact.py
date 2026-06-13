from __future__ import annotations

import numpy as np


def square_root_slippage(quantity, volume, sigma_window, eta):
    quantity = np.asarray(quantity, dtype=float)
    raw = eta * np.asarray(sigma_window, dtype=float) * np.sqrt(quantity / np.asarray(volume, dtype=float))
    return np.minimum(raw, 1.0)


def kyle_linear_slippage(quantity, kyle_lambda, price):
    quantity = np.asarray(quantity, dtype=float)
    raw = np.asarray(kyle_lambda, dtype=float) * quantity / np.asarray(price, dtype=float)
    return np.minimum(raw, 1.0)

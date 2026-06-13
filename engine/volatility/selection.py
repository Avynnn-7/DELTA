from __future__ import annotations

import numpy as np


def aic(loglik, num_params):
    return 2.0 * num_params - 2.0 * loglik


def bic(loglik, num_params, num_obs):
    return num_params * np.log(num_obs) - 2.0 * loglik


def qlike(realized, forecast):
    ratio = np.asarray(realized, dtype=float) / np.asarray(forecast, dtype=float)
    return float(np.mean(ratio - np.log(ratio) - 1.0))


def mse(realized, forecast):
    diff = np.asarray(realized, dtype=float) - np.asarray(forecast, dtype=float)
    return float(np.mean(diff**2))

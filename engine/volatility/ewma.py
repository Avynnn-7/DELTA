from __future__ import annotations

import numpy as np

RISKMETRICS_LAMBDA = 0.94


def ewma_variance(returns, decay=RISKMETRICS_LAMBDA, initial=None):
    if not 0.0 < decay < 1.0:
        raise ValueError("decay must lie in (0, 1)")
    r = np.asarray(returns, dtype=float)
    n = r.shape[0]
    variances = np.empty(n + 1, dtype=float)
    variances[0] = float(np.mean(r**2)) if initial is None else float(initial)
    for t in range(n):
        variances[t + 1] = decay * variances[t] + (1.0 - decay) * r[t] ** 2
    return variances

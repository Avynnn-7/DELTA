from __future__ import annotations

import numpy as np
from scipy import optimize as _opt


def minimize(objective, x0, method="Nelder-Mead", max_iter=20000, tol=1e-10):
    x0 = np.asarray(x0, dtype=float)
    if method == "Nelder-Mead":
        options = {"maxiter": max_iter, "maxfev": max_iter, "xatol": tol, "fatol": tol}
    else:
        options = {"maxiter": max_iter, "gtol": tol}
    result = _opt.minimize(objective, x0, method=method, options=options)
    return result.x, float(result.fun), bool(result.success)


def brentq(objective, lower, upper, tol=1e-12, max_iter=200):
    return float(_opt.brentq(objective, lower, upper, xtol=tol, maxiter=max_iter))

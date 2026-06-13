from __future__ import annotations

import numpy as np
from scipy.special import expit, gammaln

from engine.numerics.optimize import minimize
from engine.volatility import garch as _g

_LOG_2PI = float(np.log(2.0 * np.pi))
_MODELS = ("garch", "gjr", "egarch")
_DISTS = ("normal", "t")


def gbm_mle(returns, unbiased=False):
    r = np.asarray(returns, dtype=float)
    n = r.shape[0]
    if n < 2:
        raise ValueError("gbm_mle requires at least two returns")
    mu = float(r.mean())
    divisor = n - 1 if unbiased else n
    sigma2 = float(np.sum((r - mu) ** 2) / divisor)
    return mu, sigma2


def _normal_loglik(eps, sigma2):
    return -0.5 * np.sum(_LOG_2PI + np.log(sigma2) + eps**2 / sigma2)


def _student_t_loglik(eps, sigma2, nu):
    z2 = eps**2 / (sigma2 * (nu - 2.0))
    constant = gammaln((nu + 1.0) / 2.0) - gammaln(nu / 2.0) - 0.5 * np.log(np.pi * (nu - 2.0))
    return float(np.sum(constant - 0.5 * np.log(sigma2) - 0.5 * (nu + 1.0) * np.log1p(z2)))


def _softmax3(a, b):
    raw = np.array([a, b, 0.0])
    shifted = raw - raw.max()
    weights = np.exp(shifted)
    return weights / weights.sum()


def _unpack(model, dist, theta):
    if dist == "t":
        nu = 2.0 + np.exp(theta[-1])
        head = theta[:-1]
    else:
        nu = None
        head = theta
    if model == "garch":
        omega = np.exp(head[0])
        persistence = expit(head[1])
        weight = expit(head[2])
        alpha = persistence * weight
        beta = persistence * (1.0 - weight)
        return {"omega": omega, "alpha": alpha, "beta": beta, "nu": nu}
    if model == "gjr":
        omega = np.exp(head[0])
        persistence = expit(head[1])
        parts = _softmax3(head[2], head[3]) * persistence
        return {
            "omega": omega,
            "alpha": parts[0],
            "gamma": 2.0 * parts[1],
            "beta": parts[2],
            "nu": nu,
        }
    omega = head[0]
    alpha = head[1]
    gamma = head[2]
    beta = np.tanh(head[3])
    return {"omega": omega, "alpha": alpha, "gamma": gamma, "beta": beta, "nu": nu}


def _conditional_variance(model, dist, params, eps):
    if model == "garch":
        persistence = _g.garch_persistence(params["alpha"], params["beta"])
        seed = _g.long_run_variance(params["omega"], persistence)
        return _g.garch_variance(eps, params["omega"], params["alpha"], params["beta"], seed)
    if model == "gjr":
        persistence = _g.gjr_persistence(params["alpha"], params["gamma"], params["beta"])
        seed = _g.long_run_variance(params["omega"], persistence)
        return _g.gjr_variance(
            eps, params["omega"], params["alpha"], params["gamma"], params["beta"], seed
        )
    if dist == "t":
        expected_abs = _g.expected_abs_standard_t(params["nu"])
    else:
        expected_abs = _g.expected_abs_normal()
    seed = params["omega"] / (1.0 - params["beta"])
    return _g.egarch_variance(
        eps, params["omega"], params["alpha"], params["gamma"], params["beta"], expected_abs, seed
    )


def _loglik(model, dist, theta, eps):
    params = _unpack(model, dist, theta)
    sigma2 = _conditional_variance(model, dist, params, eps)
    if not np.all(np.isfinite(sigma2)) or np.any(sigma2 <= 0.0):
        return -np.inf
    if dist == "t":
        return _student_t_loglik(eps, sigma2, params["nu"])
    return float(_normal_loglik(eps, sigma2))


def _initial_theta(model, dist, variance):
    if model == "garch":
        head = [np.log(variance * 0.05), 0.0, np.log(0.05 / 0.90)]
    elif model == "gjr":
        head = [np.log(variance * 0.05), 0.0, 0.0, 0.0]
    else:
        head = [np.log(variance) * 0.05, 0.05, 0.0, np.arctanh(0.95)]
    if dist == "t":
        head = head + [np.log(6.0)]
    return np.array(head, dtype=float)


def _num_params(model, dist):
    base = 1 + (3 if model == "garch" else 4)
    return base + (1 if dist == "t" else 0)


def fit_garch(returns, model="garch", dist="normal", max_iter=20000):
    if model not in _MODELS:
        raise ValueError(f"unknown model: {model!r}")
    if dist not in _DISTS:
        raise ValueError(f"unknown innovation distribution: {dist!r}")
    r = np.asarray(returns, dtype=float)
    if r.shape[0] < 10:
        raise ValueError("fit_garch requires at least ten returns")
    mu = float(r.mean())
    eps = r - mu
    variance = float(np.var(eps))
    theta0 = _initial_theta(model, dist, variance)

    def objective(theta):
        value = _loglik(model, dist, theta, eps)
        return np.inf if not np.isfinite(value) else -value

    theta, neg_loglik, _ = minimize(objective, theta0, max_iter=max_iter)
    params = _unpack(model, dist, theta)
    sigma2 = _conditional_variance(model, dist, params, eps)
    result = {
        "model": model,
        "dist": dist,
        "mu": mu,
        "omega": float(params["omega"]),
        "alpha": float(params["alpha"]),
        "beta": float(params["beta"]),
        "conditional_variance": sigma2,
        "loglik": -neg_loglik,
        "num_params": _num_params(model, dist),
        "num_obs": r.shape[0],
    }
    if "gamma" in params and params["gamma"] is not None:
        result["gamma"] = float(params["gamma"])
    if params["nu"] is not None:
        result["nu"] = float(params["nu"])
    if model == "garch":
        result["persistence"] = float(_g.garch_persistence(params["alpha"], params["beta"]))
        result["long_run_variance"] = float(_g.long_run_variance(params["omega"], result["persistence"]))
    elif model == "gjr":
        result["persistence"] = float(
            _g.gjr_persistence(params["alpha"], params["gamma"], params["beta"])
        )
        result["long_run_variance"] = float(_g.long_run_variance(params["omega"], result["persistence"]))
    return result

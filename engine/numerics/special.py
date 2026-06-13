from __future__ import annotations

import numpy as np
from scipy import special as _sp

from . import linalg, normal, rng

_NEG_INF = -np.inf
_POS_INF = np.inf
_PPF_CLIP = 1e-16


def lower_incomplete_gamma(a, x):
    return _sp.gammainc(a, x)


def upper_incomplete_gamma(a, x):
    return _sp.gammaincc(a, x)


def lower_incomplete_gamma_inv(a, p):
    return _sp.gammaincinv(a, p)


def chi2_cdf(x, df):
    x = np.asarray(x, dtype=float)
    return _sp.gammainc(df / 2.0, x / 2.0)


def chi2_ppf(p, df):
    p = np.asarray(p, dtype=float)
    return 2.0 * _sp.gammaincinv(df / 2.0, p)


def _genz_core(lower, upper, chol, w):
    samples, dim = upper.shape
    c00 = chol[0, 0]
    a0 = lower[:, 0]
    b0 = upper[:, 0]
    d_prev = np.where(np.isneginf(a0), 0.0, normal.cdf(a0 / c00))
    e_prev = np.where(np.isposinf(b0), 1.0, normal.cdf(b0 / c00))
    f = e_prev - d_prev
    y = np.empty((samples, dim), dtype=float)
    for i in range(1, dim):
        arg = np.clip(d_prev + w[:, i - 1] * (e_prev - d_prev), _PPF_CLIP, 1.0 - _PPF_CLIP)
        y[:, i - 1] = normal.ppf(arg)
        partial = y[:, :i] @ chol[i, :i]
        cii = chol[i, i]
        ai = lower[:, i]
        bi = upper[:, i]
        d_i = np.where(np.isneginf(ai), 0.0, normal.cdf((ai - partial) / cii))
        e_i = np.where(np.isposinf(bi), 1.0, normal.cdf((bi - partial) / cii))
        f = f * (e_i - d_i)
        d_prev, e_prev = d_i, e_i
    return f


def _limits(upper, lower, dim):
    upper = np.asarray(upper, dtype=float)
    if lower is None:
        lower = np.full(dim, _NEG_INF)
    else:
        lower = np.asarray(lower, dtype=float)
    return upper, lower


def mvn_cdf(upper, corr, lower=None, samples=20000, seed=0):
    corr = np.asarray(corr, dtype=float)
    dim = corr.shape[0]
    upper, lower = _limits(upper, lower, dim)
    if dim == 1:
        lo = 0.0 if np.isneginf(lower[0]) else float(normal.cdf(lower[0]))
        hi = 1.0 if np.isposinf(upper[0]) else float(normal.cdf(upper[0]))
        return hi - lo, 0.0
    chol = linalg.cholesky(corr)
    gen = rng.generator(seed)
    w = rng.uniform_open(gen, size=(samples, dim - 1))
    low = np.broadcast_to(lower, (samples, dim))
    up = np.broadcast_to(upper, (samples, dim))
    f = _genz_core(low, up, chol, w)
    return float(f.mean()), float(f.std(ddof=1) / np.sqrt(samples))


def mvt_cdf(upper, corr, df, lower=None, samples=20000, seed=0):
    corr = np.asarray(corr, dtype=float)
    dim = corr.shape[0]
    upper, lower = _limits(upper, lower, dim)
    if dim == 1:
        lo = 0.0 if np.isneginf(lower[0]) else float(_sp.stdtr(df, lower[0]))
        hi = 1.0 if np.isposinf(upper[0]) else float(_sp.stdtr(df, upper[0]))
        return hi - lo, 0.0
    chol = linalg.cholesky(corr)
    gen = rng.generator(seed)
    radial = gen.standard_gamma(df / 2.0, size=samples) * 2.0
    scale = np.sqrt(radial / df)[:, None]
    up = upper[None, :] * scale
    low = lower[None, :] * scale
    w = rng.uniform_open(gen, size=(samples, dim - 1))
    f = _genz_core(low, up, chol, w)
    return float(f.mean()), float(f.std(ddof=1) / np.sqrt(samples))

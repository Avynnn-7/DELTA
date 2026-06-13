from __future__ import annotations

import numpy as np
from scipy import special as _sp

from .stability import log1mexp

erf = _sp.erf
erfc = _sp.erfc

_INV_SQRT2 = 1.0 / np.sqrt(2.0)
_LOG_2PI = float(np.log(2.0 * np.pi))
_ASYMPTOTIC_LEFT = -25.0

_A = np.array([
    2.5090809287301226727e3,
    3.3430575583588128105e4,
    6.7265770927008700853e4,
    4.5921953931549871457e4,
    1.3731693765509461125e4,
    1.9715909503065514427e3,
    1.3314166789178437745e2,
    3.3871328727963666080e0,
])
_B = np.array([
    5.2264952788528545610e3,
    2.8729085735721942674e4,
    3.9307895800092710610e4,
    2.1213794301586595867e4,
    5.3941960214247511077e3,
    6.8718700749205790830e2,
    4.2313330701600911252e1,
    1.0,
])
_C = np.array([
    7.74545014278341407640e-4,
    2.27238449892691845833e-2,
    2.41780725177450611770e-1,
    1.27045825245236838258e0,
    3.64784832476320460504e0,
    5.76949722146069140550e0,
    4.63033784615654529590e0,
    1.42343711074968357734e0,
])
_D = np.array([
    1.05075007164441684324e-9,
    5.47593808499534494600e-4,
    1.51986665636164571966e-2,
    1.48103976427480074590e-1,
    6.89767334985100004550e-1,
    1.67638483018380384940e0,
    2.05319162663775882187e0,
    1.0,
])
_E = np.array([
    2.01033439929228813265e-7,
    2.71155556874348757815e-5,
    1.24266094738807843860e-3,
    2.65321895265761230930e-2,
    2.96560571828504891230e-1,
    1.78482653991729133580e0,
    5.46378491116411436990e0,
    6.65790464350110377720e0,
])
_F = np.array([
    2.04426310338993978564e-15,
    1.42151175831644588870e-7,
    1.84631831751005468180e-5,
    7.86869131145613259100e-4,
    1.48753612908506148525e-2,
    1.36929880922735805310e-1,
    5.99832206555887937690e-1,
    1.0,
])


def pdf(x):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * x * x) / np.sqrt(2.0 * np.pi)


def cdf(x):
    x = np.asarray(x, dtype=float)
    return 0.5 * erfc(-x * _INV_SQRT2)


def _log_cdf_asymptotic(x):
    t = -x
    inv = 1.0 / (t * t)
    series = inv * (-1.0 + inv * (3.0 + inv * (-15.0 + inv * (105.0 + inv * (-945.0)))))
    log_phi = -0.5 * x * x - 0.5 * _LOG_2PI
    return log_phi - np.log(t) + np.log1p(series)


def _log_cdf_nonpos(x):
    x = np.asarray(x, dtype=float)
    out = np.empty(x.shape, dtype=float)
    direct = x > _ASYMPTOTIC_LEFT
    out[direct] = np.log(0.5 * erfc(-x[direct] * _INV_SQRT2))
    asymptotic = ~direct
    if np.any(asymptotic):
        out[asymptotic] = _log_cdf_asymptotic(x[asymptotic])
    return out


def log_cdf(x):
    x = np.asarray(x, dtype=float)
    scalar = x.ndim == 0
    x = np.atleast_1d(x)
    out = np.empty(x.shape, dtype=float)
    nonpos = x <= 0.0
    out[nonpos] = _log_cdf_nonpos(x[nonpos])
    pos = ~nonpos
    if np.any(pos):
        out[pos] = log1mexp(_log_cdf_nonpos(-x[pos]))
    return out[0] if scalar else out


def ppf(p):
    p = np.asarray(p, dtype=float)
    scalar = p.ndim == 0
    p = np.atleast_1d(p)
    out = np.full(p.shape, np.nan, dtype=float)

    out[p == 0.0] = -np.inf
    out[p == 1.0] = np.inf

    interior = (p > 0.0) & (p < 1.0)
    q = p - 0.5

    central = interior & (np.abs(q) <= 0.425)
    if np.any(central):
        qc = q[central]
        r = 0.180625 - qc * qc
        out[central] = qc * np.polyval(_A, r) / np.polyval(_B, r)

    tail = interior & (np.abs(q) > 0.425)
    if np.any(tail):
        qt = q[tail]
        pt = p[tail]
        r0 = np.sqrt(-np.log(np.where(qt < 0.0, pt, 1.0 - pt)))
        val = np.empty(r0.shape, dtype=float)

        near = r0 <= 5.0
        rn = r0[near] - 1.6
        val[near] = np.polyval(_C, rn) / np.polyval(_D, rn)

        far = ~near
        rf = r0[far] - 5.0
        val[far] = np.polyval(_E, rf) / np.polyval(_F, rf)

        out[tail] = np.where(qt < 0.0, -val, val)

    return out[0] if scalar else out

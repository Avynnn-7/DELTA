import numpy as np
from scipy import stats

from engine.volatility import garch, mle


def test_gbm_mle_divisor_is_n():
    r = np.array([0.01, -0.02, 0.005, -0.001, 0.012, -0.004])
    mu, sigma2 = mle.gbm_mle(r)
    assert np.isclose(mu, r.mean())
    assert np.isclose(sigma2, np.sum((r - r.mean()) ** 2) / r.shape[0])


def test_gbm_mle_unbiased_uses_bessel():
    r = np.array([0.01, -0.02, 0.005, -0.001, 0.012, -0.004])
    _, sigma2 = mle.gbm_mle(r, unbiased=True)
    assert np.isclose(sigma2, np.sum((r - r.mean()) ** 2) / (r.shape[0] - 1))


def _simulate_garch(omega, alpha, beta, n, seed):
    generator = np.random.default_rng(seed)
    z = generator.standard_normal(n)
    sigma2 = np.empty(n)
    eps = np.empty(n)
    sigma2[0] = omega / (1.0 - alpha - beta)
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    return eps


def test_garch_fit_recovers_parameters():
    omega, alpha, beta = 2.0e-6, 0.05, 0.92
    eps = _simulate_garch(omega, alpha, beta, 40000, 0)
    fit = mle.fit_garch(eps, model="garch", dist="normal")
    assert abs(fit["persistence"] - (alpha + beta)) < 0.02
    assert abs(fit["alpha"] - alpha) < 0.02
    assert abs(fit["beta"] - beta) < 0.03
    np.testing.assert_allclose(
        fit["long_run_variance"], omega / (1.0 - alpha - beta), rtol=0.4
    )


def test_garch_loglik_matches_direct_evaluation():
    eps = _simulate_garch(2.0e-6, 0.05, 0.92, 5000, 1)
    fit = mle.fit_garch(eps, model="garch", dist="normal")
    residual = eps - fit["mu"]
    direct = np.sum(stats.norm.logpdf(residual, scale=np.sqrt(fit["conditional_variance"])))
    assert np.isclose(fit["loglik"], direct, rtol=1e-9)


def _simulate_garch_t(omega, alpha, beta, nu, n, seed):
    generator = np.random.default_rng(seed)
    raw = generator.standard_t(nu, size=n)
    z = raw / np.sqrt(nu / (nu - 2.0))
    sigma2 = np.empty(n)
    eps = np.empty(n)
    sigma2[0] = omega / (1.0 - alpha - beta)
    eps[0] = np.sqrt(sigma2[0]) * z[0]
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
        eps[t] = np.sqrt(sigma2[t]) * z[t]
    return eps


def test_garch_t_fit_recovers_degrees_of_freedom():
    omega, alpha, beta, nu = 2.0e-6, 0.06, 0.90, 6.0
    eps = _simulate_garch_t(omega, alpha, beta, nu, 50000, 2)
    fit = mle.fit_garch(eps, model="garch", dist="t")
    assert "nu" in fit
    assert abs(fit["nu"] - nu) < 1.5
    assert abs(fit["persistence"] - (alpha + beta)) < 0.03


def test_gjr_fit_produces_valid_stationary_parameters():
    eps = _simulate_garch(2.0e-6, 0.05, 0.92, 20000, 3)
    fit = mle.fit_garch(eps, model="gjr", dist="normal")
    assert fit["omega"] > 0.0
    assert fit["alpha"] >= 0.0
    assert fit["beta"] >= 0.0
    assert fit["gamma"] >= 0.0
    assert fit["persistence"] < 1.0


def test_egarch_fit_is_finite_and_positive_variance():
    eps = _simulate_garch(2.0e-6, 0.05, 0.92, 20000, 4)
    fit = mle.fit_garch(eps, model="egarch", dist="normal")
    assert np.all(fit["conditional_variance"] > 0.0)
    assert np.isfinite(fit["loglik"])
    assert abs(fit["beta"]) < 1.0

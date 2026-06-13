import numpy as np

from engine.hazard import cir
from validation import probabilistic


def _simulate_cir_survival(kappa, theta, nu, lambda_0, t, n_paths, n_steps, seed):
    dt = t / n_steps
    gen = np.random.default_rng(seed)
    lam = np.full(n_paths, lambda_0)
    integral = np.zeros(n_paths)
    for _ in range(n_steps):
        integral += lam * dt
        drift = kappa * (theta - lam) * dt
        diffusion = nu * np.sqrt(np.maximum(lam, 0.0) * dt) * gen.standard_normal(n_paths)
        lam = np.maximum(lam + drift + diffusion, 0.0)
    return np.mean(np.exp(-integral))


def test_feller_condition():
    assert cir.feller_condition(1.0, 0.05, 0.2)
    assert not cir.feller_condition(0.5, 0.01, 0.3)


def test_riccati_initial_conditions():
    assert np.isclose(cir.riccati_b(0.0, 1.0, 0.2), 0.0)
    assert np.isclose(cir.riccati_a(0.0, 1.0, 0.05, 0.2), 1.0)


def test_survival_at_zero_is_one():
    assert np.isclose(cir.survival(0.0, 1.0, 0.05, 0.2, 0.03), 1.0)


def test_survival_is_valid_curve():
    t = np.linspace(0.01, 10.0, 50)
    s = cir.survival(t, 1.0, 0.05, 0.2, 0.03)
    probabilistic.assert_in_unit_interval(s)
    probabilistic.assert_monotone_non_increasing(s)


def test_affine_survival_matches_monte_carlo():
    kappa, theta, nu, lambda_0, t = 1.5, 0.04, 0.2, 0.03, 3.0
    assert cir.feller_condition(kappa, theta, nu)
    analytic = cir.survival(t, kappa, theta, nu, lambda_0)
    empirical = _simulate_cir_survival(kappa, theta, nu, lambda_0, t, 400000, 3000, 0)
    assert abs(analytic - empirical) < 3e-3


def test_survival_rejects_feller_violation():
    try:
        cir.survival(1.0, 0.5, 0.01, 0.3, 0.05)
    except ValueError:
        return
    raise AssertionError("expected Feller violation to raise")

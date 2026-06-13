import numpy as np
import pytest

from engine.conventions.constants import HOURS_PER_YEAR
from engine.volatility import ewma, realized


def test_realized_variance_is_sum_of_squares():
    r = np.array([0.01, -0.02, 0.005, -0.001])
    assert np.isclose(realized.realized_variance(r), np.sum(r**2))


def test_sample_variance_uses_bessel_divisor():
    r = np.array([0.01, -0.02, 0.005, -0.001, 0.012])
    expected = np.sum((r - r.mean()) ** 2) / (r.shape[0] - 1)
    assert np.isclose(realized.sample_variance(r), expected)


def test_realized_variance_converges_to_integrated_variance():
    sigma = 0.5
    n = 2_000_000
    dt = 1.0 / n
    gen = np.random.default_rng(0)
    increments = sigma * np.sqrt(dt) * gen.standard_normal(n)
    rv = realized.realized_variance(increments)
    np.testing.assert_allclose(rv, sigma**2 * 1.0, rtol=5e-3)


def test_annualization_square_root_rule_24_7():
    r = np.array([0.001, -0.002, 0.0015, -0.0005, 0.0011, -0.0009])
    period_vol = np.sqrt(realized.sample_variance(r))
    assert np.isclose(
        realized.annualized_volatility(r, HOURS_PER_YEAR),
        period_vol * np.sqrt(HOURS_PER_YEAR),
    )
    assert np.isclose(
        realized.annualized_variance(r, HOURS_PER_YEAR),
        realized.sample_variance(r) * HOURS_PER_YEAR,
    )


def test_sample_variance_requires_two_points():
    with pytest.raises(ValueError):
        realized.sample_variance([0.01])


def test_ewma_recursion_matches_definition():
    r = np.array([0.02, -0.01, 0.015, -0.03])
    lam = 0.94
    seed = float(np.mean(r**2))
    variances = ewma.ewma_variance(r, decay=lam, initial=seed)
    expected = np.empty(r.shape[0] + 1)
    expected[0] = seed
    for t in range(r.shape[0]):
        expected[t + 1] = lam * expected[t] + (1.0 - lam) * r[t] ** 2
    np.testing.assert_allclose(variances, expected)


def test_ewma_is_igarch_boundary():
    r = np.array([0.02, -0.01, 0.015, -0.03, 0.005])
    lam = 0.94
    seed = 1e-4
    ewma_path = ewma.ewma_variance(r, decay=lam, initial=seed)
    omega, alpha, beta = 0.0, 1.0 - lam, lam
    igarch = np.empty(r.shape[0] + 1)
    igarch[0] = seed
    for t in range(r.shape[0]):
        igarch[t + 1] = omega + alpha * r[t] ** 2 + beta * igarch[t]
    np.testing.assert_allclose(ewma_path, igarch)


def test_ewma_rejects_invalid_decay():
    with pytest.raises(ValueError):
        ewma.ewma_variance([0.01, 0.02], decay=1.0)

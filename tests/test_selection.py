import numpy as np

from engine.volatility import selection


def test_aic_formula():
    assert np.isclose(selection.aic(loglik=100.0, num_params=4), 2.0 * 4 - 2.0 * 100.0)


def test_bic_formula():
    assert np.isclose(
        selection.bic(loglik=100.0, num_params=4, num_obs=500),
        4 * np.log(500) - 2.0 * 100.0,
    )


def test_qlike_is_zero_for_perfect_forecast():
    forecast = np.array([1e-4, 2e-4, 1.5e-4])
    assert np.isclose(selection.qlike(forecast, forecast), 0.0)


def test_qlike_is_non_negative():
    realized = np.array([1e-4, 3e-4, 2e-4])
    forecast = np.array([1.2e-4, 2.5e-4, 2.2e-4])
    assert selection.qlike(realized, forecast) >= 0.0


def test_qlike_prefers_closer_forecast():
    realized = np.array([1e-4, 2e-4, 3e-4, 2.5e-4])
    good = realized * 1.05
    bad = realized * 2.0
    assert selection.qlike(realized, good) < selection.qlike(realized, bad)


def test_mse_formula():
    realized = np.array([1.0, 2.0, 3.0])
    forecast = np.array([1.5, 2.0, 2.0])
    assert np.isclose(selection.mse(realized, forecast), np.mean((realized - forecast) ** 2))

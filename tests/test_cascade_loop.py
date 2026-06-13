import numpy as np

from engine.cascade import impact, loop, loss


def test_square_root_slippage_formula():
    quantity = np.array([4.0, 9.0])
    volume = np.array([100.0, 100.0])
    sigma_window = np.array([0.2, 0.2])
    eta = 1.0
    slip = impact.square_root_slippage(quantity, volume, sigma_window, eta)
    expected = eta * sigma_window * np.sqrt(quantity / volume)
    np.testing.assert_allclose(slip, expected)


def test_square_root_slippage_capped_at_one():
    slip = impact.square_root_slippage(1e9, 1.0, 1.0, 1.0)
    assert slip == 1.0


def test_kyle_linear_slippage_formula():
    slip = impact.kyle_linear_slippage(2.0, 0.1, 4.0)
    assert np.isclose(slip, 0.05)


def test_cascade_prices_monotone_and_terminates():
    base = np.array([1.0])
    asset_index = np.array([0, 0, 0])
    quantity = np.array([1.0, 1.0, 1.0])
    threshold = np.array([0.8, 0.8, 0.8])
    debt = np.array([0.85, 0.83, 0.81])
    slip = np.array([0.05, 0.05, 0.05])
    prices = np.array([[1.0]])
    liquidated, liquidation_price = loop.run_cascade(
        prices, asset_index, quantity, threshold, debt, slip, max_rounds=3
    )
    assert liquidated.shape == (1, 3)


def test_cascade_contagion_amplifies_independent():
    base = np.array([1.0])
    asset_index = np.array([0, 0])
    quantity = np.array([1.0, 1.0])
    threshold = np.array([0.9, 0.9])
    debt = np.array([0.89, 0.86])
    slip = np.array([0.1, 0.1])

    prices = np.array([[0.98]])
    independent_first = loop.run_cascade(
        prices, asset_index, quantity, threshold, debt, slip, max_rounds=1
    )[0]
    full = loop.run_cascade(
        prices, asset_index, quantity, threshold, debt, slip, max_rounds=2
    )[0]
    assert independent_first.sum() < full.sum()


def test_cascade_round_bound():
    base = np.array([1.0])
    d = 5
    asset_index = np.zeros(d, dtype=int)
    quantity = np.ones(d)
    threshold = np.full(d, 0.95)
    debt = np.array([0.945, 0.90, 0.86, 0.82, 0.78])
    slip = np.full(d, 0.05)
    prices = np.array([[1.0]])
    liquidated, _ = loop.run_cascade(prices, asset_index, quantity, threshold, debt, slip)
    assert liquidated.shape[1] == d


def test_scenario_loss_decomposition():
    liquidated = np.array([[True, False]])
    liquidation_price = np.array([[0.9, 0.0]])
    quantity = np.array([2.0, 1.0])
    debt = np.array([1.5, 1.0])
    slip = np.array([0.1, 0.1])
    threshold = np.array([0.8, 0.8])
    total, per_position = loss.scenario_loss(
        liquidated, liquidation_price, quantity, debt, slip, threshold
    )
    lgd = loss.loss_given_default(slip, threshold)
    expected_credit = lgd[0] * debt[0]
    expected_slippage = quantity[0] * liquidation_price[0, 0] * slip[0]
    assert np.isclose(per_position[0, 0], expected_credit + expected_slippage)
    assert per_position[0, 1] == 0.0
    assert np.isclose(total[0], per_position[0, 0])


def test_loss_given_default_full_recovery():
    slip = np.array([0.0])
    threshold = np.array([0.8])
    lgd = loss.loss_given_default(slip, threshold)
    assert lgd[0] == 0.0

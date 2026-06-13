import numpy as np
import pytest

from engine.conventions import constants, returns, units
from engine.conventions.measures import Measure


def test_hours_per_year_is_8760():
    assert constants.HOURS_PER_YEAR == 8760
    assert constants.PERIODS_PER_YEAR["hourly"] == 8760
    assert constants.PERIODS_PER_YEAR["daily"] == 365


def test_log_return_matches_definition():
    p0 = np.array([100.0, 50.0])
    p1 = np.array([110.0, 55.0])
    expected = np.log(p1 / p0)
    np.testing.assert_allclose(returns.log_return(p1, p0), expected)


def test_periods_per_year_lookup_and_error():
    assert returns.periods_per_year("hourly") == 8760
    with pytest.raises(ValueError):
        returns.periods_per_year("fortnightly")


def test_annualization_square_root_rule():
    var_period = 1e-4
    n = 8760
    ann_var = returns.annualize_variance(var_period, n)
    ann_vol = returns.annualize_volatility(np.sqrt(var_period), n)
    np.testing.assert_allclose(ann_var, var_period * n)
    np.testing.assert_allclose(ann_vol, np.sqrt(var_period) * np.sqrt(n))
    np.testing.assert_allclose(ann_vol**2, ann_var)


def test_volatility_time_product_is_dimensionless():
    variance_time = units.VOLATILITY**2 * units.TIME
    vol_root_time = units.VOLATILITY * units.TIME**units.Fraction(1, 2)
    assert variance_time.is_dimensionless
    assert vol_root_time.is_dimensionless


def test_dimension_algebra():
    assert (units.CURRENCY / units.CURRENCY).is_dimensionless
    assert units.RATE * units.TIME == units.DIMENSIONLESS
    assert not units.CURRENCY.is_dimensionless


def test_measure_tags():
    assert Measure.PHYSICAL.value == "P"
    assert Measure.RISK_NEUTRAL.value == "Q"

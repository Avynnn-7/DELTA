from engine.conventions import units
from validation import dimensional


def test_dtl_argument_is_dimensionless():
    drift_time = units.RATE * units.TIME
    variance_time = units.VOLATILITY**2 * units.TIME
    sigma_root_time = units.VOLATILITY * units.TIME ** units.Fraction(1, 2)
    dimensional.assert_dimensionless(drift_time, "drift*T")
    dimensional.assert_dimensionless(variance_time, "sigma^2*T")
    dimensional.assert_dimensionless(sigma_root_time, "sigma*sqrt(T)")


def test_first_passage_exponent_is_dimensionless():
    exponent = (units.RATE * units.TIME) / (units.VOLATILITY**2 * units.TIME)
    dimensional.assert_dimensionless(exponent * (units.VOLATILITY**2 * units.TIME), "2mb/sigma^2")


def test_health_factor_is_dimensionless():
    ratio = units.CURRENCY / units.CURRENCY
    dimensional.assert_dimensionless(ratio, "ell*C/B")

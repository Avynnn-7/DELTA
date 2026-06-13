import numpy as np
import pytest

from engine.conventions import units
from validation import dimensional, probabilistic


def test_assert_dimensionless_accepts_and_rejects():
    dimensional.assert_dimensionless(units.DIMENSIONLESS)
    dimensional.assert_dimensionless(units.RATE * units.TIME)
    with pytest.raises(ValueError):
        dimensional.assert_dimensionless(units.CURRENCY)


def test_assert_same_dimension():
    dimensional.assert_same_dimension(units.CURRENCY, units.CURRENCY)
    with pytest.raises(ValueError):
        dimensional.assert_same_dimension(units.CURRENCY, units.TIME)


def test_assert_in_unit_interval():
    probabilistic.assert_in_unit_interval([0.0, 0.5, 1.0])
    with pytest.raises(ValueError):
        probabilistic.assert_in_unit_interval([0.5, 1.2])
    with pytest.raises(ValueError):
        probabilistic.assert_in_unit_interval([-0.1, 0.5])


def test_assert_non_negative():
    probabilistic.assert_non_negative([0.0, 1.0, 3.0])
    with pytest.raises(ValueError):
        probabilistic.assert_non_negative([-1.0])


def test_assert_ge_for_es_dominates_var():
    probabilistic.assert_ge(0.08, 0.05, name="expected_shortfall")
    with pytest.raises(ValueError):
        probabilistic.assert_ge(0.04, 0.05, name="expected_shortfall")


def test_monotonicity_assertions():
    probabilistic.assert_monotone_non_decreasing([0.0, 0.1, 0.1, 0.9])
    probabilistic.assert_monotone_non_increasing([1.0, 0.5, 0.5, 0.0])
    with pytest.raises(ValueError):
        probabilistic.assert_monotone_non_decreasing([0.0, 0.2, 0.1])
    with pytest.raises(ValueError):
        probabilistic.assert_monotone_non_increasing([0.0, 0.2, 0.1])

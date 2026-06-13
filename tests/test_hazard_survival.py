import numpy as np

from engine.hazard import survival
from validation import probabilistic


def test_survival_from_cumulative_hazard():
    cum = np.array([0.0, 0.1, 0.5, 1.0])
    np.testing.assert_allclose(survival.survival_from_cumulative_hazard(cum), np.exp(-cum))


def test_default_probability_is_one_minus_survival():
    cum = np.array([0.0, 0.2, 1.0, 3.0])
    np.testing.assert_allclose(
        survival.default_probability(cum), 1.0 - np.exp(-cum)
    )


def test_constant_intensity_is_exponential():
    lam, t = 0.3, np.array([0.0, 1.0, 5.0])
    np.testing.assert_allclose(survival.constant_survival(lam, t), np.exp(-lam * t))
    assert np.isclose(survival.constant_mean_time(lam), 1.0 / lam)


def test_piecewise_cumulative_hazard_matches_definition():
    intensities = np.array([0.1, 0.2, 0.4])
    durations = np.array([0.5, 0.5, 1.0])
    expected = np.cumsum(intensities * durations)
    np.testing.assert_allclose(
        survival.piecewise_cumulative_hazard(intensities, durations), expected
    )


def test_bootstrap_inverts_survival_curve():
    intensities = np.array([0.05, 0.10, 0.20, 0.15])
    durations = np.array([0.25, 0.25, 0.5, 1.0])
    curve = survival.piecewise_survival(intensities, durations)
    recovered = survival.bootstrap_intensities(curve, durations)
    np.testing.assert_allclose(recovered, intensities)


def test_survival_curve_is_valid():
    intensities = np.array([0.05, 0.10, 0.20, 0.15])
    durations = np.array([0.25, 0.25, 0.5, 1.0])
    curve = survival.piecewise_survival(intensities, durations)
    probabilistic.assert_in_unit_interval(curve)
    probabilistic.assert_monotone_non_increasing(curve)

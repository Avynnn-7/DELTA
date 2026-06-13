import numpy as np

from engine.hazard import cox
from engine.numerics import rng


def test_cox_survival_constant_intensity():
    lam = 0.4
    times = np.linspace(0.0, 5.0, 6)
    cum = lam * times
    paths = np.tile(cum, (1000, 1))
    survival = cox.cox_survival(paths)
    np.testing.assert_allclose(survival, np.exp(-cum))


def test_cox_survival_expectation_over_paths():
    times = np.array([1.0])
    gen = np.random.default_rng(0)
    intensities = gen.gamma(shape=2.0, scale=0.5, size=(200000, 1))
    cum = intensities * times
    survival = cox.cox_survival(cum)
    analytic = (1.0 / (1.0 + 0.5)) ** 2.0
    assert abs(survival[0] - analytic) < 5e-3


def test_default_time_constant_intensity_inversion():
    lam = 0.5
    times = np.linspace(0.0, 20.0, 2001)
    cum = lam * times
    threshold = 2.0
    tau = cox.default_time(times, cum, threshold)
    assert np.isclose(tau, threshold / lam, atol=1e-2)


def test_default_time_infinite_when_threshold_exceeds_curve():
    times = np.linspace(0.0, 1.0, 11)
    cum = 0.1 * times
    assert cox.default_time(times, cum, 10.0) == np.inf


def test_sampled_default_times_are_exponential():
    lam = 0.7
    times = np.linspace(0.0, 200.0, 200001)
    cum = lam * times
    gen = rng.generator(3)
    samples = cox.sample_default_times(gen, times, cum, size=200000)
    finite = samples[np.isfinite(samples)]
    assert abs(finite.mean() - 1.0 / lam) < 0.02
    assert abs(np.median(finite) - np.log(2.0) / lam) < 0.02

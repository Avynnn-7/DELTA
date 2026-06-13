import numpy as np

from engine.cascade import convergence
from engine.numerics import rng


def test_standard_error_decays_root_n():
    generator = rng.generator(seed=50)
    base = rng.standard_normal(generator, size=160000)
    se_small = convergence.standard_error(base[:10000])
    se_large = convergence.standard_error(base[:40000])
    ratio = se_small / se_large
    assert abs(ratio - 2.0) < 0.2


def test_running_standard_error_matches_batch():
    generator = rng.generator(seed=51)
    samples = rng.standard_normal(generator, size=5000)
    running = convergence.running_standard_error(samples)
    assert np.isclose(running[-1], convergence.standard_error(samples))


def test_confidence_interval_coverage():
    rng_factors = rng.substreams(seed=52, count=400)
    true_mean = 0.0
    covered = 0
    for generator in rng_factors:
        samples = rng.standard_normal(generator, size=2000)
        low, high = convergence.confidence_interval(samples, level=0.95)
        if low <= true_mean <= high:
            covered += 1
    coverage = covered / len(rng_factors)
    assert abs(coverage - 0.95) < 0.04


def test_tail_probability_and_error():
    generator = rng.generator(seed=53)
    samples = rng.standard_normal(generator, size=200000)
    p = convergence.tail_probability(samples, 1.6448536269514722)
    assert abs(p - 0.05) < 5e-3
    error = convergence.tail_probability_standard_error(samples, 1.6448536269514722)
    assert error > 0.0


def test_mean_estimate_consistency():
    generator = rng.generator(seed=54)
    samples = 3.0 + rng.standard_normal(generator, size=500000)
    assert abs(convergence.mean_estimate(samples) - 3.0) < 1e-2


def test_effective_sample_size():
    ess = convergence.effective_sample_size(4.0, 1.0, 1000)
    assert ess == 4000.0

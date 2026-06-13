import numpy as np

from engine.numerics import normal, rng


def test_generator_is_reproducible():
    a = rng.uniform_open(rng.generator(123), size=1000)
    b = rng.uniform_open(rng.generator(123), size=1000)
    np.testing.assert_array_equal(a, b)


def test_uniform_open_is_in_open_interval():
    u = rng.uniform_open(rng.generator(5), size=100000)
    assert u.min() > 0.0
    assert u.max() < 1.0


def test_substreams_are_reproducible_and_decorrelated():
    streams_a = rng.substreams(99, 3)
    streams_b = rng.substreams(99, 3)
    draws_a = [rng.uniform_open(g, size=5000) for g in streams_a]
    draws_b = [rng.uniform_open(g, size=5000) for g in streams_b]
    for da, db in zip(draws_a, draws_b):
        np.testing.assert_array_equal(da, db)
    corr01 = np.corrcoef(draws_a[0], draws_a[1])[0, 1]
    corr02 = np.corrcoef(draws_a[0], draws_a[2])[0, 1]
    assert abs(corr01) < 0.05
    assert abs(corr02) < 0.05


def test_standard_normal_is_inversion_of_uniform():
    u = rng.uniform_open(rng.generator(42), size=1000)
    z = rng.standard_normal(rng.generator(42), size=1000)
    np.testing.assert_allclose(z, normal.ppf(u), rtol=1e-12)


def test_standard_normal_moments():
    z = rng.standard_normal(rng.generator(2024), size=500000)
    assert abs(z.mean()) < 0.01
    assert abs(z.std() - 1.0) < 0.01

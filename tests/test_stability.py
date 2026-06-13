import numpy as np
import pytest

from engine.numerics.stability import log1mexp


def test_log1mexp_matches_reference():
    mp = pytest.importorskip("mpmath")
    mp.mp.dps = 50
    xs = [-1e-8, -1e-3, -0.5, -np.log(2.0), -1.0, -10.0, -50.0]
    expected = np.array([float(mp.log(mp.mpf(1) - mp.e ** mp.mpf(xi))) for xi in xs])
    np.testing.assert_allclose(log1mexp(np.array(xs)), expected, rtol=1e-12, atol=1e-15)


def test_log1mexp_small_argument_accuracy():
    x = -1e-12
    expected = np.log(-np.expm1(x))
    np.testing.assert_allclose(log1mexp(x), expected, rtol=1e-12)


def test_log1mexp_rejects_positive():
    with pytest.raises(ValueError):
        log1mexp(np.array([0.1]))

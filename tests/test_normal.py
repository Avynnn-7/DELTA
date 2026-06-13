import numpy as np
from scipy import special as sp

from engine.numerics import normal


def test_pdf_matches_formula():
    x = np.linspace(-6.0, 6.0, 101)
    expected = np.exp(-0.5 * x * x) / np.sqrt(2.0 * np.pi)
    np.testing.assert_allclose(normal.pdf(x), expected, rtol=1e-14)


def test_cdf_matches_scipy_ndtr():
    x = np.linspace(-40.0, 40.0, 401)
    np.testing.assert_allclose(normal.cdf(x), sp.ndtr(x), rtol=1e-12, atol=1e-300)


def test_ppf_matches_scipy_ndtri():
    p = np.array([1e-300, 1e-50, 1e-12, 1e-6, 0.01, 0.2, 0.5, 0.8, 0.99, 1 - 1e-12, 1 - 1e-15])
    np.testing.assert_allclose(normal.ppf(p), sp.ndtri(p), rtol=1e-12, atol=1e-12)


def test_ppf_tail_relative_accuracy():
    p = np.array([1e-200, 1e-100, 1e-40, 1e-15])
    got = normal.ppf(p)
    ref = sp.ndtri(p)
    np.testing.assert_allclose(got, ref, rtol=1e-10)


def test_log_cdf_matches_log_ndtr_deep_tail():
    x = np.array([-300.0, -100.0, -40.0, -25.0, -10.0, -1.0, 0.0, 1.0, 10.0, 40.0])
    np.testing.assert_allclose(normal.log_cdf(x), sp.log_ndtr(x), rtol=1e-10, atol=1e-10)


def test_ppf_cdf_roundtrip():
    x = np.linspace(-5.5, 5.5, 111)
    np.testing.assert_allclose(normal.ppf(normal.cdf(x)), x, atol=1e-9)


def test_ppf_boundaries():
    assert normal.ppf(0.0) == -np.inf
    assert normal.ppf(1.0) == np.inf
    assert np.isnan(normal.ppf(-0.1))
    assert np.isnan(normal.ppf(1.1))

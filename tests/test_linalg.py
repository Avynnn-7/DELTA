import numpy as np
import pytest

from engine.numerics import linalg, rng


def test_cholesky_reconstructs_matrix():
    corr = np.array([[1.0, 0.4, 0.2], [0.4, 1.0, 0.5], [0.2, 0.5, 1.0]])
    chol = linalg.cholesky(corr)
    np.testing.assert_allclose(chol @ chol.T, corr, atol=1e-12)
    assert np.allclose(np.triu(chol, 1), 0.0)


def test_cholesky_sampling_reproduces_correlation():
    corr = np.array([[1.0, 0.6], [0.6, 1.0]])
    chol = linalg.cholesky(corr)
    gen = rng.generator(3)
    z = rng.standard_normal(gen, size=(200000, 2))
    x = z @ chol.T
    np.testing.assert_allclose(np.corrcoef(x.T), corr, atol=1e-2)


def test_cholesky_rejects_non_spd():
    bad = np.array([[1.0, 2.0], [2.0, 1.0]])
    with pytest.raises(ValueError):
        linalg.cholesky(bad)


def test_eigenvalue_clip_is_positive_definite():
    indefinite = np.array([[1.0, 0.9, 0.9], [0.9, 1.0, -0.9], [0.9, -0.9, 1.0]])
    repaired = linalg.eigenvalue_clip(indefinite, eps=1e-8)
    values = np.linalg.eigvalsh(repaired)
    assert values.min() >= 1e-8 - 1e-12
    linalg.cholesky(repaired)


def test_nearest_correlation_has_unit_diagonal_and_is_psd():
    approx = np.array([[1.0, 0.9, 0.7], [0.9, 1.0, 0.9], [0.7, 0.9, 1.0]])
    approx = approx + np.array([[0.0, 0.05, -0.1], [0.05, 0.0, 0.08], [-0.1, 0.08, 0.0]])
    result = linalg.nearest_correlation(approx)
    np.testing.assert_allclose(np.diag(result), np.ones(3), atol=1e-10)
    np.testing.assert_allclose(result, result.T, atol=1e-12)
    assert np.linalg.eigvalsh(result).min() >= -1e-8

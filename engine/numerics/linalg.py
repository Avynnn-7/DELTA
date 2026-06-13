from __future__ import annotations

import numpy as np


def cholesky(matrix):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("cholesky requires a square matrix")
    if not np.allclose(matrix, matrix.T, atol=1e-12):
        raise ValueError("cholesky requires a symmetric matrix")
    try:
        return np.linalg.cholesky(matrix)
    except np.linalg.LinAlgError as exc:
        raise ValueError("matrix is not positive definite") from exc


def _project_psd(matrix, eps):
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    values = np.maximum(values, eps)
    return (vectors * values) @ vectors.T


def eigenvalue_clip(matrix, eps=1e-10):
    return _project_psd(np.asarray(matrix, dtype=float), eps)


def nearest_correlation(matrix, max_iter=100, tol=1e-10):
    current = 0.5 * (np.asarray(matrix, dtype=float) + np.asarray(matrix, dtype=float).T)
    dim = current.shape[0]
    diag = np.diag_indices(dim)
    dykstra = np.zeros_like(current)
    previous = current.copy()
    for _ in range(max_iter):
        residual = current - dykstra
        projected = _project_psd(residual, 0.0)
        dykstra = projected - residual
        current = projected.copy()
        current[diag] = 1.0
        denom = np.linalg.norm(previous, "fro")
        if denom == 0.0:
            denom = 1.0
        if np.linalg.norm(current - previous, "fro") / denom < tol:
            break
        previous = current.copy()
    return current

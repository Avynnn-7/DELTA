from __future__ import annotations

import numpy as np


def assert_in_unit_interval(values, name: str = "value", tol: float = 1e-12) -> None:
    array = np.asarray(values, dtype=float)
    if np.any(array < -tol) or np.any(array > 1.0 + tol):
        raise ValueError(f"{name} must lie in [0, 1]")


def assert_non_negative(values, name: str = "value", tol: float = 1e-12) -> None:
    array = np.asarray(values, dtype=float)
    if np.any(array < -tol):
        raise ValueError(f"{name} must be non-negative")


def assert_ge(left, right, name: str = "value", tol: float = 1e-12) -> None:
    left_array = np.asarray(left, dtype=float)
    right_array = np.asarray(right, dtype=float)
    if np.any(left_array < right_array - tol):
        raise ValueError(f"{name} must satisfy left >= right")


def assert_monotone_non_decreasing(values, name: str = "sequence", tol: float = 1e-12) -> None:
    array = np.asarray(values, dtype=float)
    if np.any(np.diff(array) < -tol):
        raise ValueError(f"{name} must be non-decreasing")


def assert_monotone_non_increasing(values, name: str = "sequence", tol: float = 1e-12) -> None:
    array = np.asarray(values, dtype=float)
    if np.any(np.diff(array) > tol):
        raise ValueError(f"{name} must be non-increasing")

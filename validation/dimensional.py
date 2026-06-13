from __future__ import annotations

from engine.conventions.units import Dimension


def assert_dimensionless(dimension: Dimension, name: str = "argument") -> None:
    if not isinstance(dimension, Dimension):
        raise TypeError(f"{name} must carry a Dimension")
    if not dimension.is_dimensionless:
        raise ValueError(f"{name} must be dimensionless, found {dimension!r}")


def assert_same_dimension(left: Dimension, right: Dimension, name: str = "arguments") -> None:
    if left != right:
        raise ValueError(f"{name} must share a dimension, found {left!r} and {right!r}")

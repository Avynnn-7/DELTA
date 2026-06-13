from __future__ import annotations

import numpy as np
from numpy.random import Generator, Philox

from . import normal

_TWO53 = float(1 << 53)


def generator(seed, counter=0) -> Generator:
    return Generator(Philox(key=seed, counter=counter))


def substreams(seed, count: int) -> list[Generator]:
    base = Philox(key=seed)
    return [Generator(base.jumped(i)) for i in range(count)]


def uniform_open(gen: Generator, size=None):
    draws = gen.integers(1, 1 << 53, size=size, dtype=np.uint64)
    return draws.astype(np.float64) / _TWO53


def standard_normal(gen: Generator, size=None):
    return normal.ppf(uniform_open(gen, size=size))

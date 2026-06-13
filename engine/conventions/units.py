from __future__ import annotations

from fractions import Fraction


class Dimension:
    __slots__ = ("time", "currency")

    def __init__(self, time=0, currency=0):
        self.time = Fraction(time)
        self.currency = Fraction(currency)

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(self.time + other.time, self.currency + other.currency)

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(self.time - other.time, self.currency - other.currency)

    def __pow__(self, exponent) -> "Dimension":
        factor = Fraction(exponent)
        return Dimension(self.time * factor, self.currency * factor)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Dimension)
            and self.time == other.time
            and self.currency == other.currency
        )

    def __hash__(self) -> int:
        return hash((self.time, self.currency))

    @property
    def is_dimensionless(self) -> bool:
        return self.time == 0 and self.currency == 0

    def __repr__(self) -> str:
        return f"Dimension(time={self.time}, currency={self.currency})"


DIMENSIONLESS = Dimension()
TIME = Dimension(time=1)
CURRENCY = Dimension(currency=1)
VOLATILITY = Dimension(time=Fraction(-1, 2))
RATE = Dimension(time=-1)
CUMULATIVE_HAZARD = DIMENSIONLESS

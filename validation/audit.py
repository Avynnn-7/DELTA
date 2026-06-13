from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class Limitation:
    identifier: str
    description: str
    locus: str
    response: str


REGISTERED_LIMITATIONS = (
    Limitation(
        "L-1",
        "Gaussian tails understate extremes",
        "structural PD/PL",
        "t-copula tails, EVT de-peg sizing, KMV-style empirical mapping",
    ),
    Limitation(
        "L-COP",
        "Gaussian copula has zero tail dependence",
        "portfolio cascade",
        "t-copula adopted; Gaussian retained only for Vasicek closed form",
    ),
    Limitation(
        "L-IMP",
        "Price-impact kernel fragile; liquidity vanishes in crashes",
        "cascade severity",
        "stress eta; scenario analysis; flagged not hidden",
    ),
    Limitation(
        "L-6",
        "Deterministic recovery",
        "EAD times LGD losses",
        "stochastic recovery extension noted",
    ),
    Limitation(
        "L-7",
        "Oracle latency, MEV, keeper dynamics",
        "liquidation timing",
        "idealized first-passage bound; latency model noted",
    ),
    Limitation(
        "L-V1",
        "Microstructure noise biases realized variance",
        "volatility input",
        "noise-robust realized variance and optimal sampling",
    ),
    Limitation(
        "L-DRIFT",
        "Drift poorly estimable at short horizon",
        "distance-to-default and distance-to-liquidation",
        "set drift to zero conservatively",
    ),
)


@dataclass(frozen=True)
class Assumption:
    identifier: str
    statement: str
    valid_in_crypto: bool
    handled: str


ASSUMPTION_LEDGER = (
    Assumption("A1", "Frictionless continuous trading", False, "price impact; idealization flagged"),
    Assumption("A2", "GBM constant volatility", False, "time-varying volatility estimate"),
    Assumption("A3", "Gaussian, no jumps", False, "t-copula tails, EVT; jump-diffusion future work"),
    Assumption("A4", "Default only at horizon", False, "first-passage barrier"),
    Assumption("A5", "One factor, Gaussian copula", False, "t-copula, multi-factor noted"),
    Assumption("A6", "Deterministic recovery", False, "stochastic-recovery extension noted"),
    Assumption("A7", "Oracle truthful, instant liquidation", False, "latency and MEV idealized bound"),
)


def limitation_registry():
    return MappingProxyType({item.identifier: item for item in REGISTERED_LIMITATIONS})


def assumption_registry():
    return MappingProxyType({item.identifier: item for item in ASSUMPTION_LEDGER})


def assert_limitations_documented():
    for item in REGISTERED_LIMITATIONS:
        if not item.description or not item.response:
            raise ValueError(f"limitation {item.identifier} lacks a documented response")


def assert_assumptions_handled():
    for item in ASSUMPTION_LEDGER:
        if not item.handled:
            raise ValueError(f"assumption {item.identifier} is not handled")

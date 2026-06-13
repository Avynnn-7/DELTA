from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType

import numpy as np

from engine.risk import allocation, estimators, var_es

SCHEMA_VERSION = "1"


def _freeze(array):
    frozen = np.array(array, dtype=float, copy=True)
    frozen.setflags(write=False)
    return frozen


@dataclass(frozen=True)
class EngineArtifacts:
    alpha: float
    position_metrics: MappingProxyType
    survival_curves: MappingProxyType
    loss_distribution: np.ndarray
    loss_histogram: MappingProxyType
    value_at_risk: float
    expected_shortfall: float
    es_contributions: np.ndarray
    diagnostics: MappingProxyType
    metadata: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))


def build_artifacts(
    position_metrics,
    survival_curves,
    loss_distribution,
    position_losses,
    alpha,
    diagnostics,
    metadata=None,
    histogram_bins=50,
):
    losses = _freeze(loss_distribution)
    var = estimators.var_estimator(losses, alpha)
    es = var_es.expected_shortfall_conditional(losses, alpha)
    contributions = _freeze(allocation.es_contributions(position_losses, alpha))
    density, edges = np.histogram(losses, bins=histogram_bins, density=True)
    histogram = MappingProxyType({"edges": _freeze(edges), "density": _freeze(density)})
    frozen_positions = MappingProxyType({k: _freeze(v) for k, v in position_metrics.items()})
    frozen_survival = MappingProxyType({k: _freeze(v) for k, v in survival_curves.items()})
    frozen_diagnostics = MappingProxyType(dict(diagnostics))
    frozen_metadata = MappingProxyType(dict(metadata) if metadata is not None else {})
    return EngineArtifacts(
        alpha=float(alpha),
        position_metrics=frozen_positions,
        survival_curves=frozen_survival,
        loss_distribution=losses,
        loss_histogram=histogram,
        value_at_risk=var,
        expected_shortfall=es,
        es_contributions=contributions,
        diagnostics=frozen_diagnostics,
        metadata=frozen_metadata,
    )


def _scalar(value):
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return value


def serialize(artifacts):
    return {
        "schema_version": SCHEMA_VERSION,
        "alpha": float(artifacts.alpha),
        "value_at_risk": float(artifacts.value_at_risk),
        "expected_shortfall": float(artifacts.expected_shortfall),
        "loss_distribution": np.asarray(artifacts.loss_distribution, dtype=float).tolist(),
        "loss_histogram": {
            "edges": np.asarray(artifacts.loss_histogram["edges"], dtype=float).tolist(),
            "density": np.asarray(artifacts.loss_histogram["density"], dtype=float).tolist(),
        },
        "es_contributions": np.asarray(artifacts.es_contributions, dtype=float).tolist(),
        "position_metrics": {
            key: np.asarray(value, dtype=float).tolist()
            for key, value in artifacts.position_metrics.items()
        },
        "survival_curves": {
            key: np.asarray(value, dtype=float).tolist()
            for key, value in artifacts.survival_curves.items()
        },
        "diagnostics": {key: _scalar(value) for key, value in artifacts.diagnostics.items()},
        "metadata": {key: _scalar(value) for key, value in artifacts.metadata.items()},
    }


def to_json(artifacts, indent=2):
    return json.dumps(serialize(artifacts), indent=indent, sort_keys=True)

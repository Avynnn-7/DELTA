import numpy as np
import pytest

from engine.risk import artifacts


def _build():
    generator = np.random.default_rng(30)
    n = 20000
    position_losses = np.maximum(generator.standard_normal((n, 3)), 0.0)
    loss = position_losses.sum(axis=1)
    position_metrics = {"distance_to_liquidation": np.array([1.2, 0.8, 2.0])}
    survival_curves = {"pegged": np.array([1.0, 0.97, 0.9])}
    diagnostics = {"standard_error": 0.01, "effective_sample_size": 4000.0}
    return artifacts.build_artifacts(
        position_metrics, survival_curves, loss, position_losses, 0.95, diagnostics
    )


def test_artifacts_contains_risk_numbers():
    result = _build()
    assert result.expected_shortfall >= result.value_at_risk
    assert result.es_contributions.shape == (3,)
    assert np.isclose(result.es_contributions.sum(), result.expected_shortfall, atol=5e-2)


def test_artifacts_are_read_only():
    result = _build()
    with pytest.raises(ValueError):
        result.loss_distribution[0] = 0.0
    with pytest.raises(ValueError):
        result.es_contributions[0] = 0.0


def test_artifacts_frozen_dataclass():
    result = _build()
    with pytest.raises(Exception):
        result.value_at_risk = 0.0


def test_artifacts_metadata_mapping_immutable():
    result = _build()
    with pytest.raises(TypeError):
        result.diagnostics["standard_error"] = 1.0

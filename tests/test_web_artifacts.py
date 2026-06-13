import json
from pathlib import Path

import numpy as np
import pytest

from engine.risk import artifacts

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@pytest.fixture(scope="module")
def schema():
    return json.loads((WEB_DIR / "schema.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def built():
    rng = np.random.default_rng(11)
    position_losses = np.maximum(
        rng.standard_normal((20000, 3)) * np.array([1.0, 1.3, 0.8]) + 0.3, 0.0
    )
    loss = position_losses.sum(axis=1)
    position_metrics = {
        "distance_to_liquidation": np.array([1.7, 0.9, 2.2]),
        "first_passage_pl": np.array([0.08, 0.29, 0.03]),
        "terminal_pl": np.array([0.06, 0.22, 0.02]),
    }
    survival_curves = {
        "steth": np.array([1.0, 0.99, 0.97, 0.94]),
        "usdc": np.array([1.0, 0.999, 0.996, 0.991]),
    }
    diagnostics = {"standard_error": 0.003, "effective_sample_size": 9000.0}
    metadata = {"horizon_days": 7, "impact_eta": 1.0}
    return artifacts.build_artifacts(
        position_metrics, survival_curves, loss, position_losses, 0.975, diagnostics, metadata
    )


def _conforms(value, type_spec):
    if isinstance(type_spec, dict):
        if not isinstance(value, dict):
            return False
        return all(_conforms(value.get(k), v) for k, v in type_spec.items())
    if type_spec == "string":
        return isinstance(value, str)
    if type_spec == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_spec == "array<number>":
        return isinstance(value, list) and all(
            isinstance(x, (int, float)) and not isinstance(x, bool) for x in value
        )
    if type_spec == "map<string,array<number>>":
        return isinstance(value, dict) and all(
            isinstance(k, str) and _conforms(v, "array<number>") for k, v in value.items()
        )
    if type_spec == "map<string,number>":
        return isinstance(value, dict) and all(
            isinstance(k, str) and _conforms(v, "number") for k, v in value.items()
        )
    if type_spec == "map<string,scalar>":
        return isinstance(value, dict) and all(
            isinstance(k, str) and isinstance(v, (int, float, str, bool)) for k, v in value.items()
        )
    raise AssertionError(f"unknown type spec {type_spec}")


def test_serialized_artifact_conforms_to_schema(schema, built):
    payload = artifacts.serialize(built)
    for field_name, type_spec in schema["fields"].items():
        assert field_name in payload, f"missing field {field_name}"
        assert _conforms(payload[field_name], type_spec), f"field {field_name} violates schema"


def test_sample_data_file_conforms_to_schema(schema):
    payload = json.loads((WEB_DIR / "data" / "artifacts.json").read_text(encoding="utf-8"))
    for field_name, type_spec in schema["fields"].items():
        assert field_name in payload, f"missing field {field_name}"
        assert _conforms(payload[field_name], type_spec), f"field {field_name} violates schema"


def test_schema_version_matches_engine(schema, built):
    payload = artifacts.serialize(built)
    assert schema["schema_version"] == artifacts.SCHEMA_VERSION
    assert payload["schema_version"] == artifacts.SCHEMA_VERSION


def test_displayed_values_match_engine_exactly(built):
    payload = artifacts.serialize(built)
    assert payload["alpha"] == built.alpha
    assert payload["value_at_risk"] == built.value_at_risk
    assert payload["expected_shortfall"] == built.expected_shortfall
    np.testing.assert_array_equal(payload["es_contributions"], built.es_contributions)
    np.testing.assert_array_equal(
        payload["loss_histogram"]["edges"], built.loss_histogram["edges"]
    )
    np.testing.assert_array_equal(
        payload["loss_histogram"]["density"], built.loss_histogram["density"]
    )
    for key, values in built.position_metrics.items():
        np.testing.assert_array_equal(payload["position_metrics"][key], values)
    for key, values in built.survival_curves.items():
        np.testing.assert_array_equal(payload["survival_curves"][key], values)


def test_each_view_field_present_in_serialized_artifact(schema, built):
    payload = artifacts.serialize(built)
    for view, referenced in schema["views"].items():
        for name in referenced:
            assert name in payload, f"view {view} needs absent field {name}"


def test_histogram_density_dimensions_consistent(built):
    edges = np.asarray(built.loss_histogram["edges"])
    density = np.asarray(built.loss_histogram["density"])
    assert edges.shape[0] == density.shape[0] + 1

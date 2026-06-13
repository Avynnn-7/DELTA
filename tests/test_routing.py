import pytest

from engine.structural.routing import AssetType, RiskModel, route


def test_volatile_routes_to_structural():
    assert route(AssetType.VOLATILE) is RiskModel.STRUCTURAL


def test_pegged_routes_to_hazard():
    assert route(AssetType.PEGGED) is RiskModel.HAZARD


def test_unknown_asset_type_rejected():
    with pytest.raises(ValueError):
        route("volatile")

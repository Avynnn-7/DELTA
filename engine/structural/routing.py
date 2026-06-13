from __future__ import annotations

from enum import Enum


class AssetType(Enum):
    VOLATILE = "volatile"
    PEGGED = "pegged"


class RiskModel(Enum):
    STRUCTURAL = "structural"
    HAZARD = "hazard"


def route(asset_type: AssetType) -> RiskModel:
    if asset_type is AssetType.VOLATILE:
        return RiskModel.STRUCTURAL
    if asset_type is AssetType.PEGGED:
        return RiskModel.HAZARD
    raise ValueError(f"unknown asset type: {asset_type!r}")

import json
import re
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

FORBIDDEN_ENGINE_TOKENS = [
    "engine.",
    "from engine",
    "import engine",
    "validation.",
]

FORBIDDEN_COMPUTATION_TOKENS = [
    "quantile",
    "cholesky",
    "copula",
    "philox",
    "vasicek",
    "cascade",
    "Math.random",
    "histogram(",
    "kendall",
    "garch",
]


def _web_files(suffix):
    return list(WEB_DIR.rglob(f"*{suffix}"))


def test_web_contains_no_python():
    assert _web_files(".py") == []


def test_web_javascript_has_no_engine_imports():
    for path in _web_files(".js"):
        text = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_ENGINE_TOKENS:
            assert token.lower() not in text, f"{path} references {token}"


def test_web_javascript_has_no_risk_computation():
    for path in _web_files(".js"):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for token in FORBIDDEN_COMPUTATION_TOKENS:
            assert token.lower() not in lowered, f"{path} contains computation token {token}"


def test_web_javascript_does_not_recompute_risk_numbers():
    for path in _web_files(".js"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"Math\.(exp|log|sqrt|pow|erf)", text), f"{path} performs math"


def test_web_has_required_assets():
    names = {path.name for path in WEB_DIR.iterdir() if path.is_file()}
    assert {"index.html", "styles.css", "app.js", "schema.json"} <= names


def test_schema_views_reference_declared_fields():
    schema = json.loads((WEB_DIR / "schema.json").read_text(encoding="utf-8"))
    fields = set(schema["fields"])
    for view, referenced in schema["views"].items():
        for name in referenced:
            assert name in fields, f"view {view} references undeclared field {name}"


def test_mandated_views_present():
    schema = json.loads((WEB_DIR / "schema.json").read_text(encoding="utf-8"))
    assert set(schema["views"]) == {
        "position_inspector",
        "survival_term_structure",
        "portfolio_risk",
        "contagion_map",
    }


def test_index_renders_each_view():
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    for view_id in [
        "position-inspector",
        "survival-term-structure",
        "portfolio-risk",
        "contagion-map",
    ]:
        assert f'id="{view_id}"' in html

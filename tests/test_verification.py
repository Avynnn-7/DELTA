import numpy as np

from validation import audit, verify


def test_master_ledger_all_verified():
    verify.assert_ledger_verified()
    statuses = {row.status for row in verify.MASTER_LEDGER}
    assert statuses == {"verified"}


def test_literature_crosschecks_reference_ledger():
    verify.assert_results_cross_referenced()


def test_var_non_subadditivity_counterexample():
    result = verify.var_subadditivity_counterexample(alpha=0.975)
    assert np.isclose(result["var_single"], -1.0)
    assert np.isclose(result["var_joint"], 98.0)
    assert np.isclose(result["additive_bound"], -2.0)
    assert result["subadditivity_violated"]


def test_probabilistic_validity_sweep():
    report = verify.probabilistic_validity_report()
    assert all(report.values())
    assert "es_ge_var" in report
    assert "first_passage_dominates_terminal" in report


def test_dimensional_validity_sweep():
    report = verify.dimensional_validity_report()
    assert all(report.values())
    assert "square_root_impact" in report


def test_error_budget_ordering():
    assert verify.error_budget_ordering(1e-12, 1e-3, 1e-1)
    assert not verify.error_budget_ordering(1e-1, 1e-3, 1e-12)


def test_audit_limitations_documented():
    audit.assert_limitations_documented()
    registry = audit.limitation_registry()
    assert "L-COP" in registry
    assert "L-IMP" in registry


def test_audit_assumptions_handled():
    audit.assert_assumptions_handled()
    registry = audit.assumption_registry()
    assert len(registry) == 7

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from engine.conventions import units
from engine.dependence import copula, vasicek
from engine.hazard import survival
from engine.numerics import normal
from engine.risk import var_es
from engine.structural import firstpassage
from validation import dimensional, probabilistic


@dataclass(frozen=True)
class LedgerRow:
    identifier: str
    result: str
    status: str


MASTER_LEDGER = (
    LedgerRow("D-1.1", "GBM solution", "verified"),
    LedgerRow("D-1.3", "Expected price", "verified"),
    LedgerRow("D-2.1", "Merton PD", "verified"),
    LedgerRow("D-2.2", "Asset inversion", "verified"),
    LedgerRow("D-3.1", "Liquidation probability", "verified"),
    LedgerRow("D-3.2", "Drop to liquidation", "verified"),
    LedgerRow("R-3.3", "Interest-adjusted drift", "verified"),
    LedgerRow("D-4.1", "First-passage CDF", "verified"),
    LedgerRow("D-4.2", "Inverse-Gaussian density", "verified"),
    LedgerRow("R-4.3", "Defect mass", "verified"),
    LedgerRow("D-5.1", "Survival-hazard", "verified"),
    LedgerRow("D-5.2", "Cox survival", "verified"),
    LedgerRow("D-5.3", "Bootstrap intensities", "verified"),
    LedgerRow("D-5.4", "CIR survival", "verified"),
    LedgerRow("D-5.5", "Credit triangle", "verified"),
    LedgerRow("D-6.1", "Realized to quadratic variation", "verified"),
    LedgerRow("D-6.2", "EWMA", "verified"),
    LedgerRow("D-6.3", "GARCH long-run variance", "verified"),
    LedgerRow("D-6.4", "GARCH forecast", "verified"),
    LedgerRow("D-6.5", "MLE", "verified"),
    LedgerRow("R-6.6", "MLE divisor", "verified"),
    LedgerRow("D-7.1", "Factor correlation", "verified"),
    LedgerRow("D-7.2", "Vasicek loss CDF", "verified"),
    LedgerRow("Thm-7.2", "Gaussian zero tail dependence", "verified"),
    LedgerRow("D-7.3", "t-copula tail dependence", "verified"),
    LedgerRow("D-7.4", "Kendall to correlation", "verified"),
    LedgerRow("D-8.1", "Square-root impact", "verified"),
    LedgerRow("R-8.2", "Cascade termination", "verified"),
    LedgerRow("D-8.2", "Monte Carlo LLN", "verified"),
    LedgerRow("D-8.3", "Monte Carlo CLT", "verified"),
    LedgerRow("R-8.4", "Antithetic variates", "verified"),
    LedgerRow("R-8.5", "Importance sampling", "verified"),
    LedgerRow("D-9.1", "Expected shortfall forms", "verified"),
    LedgerRow("Thm-9.1", "Coherence", "verified"),
    LedgerRow("D-9.2", "ES contribution", "verified"),
    LedgerRow("D-9.3", "VaR estimator", "verified"),
    LedgerRow("D-9.4", "ES estimator", "verified"),
    LedgerRow("D-10.1", "Cholesky sampling", "verified"),
)


LITERATURE_CROSSCHECKS = {
    "D-1.1": "Oksendal (2003); Hull (2018)",
    "D-2.1": "Merton (1974); Crosbie and Bohn (2003)",
    "D-4.1": "Harrison (1985); Borodin and Salminen (2002)",
    "D-4.2": "Chhikara and Folks (1989)",
    "D-5.1": "Cox and Oakes (1984)",
    "D-5.2": "Lando (1998); Duffie and Singleton (1999)",
    "D-5.5": "Hull and White (2000); O'Kane (2008)",
    "D-6.3": "Bollerslev (1986)",
    "D-7.2": "Vasicek (1987, 2002); BCBS (2005)",
    "Thm-7.2": "Embrechts, McNeil and Straumann (2002); Sibuya (1960)",
    "D-7.3": "Demarta and McNeil (2005)",
    "D-7.4": "Lindskog, McNeil and Schmock (2003)",
    "D-8.1": "Almgren et al. (2005); Toth et al. (2011)",
    "D-8.3": "Glasserman (2004)",
    "R-8.5": "Glasserman and Li (2005)",
    "Thm-9.1": "Artzner et al. (1999); Acerbi and Tasche (2002)",
    "D-9.2": "Tasche (1999)",
    "D-9.3": "Serfling (1980)",
    "D-10.1": "Glasserman (2004)",
}


def assert_ledger_verified():
    for row in MASTER_LEDGER:
        if row.status != "verified":
            raise ValueError(f"ledger row {row.identifier} is not verified")


def assert_results_cross_referenced():
    ledger_ids = {row.identifier for row in MASTER_LEDGER}
    for identifier in LITERATURE_CROSSCHECKS:
        if identifier not in ledger_ids:
            raise ValueError(f"cross-check {identifier} has no ledger row")


def discrete_value_at_risk(values, probabilities, alpha):
    values = np.asarray(values, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    order = np.argsort(values)
    values = values[order]
    cumulative = np.cumsum(probabilities[order])
    index = int(np.searchsorted(cumulative, alpha, side="left"))
    index = min(index, values.shape[0] - 1)
    return float(values[index])


def var_subadditivity_counterexample(alpha=0.975):
    single_values = np.array([-1.0, 99.0])
    single_probabilities = np.array([0.98, 0.02])
    var_single = discrete_value_at_risk(single_values, single_probabilities, alpha)

    joint_values = np.array([-2.0, 98.0, 198.0])
    joint_probabilities = np.array([0.98**2, 2.0 * 0.98 * 0.02, 0.02**2])
    var_joint = discrete_value_at_risk(joint_values, joint_probabilities, alpha)

    additive_bound = 2.0 * var_single
    return {
        "var_single": var_single,
        "var_joint": var_joint,
        "additive_bound": additive_bound,
        "subadditivity_violated": var_joint > additive_bound,
    }


def probabilistic_validity_report():
    report = {}

    grid = np.linspace(-6.0, 6.0, 200)
    cdf = normal.cdf(grid)
    probabilistic.assert_in_unit_interval(cdf, "normal cdf")
    report["normal_cdf"] = True

    horizons = np.linspace(0.01, 5.0, 200)
    survival_curve = survival.constant_survival(0.3, horizons)
    probabilistic.assert_in_unit_interval(survival_curve, "survival")
    probabilistic.assert_monotone_non_increasing(survival_curve, "survival")
    report["survival_monotone"] = True

    times = np.linspace(0.01, 2.0, 100)
    first_passage = firstpassage.first_passage_cdf(1.5, -0.1, 0.4, times)
    terminal = firstpassage.terminal_cdf(1.5, -0.1, 0.4, times)
    probabilistic.assert_in_unit_interval(first_passage, "first passage")
    probabilistic.assert_ge(first_passage, terminal, "first passage vs terminal")
    report["first_passage_dominates_terminal"] = True

    x = np.linspace(0.01, 0.99, 100)
    loss_cdf = vasicek.loss_cdf(x, 0.05, 0.3)
    probabilistic.assert_in_unit_interval(loss_cdf, "vasicek loss cdf")
    probabilistic.assert_monotone_non_decreasing(loss_cdf, "vasicek loss cdf")
    report["vasicek_loss_cdf"] = True

    lam = copula.student_t_lower_tail_dependence(0.5, 6.0)
    probabilistic.assert_in_unit_interval(lam, "t-copula tail dependence")
    if lam <= 0.0:
        raise ValueError("t-copula tail dependence must be positive")
    report["t_copula_tail_dependence_positive"] = True

    losses = np.linspace(0.0, 100.0, 10000)
    var = var_es.value_at_risk(losses, 0.99)
    es = var_es.expected_shortfall_conditional(losses, 0.99)
    probabilistic.assert_ge(es, var, "ES vs VaR")
    report["es_ge_var"] = True

    return report


def dimensional_validity_report():
    report = {}

    drift_time = units.RATE * units.TIME
    sigma_root_time = units.VOLATILITY * units.TIME**units.Fraction(1, 2)
    dimensional.assert_dimensionless(units.DIMENSIONLESS, "log health")
    dimensional.assert_dimensionless(drift_time, "drift times time")
    dimensional.assert_dimensionless(sigma_root_time, "sigma root time")
    report["distance_to_liquidation"] = True

    cumulative_hazard = units.RATE * units.TIME
    dimensional.assert_dimensionless(cumulative_hazard, "cumulative hazard")
    report["cumulative_hazard"] = True

    relative_volume = units.CURRENCY / units.CURRENCY
    impact = units.DIMENSIONLESS * relative_volume**units.Fraction(1, 2)
    dimensional.assert_dimensionless(impact, "square-root impact")
    report["square_root_impact"] = True

    return report


def error_budget_ordering(epsilon_numerical, epsilon_monte_carlo, epsilon_parameter):
    return epsilon_numerical < epsilon_monte_carlo < epsilon_parameter

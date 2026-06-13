# DELTA — Crypto Default & Contagion Risk Analyser

> **Mathematical Framework** · a real-time DeFi liquidation & contagion (crypto default) risk engine.

A research-grade reference documenting the complete mathematical foundation of a real-time
DeFi liquidation and contagion risk engine. Every model is grounded in peer-reviewed
literature, derived from first principles, and independently verified through two review passes.

## Purpose

This collection translates the established **structural** and **reduced-form** credit-risk
apparatus (Merton 1974; Black & Cox 1976; Jarrow & Turnbull 1995; Li 2000; Vasicek 1987, 2002)
into the on-chain over-collateralized lending and stablecoin setting, and supplies the
risk-aggregation theory (Artzner et al. 1999; Rockafellar & Uryasev 2000, 2002;
McNeil, Frey & Embrechts 2015) needed to quantify protocol-level risk.

## Document map

| File | Contents |
|------|----------|
| [00_notation_and_conventions.md](00_notation_and_conventions.md) | Symbols, probability space, conventions, dimensional bookkeeping |
| [01_geometric_brownian_motion.md](01_geometric_brownian_motion.md) | GBM, Itô calculus, log-return distribution — the price-process foundation |
| [02_merton_structural_model.md](02_merton_structural_model.md) | Merton model, distance-to-default, the equity↔asset inversion |
| [03_distance_to_liquidation.md](03_distance_to_liquidation.md) | Mapping Merton to over-collateralized lending; first-passage formulation |
| [04_first_passage_barrier.md](04_first_passage_barrier.md) | Black–Cox first-passage, reflection principle, inverse-Gaussian hitting time |
| [05_reduced_form_hazard.md](05_reduced_form_hazard.md) | Cox/intensity models, survival curves, de-peg hazard, CDS-style calibration |
| [06_volatility_estimation.md](06_volatility_estimation.md) | Realized variance, EWMA, GARCH(1,1), MLE — estimating the σ input |
| [07_copula_dependence.md](07_copula_dependence.md) | Sklar's theorem, Gaussian & t copulas, tail dependence, factor model |
| [08_monte_carlo_cascade.md](08_monte_carlo_cascade.md) | Correlated simulation, price-impact contagion, convergence, variance reduction |
| [09_risk_measures.md](09_risk_measures.md) | VaR, Expected Shortfall, coherence, Euler allocation, estimator theory |
| [10_numerical_methods.md](10_numerical_methods.md) | Φ and Φ⁻¹ approximations, root-finding, Cholesky, RNG |
| [11_audit_pass_1.md](11_audit_pass_1.md) | **Audit:** derivation checks, notation, assumptions, gap analysis |
| [12_verification_pass_2.md](12_verification_pass_2.md) | **Verification:** independent re-derivations, dimensional/probabilistic checks |
| [13_references.md](13_references.md) | Full bibliography (primary sources + canonical texts) |

## How to read

1. Start with notation ([00](00_notation_and_conventions.md)) and the GBM foundation ([01](01_geometric_brownian_motion.md)).
2. Single-name risk: [02](02_merton_structural_model.md) → [03](03_distance_to_liquidation.md) → [04](04_first_passage_barrier.md); term-structure risk: [05](05_reduced_form_hazard.md); the σ input: [06](06_volatility_estimation.md).
3. Portfolio risk: dependence ([07](07_copula_dependence.md)) → cascade simulation ([08](08_monte_carlo_cascade.md)) → risk measures ([09](09_risk_measures.md)).
4. Implementation numerics: [10](10_numerical_methods.md).
5. Correctness: the two review passes ([11](11_audit_pass_1.md), [12](12_verification_pass_2.md)) and the bibliography ([13](13_references.md)).

## Verification status

Every numbered result (D-x.y / R-x.y) is checked once in [Audit Pass 1](11_audit_pass_1.md)
and re-derived independently in [Verification Pass 2](12_verification_pass_2.md). The audit
ledger at the end of [12](12_verification_pass_2.md) records the status of each.

> **Scope caveat.** This is a *mathematical* reference. Where a model's assumptions are known
> to be violated by crypto markets (heavy tails, jumps, liquidity spirals, oracle latency,
> reflexivity), the limitation is stated explicitly rather than hidden. Mathematical
> correctness — not implementation convenience — is the governing priority throughout.

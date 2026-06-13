# Phase 2 — Price Process & Volatility Input

> Files: `defi/01` (geometric Brownian motion), `defi/06` (volatility estimation).
> Modules: M-GBM, M-Vol.

The structural metrics of Phase 3 are all functions of `σ` and of the GBM
log-return law. This phase establishes the price-process foundation and the `σ`
estimator that feeds every distance measure. Per `defi/06`, a wrong `σ` corrupts
every downstream number, so `σ` estimation carries the same rigor as the models
it feeds.

---

## Objectives

1. Implement the GBM solution and its exact log-return distribution (D-1.1–D-1.4).
2. Implement the volatility estimators (RV, EWMA, GARCH family) with their
   stationarity/annualization guarantees and the variance term structure.
3. Encode the "trust `σ̂`, distrust `μ̂`" stance: variance is estimable from short
   windows, drift is not (`defi/06` §6.6, L-DRIFT) — resolves GAP-8.

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| D-1.1 | GBM solution | `P_t=P_0 exp[(μ−½σ²)t+σW_t]` | `defi/01` §1.3 |
| D-1.2 | Log-return law | `ln(P_t/P_0)~N((μ−½σ²)t, σ²t)` | `defi/01` §1.4 |
| D-1.3 | Mean | `E[P_t]=P_0 e^{μt}` (volatility drag `½σ²`) | `defi/01` §1.4 |
| D-1.4 | Variance | `Var(P_t)=P_0² e^{2μt}(e^{σ²t}−1)` | `defi/01` §1.7 |
| D-6.1 | Realized variance | `Σr_i² → ∫σ_s²ds` (quadratic variation); `σ̂²=1/(n−1)Σ(r_i−r̄)²` | `defi/06` §6.2 |
| D-6.2 | EWMA recursion | `σ̂_t²=λσ̂_{t−1}²+(1−λ)r_{t−1}²` (RiskMetrics, λ=0.94 daily) | `defi/06` §6.3 |
| D-6.3 | GARCH long-run var | `σ̄²=ω/(1−α−β)`, requires `α+β<1` | `defi/06` §6.4 |
| D-6.4 | GARCH var forecast | `E_t[σ²_{t+h}]=σ̄²+(α+β)^{h−1}(σ²_{t+1}−σ̄²)` → horizon-dependent `σ(T)` | `defi/06` §6.4 |
| D-6.5 | (Q)MLE | log-likelihood (6.6); QMLE consistent under non-normal innovations | `defi/06` §6.5 |
| R-6.6 | MLE divisor | MLE divisor `n` vs unbiased `n−1` (Bessel) | `defi/06` §6.5 |
| — | GJR-GARCH / EGARCH | leverage/asymmetry; Student-t innovations for heavy tails | `defi/06` §6.6 |
| — | Annualization (24/7) | `n_yr=365×24×…`, not 252 | `defi/06` §6.6 |
| — | Model selection | AIC/BIC; out-of-sample QLIKE/MSE vs RV (Patton) | `defi/06` §6.7 |
| — | Drift handling | set `μ≈0` (or `μ=r_b`) for short horizon | `defi/06` §6.6, `defi/03` §3.6 |

Recommended default (`defi/06` §6.7): **GJR-GARCH(1,1)-t** for risk metrics, EWMA
as the `O(1)` streaming fallback, RV as the model-free monitor.

---

## Implementation scope

- `process/gbm` — GBM solution, log-return law, mean/variance, exact path sampler
  (constant-coefficient integration of (1.3)).
- `volatility/realized` — RV / quadratic-variation estimator with 24/7
  annualization; microstructure caveat noted (L-V1).
- `volatility/ewma` — EWMA recursion (`O(1)` update).
- `volatility/garch` — GARCH(1,1), GJR-GARCH, EGARCH with Student-t innovations;
  long-run variance and the (6.5) variance term structure.
- `volatility/mle` — (Q)MLE estimation (6.6); GBM closed-form MLE (R-6.6).
- `volatility/selection` — AIC/BIC and QLIKE out-of-sample comparison.

The GARCH/MLE optimizers reuse the M-Num root-finders/optimization primitives from
Phase 1 (`defi/10` §10.3); no new numerical machinery is introduced here.

---

## Dependencies

- Phase 1: M0 conventions, `Φ`/`Φ⁻¹`, stability rules, root-finders.

## Inputs

- Equally-spaced log-return series `{r_i}` (from the data-acquisition layer).
- Sampling frequency and 24/7 annualization factor `n_yr`.

## Outputs

- Annualized `σ̂` (point and, via D-6.4, horizon-dependent `σ(T)`).
- GARCH parameters and conditional-variance paths.
- Drift policy (`μ≈0`/`μ=r_b`) for short-horizon structural metrics.
- The per-asset return marginal law (innovation distribution) needed later by the
  copula transform — its specification is flagged GAP-6 and finalized in Phase 5.

---

## Validation requirements

- GBM solution and `E[P_t]=P_0e^{μt}` re-derived by the ansatz/MGF routes
  (`defi/12` §A-1); volatility drag `½σ²` confirmed.
- GARCH stationarity `α+β<1`; EWMA = IGARCH boundary (`ω=0, α+β=1`)
  (`defi/12` §A-6).
- GBM MLE divisor `n` vs unbiased `n−1` (`defi/12` §A-6, R-6.6).
- RV → quadratic-variation consistency (`defi/12` §D, D-6.1).
- Dimensional check: `(μ−½σ²)t`, `σ²t`, `σW_t` dimensionless (`defi/12` §C, eq 1.4).
- Model selection by out-of-sample QLIKE against RV (`defi/06` §6.7).

## Completion criteria

- Ledger rows D-1.1–D-1.4, D-6.1–D-6.5, R-6.6 reach **verified** (`defi/12` §E).
- A documented, estimable `σ(T)` is available to Phase 3 with annualization and
  drift policy fixed; GAP-8 resolved by an explicit short-horizon drift rule.

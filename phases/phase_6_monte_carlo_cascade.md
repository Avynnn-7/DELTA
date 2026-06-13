# Phase 6 — Monte Carlo Cascade Engine

> File: `defi/08` (Monte Carlo cascade).
> Module: M-Cascade.

This is the engine's signature computation: a correlated Monte Carlo simulation of
liquidation cascades with endogenous price impact. It turns the independent
liquidation probabilities (Phase 3/4) and the dependence structure (Phase 5) into
a systemic contagion model — the iterative "liquidate → push price down →
re-check" loop — and produces the loss distribution consumed by the risk measures
(Phase 7).

---

## Objectives

1. Implement one correlated simulation scenario: sample shared+idiosyncratic
   shocks via the t-copula, map to price shocks, and run the cascade loop with
   price impact.
2. Implement the Monte Carlo convergence machinery (LLN, CLT/standard error) and
   variance-reduction techniques to make the tail estimable in real time.
3. Produce the simulated loss distribution and per-scenario per-position losses
   for Phase 7.

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| — | Correlated shock | `X_i=√(ν/S)(√ρ_i Z+√(1−ρ_i)ε_i)`, `U_i=t_ν(X_i)`, `r_i=F_i⁻¹(U_i)` | `defi/08` §8.2 (8.1) |
| — | Shock to price | `P_i ← P_i⁰ e^{r_i}` | `defi/08` §8.2 |
| — | Cascade loop | recompute `H_j=ℓ_jQ_jP_{a(j)}/B_j`; liquidate `H_j≤1`; apply impact; repeat | `defi/08` §8.2 |
| D-8.1 | Square-root impact | `ΔP/P ≈ −η σ √(q/V)` (Almgren/Gabaix); Kyle linear alternative | `defi/08` §8.3 |
| R-8.2 | Cascade termination | monotone non-increasing price map halts in ≤ d rounds | `defi/08` §8.3 |
| — | Scenario loss | `L^{(s)}=Σ_{liquidated} LGD_j·EAD_j` + fire-sale slippage | `defi/08` §8.2 Step 4 |
| D-8.2 | MC consistency (LLN) | `θ̂_N=1/N Σ g(L^{(s)}) → θ` a.s. | `defi/08` §8.4 |
| D-8.3 | MC error (CLT) | `√N(θ̂_N−θ)→N(0,ς²)`; SE `=ς/√N`, rate `O(N^{−1/2})` | `defi/08` §8.4 |
| R-8.4 | Antithetic variates | pair `(Z,ε)` with `(−Z,−ε)`; valid by symmetry, monotone loss | `defi/08` §8.5 |
| — | Control variates | independent-default / Vasicek analytic loss (D-7.2) as control | `defi/08` §8.5 |
| R-8.5 | Importance sampling | exponential tilt of `Z` toward the loss region (Glasserman–Li) | `defi/08` §8.5 |
| — | Conditional MC / QMC | condition on `Z` with analytic `p(z)`; Sobol' low-discrepancy | `defi/08` §8.5 |

---

## Implementation scope

- `cascade/sampler` — t-copula correlated-shock draw (Phase 5 one-factor sampler +
  Phase 1 Philox RNG), price-shock mapping, GARCH marginal inverse `F_i⁻¹`
  (resolves GAP-6 with the Phase 5 contract).
- `cascade/impact` — square-root impact kernel (D-8.1) as the cascade feedback
  function; Kyle linear form available as the permanent-impact alternative.
  **GAP-3**: `η`, `V`, execution-window `σ` are required inputs with a documented
  stress range (L-IMP); **GAP-4**: the fire-sale slippage term must be tied to the
  impact kernel by an explicit formula before loss aggregation.
- `cascade/loop` — health recomputation (reuses Phase 3 `H_j`), liquidation
  marking, collateral seizure/sale, impact application, iteration to fixed point;
  termination guaranteed (R-8.2).
- `cascade/loss` — scenario loss `Σ LGD·EAD + slippage`. **GAP-1/GAP-2**: `EAD_j`
  computation and `LGD=1−R` value are required inputs (deterministic recovery, A6).
- `cascade/convergence` — running mean/variance, standard error and CIs (D-8.3).
- `cascade/variance_reduction` — antithetic (R-8.4), Vasicek control variate,
  importance sampling (R-8.5), conditional MC, Sobol' QMC.

The default-time draw for pegged assets uses the Cox construction
`τ=inf{t:Λ(t)≥E}` from Phase 4.

---

## Dependencies

- Phase 1: Philox RNG, `Φ`/`Φ⁻¹`, χ² mixing, validity utilities.
- Phase 2: GARCH return marginals `F_i`.
- Phase 3: health-factor recomputation, per-position structural metrics.
- Phase 4: de-peg default-time sampler (pegged assets).
- Phase 5: one-factor t-copula sampler, correlation `R`, Vasicek control variate.

## Inputs

- Position set with on-chain state; asset/factor assignment (`a(j)`, `ρ_i`) from
  Phase 5.
- Price-impact parameters `(η, V, σ_window)` with stress range (GAP-3).
- `EAD_j` per position (GAP-1) and `LGD_j=1−R_j` (GAP-2).
- Scenario count `N` and target accuracy.

## Outputs

- Simulated loss distribution `{L^{(s)}}_{s=1..N}`.
- Per-scenario per-position losses `L_i^{(s)}` (for Euler/ES allocation, Phase 7).
- Convergence diagnostics: standard error, confidence interval, effective sample
  size under variance reduction.

---

## Validation requirements

- Square-root impact dimensionless (`defi/12` §A-8); cascade termination ≤ d
  rounds, monotone price map, no oscillation (`defi/12` §A-8, R-8.2).
- MC standard error decays as `O(N^{−1/2})` (D-8.3); CI coverage checked.
- Control-variate estimate consistent with the Vasicek analytic loss in its
  homogeneous limit (`defi/08` §8.8); antithetic/IS unbiasedness (R-8.4, R-8.5).
- Reproducibility across threads via Philox substreams (N-3).
- Error-budget ordering `ε_num ≪ ε_MC ≪ ε_param` (`defi/10` §10.7).

## Completion criteria

- Ledger rows D-8.1, D-8.2, D-8.3, R-8.2, R-8.4, R-8.5 reach **verified**
  (`defi/12` §E).
- GAP-1, GAP-2, GAP-3, GAP-4 resolved by explicit input contracts/formulas.
- A loss distribution with quantified standard error is available to Phase 7.

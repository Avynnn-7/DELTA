# Phase 4 — Reduced-Form Hazard: De-Peg & Term-Structure Risk

> File: `defi/05` (reduced-form / intensity models).
> Module: M-Hazard.

For events with no clean asset barrier — chiefly stablecoin de-pegs — the
structural machinery of Phase 3 does not apply (`defi/03` §3.7). This phase
implements the intensity (reduced-form) approach: default is the first jump of a
point process with a (possibly stochastic) hazard. It also bridges to Phase 3 via
the structural hazard implied by the first-passage density, putting both
liquidation and de-peg risk on a common survival scale.

---

## Objectives

1. Implement survival/hazard theory and the Cox (doubly-stochastic) survival
   formula.
2. Implement the calibration workhorses: piecewise-constant bootstrap, CIR affine
   intensity, the credit triangle, and statistical (Poisson MLE / EVT / logistic)
   estimation.
3. Implement the structural↔hazard bridge so volatile-collateral liquidation and
   stablecoin de-peg share one hazard scale (R-5.7).

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| D-5.1 | Survival–hazard | `S(t)=e^{−Λ(t)}`, `λ=−d/dt ln S`, `Λ=∫₀ᵗλ` | `defi/05` §5.1 |
| — | Default prob | `PD(t)=1−S(t)=1−e^{−Λ(t)}` | `defi/05` §5.1 |
| D-5.2 | Cox survival | `S(t)=E[exp(−∫₀ᵗλ_s ds)]`; `τ=inf{t:Λ(t)≥E}`, `E~Exp(1)` | `defi/05` §5.2 |
| — | Constant intensity | `S(t)=e^{−λt}`, `τ~Exp(λ)`, mean `1/λ` | `defi/05` §5.3 |
| D-5.3 | Bootstrap | piecewise-constant `Λ(t_K)=Σλ_kΔt_k`, `S(t_j)=exp(−Σλ_kΔt_k)` | `defi/05` §5.3 |
| D-5.4 | CIR affine survival | `dλ=κ(θ−λ)dt+ν√λ dW`; `S(t)=A(t)e^{−b(t)λ_0}` (Riccati); Feller `2κθ≥ν²` | `defi/05` §5.4 |
| D-5.5 | Credit triangle | `λ≈s/(1−R)` (first-order par-spread equality) | `defi/05` §5.5 |
| R-5.6 | Poisson MLE | `λ̂=#events/exposure time` | `defi/05` §5.6 |
| — | EVT de-peg sizing | Generalized Pareto / peaks-over-threshold for deviation magnitude | `defi/05` §5.6 |
| — | Logistic hazard | discrete-time per-epoch de-peg probability with covariates | `defi/05` §5.6 |
| R-5.7 | Structural↔hazard bridge | `λ^struct(t)=f_{τ_b}(t)/S_{τ_b}(t)`, `S_{τ_b}=1−P(τ_b≤t)` | `defi/05` §5.7 |

---

## Implementation scope

- `hazard/survival` — survival/hazard relations, constant and piecewise-constant
  intensity, bootstrap stripping (D-5.3).
- `hazard/cox` — Cox survival expectation and the `τ=inf{t:Λ(t)≥E}` simulation
  construction (reused by the cascade default-time draw, Phase 6).
- `hazard/cir` — CIR intensity with the Feller condition enforced; affine survival
  `A(t)e^{−b(t)λ_0}`. **Blocked by GAP-7**: the explicit Riccati `A(t),b(t)` closed
  forms are referenced but not written in `defi/05`; they must be obtained from the
  cited affine result before this submodule is implemented.
- `hazard/calibration` — credit triangle (D-5.5); Poisson MLE (R-5.6); EVT/GPD
  de-peg-severity tail; logistic discrete-time hazard. Uses Phase 1
  incomplete-gamma/χ² and Brent root-finder.
- `hazard/bridge` — structural hazard from the Phase 3 first-passage density (R-5.7).

The credit triangle is implemented as the **first-order** form and explicitly
flagged as such; the exact leg-PV form is available if larger spreads/tenors
require it (`defi/05` §5.9, `defi/12` §A-5).

---

## Dependencies

- Phase 1: incomplete-gamma/χ², Brent root-finder, validity utilities.
- Phase 3: first-passage density `f_{τ_b}` and survival `S_{τ_b}` (for R-5.7).

## Inputs

- Peg-deviation time series (`|P_t−1|>θ` events) for Poisson MLE / EVT / logistic.
- De-peg protection spreads `s` and recovery `R` for the credit triangle
  (**GAP-2**: `R` source/value is not specified in-text and must be supplied as a
  declared input).
- CIR parameters `(κ,θ,ν,λ_0)` satisfying Feller, or a calibration target.

## Outputs

- Per-asset hazard `λ`, cumulative hazard `Λ`, survival curve `S(t)`, de-peg
  `PD(t)` term structure.
- A unified hazard/survival scale per position/asset (structural + reduced-form).
- De-peg default-time sampler (`τ=inf{t:Λ(t)≥E}`) for Phase 6.

---

## Validation requirements

- Survival–hazard and Cox construction re-derived (`defi/12` §A-5).
- Credit triangle re-derived from protection/premium leg PVs; first-order nature
  flagged (`defi/12` §A-5, D-5.5).
- Probabilistic validity: `S(t)∈(0,1]` and non-increasing; `λ_t>0` under Feller
  `2κθ≥ν²` (`defi/12` §B).
- Dimensional sweep: `Λ=∫λ dt` dimensionless; `s/(1−R)` has units yr⁻¹
  (`defi/12` §C, eqs 5.2, 5.6).
- Structural↔hazard consistency (R-5.7) checked against Phase 3 first-passage.

## Completion criteria

- Ledger rows D-5.1–D-5.5, R-5.6, R-5.7 reach **verified** (`defi/12` §E).
- GAP-7 (explicit CIR Riccati forms) and GAP-2 (`R` input contract) resolved and
  documented.
- Routing from Phase 3 (pegged assets) terminates in a survival curve here.

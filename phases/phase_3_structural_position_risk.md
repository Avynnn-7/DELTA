# Phase 3 — Structural Per-Position Risk

> Files: `defi/02` (Merton), `defi/03` (distance-to-liquidation), `defi/04`
> (first-passage / barrier).
> Modules: M-Merton, M-DTL, M-FP.

This phase produces the core single-name metrics: how likely, and how soon, a
position is liquidated. It transplants the Merton distance-to-default onto
on-chain lending (`defi/03`) and corrects the terminal-horizon probability with
the path-dependent first-passage law (`defi/04`), which is the **primary**
per-position metric.

---

## Objectives

1. Implement the Merton PD and distance-to-default, including the equity↔asset
   inversion machinery (reserved for cases lacking direct observability).
2. Map Merton onto DeFi: health factor, DTL, terminal PL, drop-to-liquidation,
   and the interest-adjusted drift correction.
3. Implement the first-passage CDF and inverse-Gaussian timing density with the
   defective-distribution handling — the primary metric.
4. Route assets by type (volatile collateral → structural here; pegged → hazard,
   Phase 4) per `defi/03` §3.7.

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| D-2.1 | Merton PD | `PD=Φ((ln(D/V_0)−(μ_V−½σ_V²)T)/(σ_V√T))=Φ(−DD)` | `defi/02` §2.2 |
| def | Distance-to-default | `DD=(ln(V_0/D)+(μ_V−½σ_V²)T)/(σ_V√T)` | `defi/02` §2.3 |
| D-2.2 | Equity↔asset inversion | (2.5) BS call + (2.7) Itô-vol → solve `(V_0,σ_V)` | `defi/02` §2.4 |
| def | Health factor | `H_t=ℓC_t/B_t`; liquidation at `H_t≤1` | `defi/03` §3.1 |
| D-3.1 | Probability of liquidation | `PL(T)=Φ(−DTL)` | `defi/03` §3.3 |
| def | Distance-to-liquidation | `DTL=(ln H_0+(μ−½σ²)T)/(σ√T)` (standardized log-health) | `defi/03` §3.3 |
| D-3.2 | Drop-to-liquidation | `δ*=1−1/H_0` (model-free) | `defi/03` §3.4 |
| — | Multi-horizon profile | `{PL(T): 1h,24h,7d,…}`, `T` annualized | `defi/03` §3.5 |
| R-3.3 | Interest-adjusted drift | ratio `C_t/B_t` is GBM with drift `μ−r_b`; replace `μ→μ−r_b` | `defi/03` §3.6 |
| def | First-passage time | `τ_b=inf{t:X_t≤b}`, `b=−ln H_0`, `X_t=mt+σW_t`, `m=μ−½σ²` | `defi/04` §4.1 |
| D-4.1 | First-passage CDF | `P(τ_b≤T)=Φ((b−mT)/(σ√T))+e^{2mb/σ²}Φ((b+mT)/(σ√T))` | `defi/04` §4.2 |
| D-4.2 | First-passage density | inverse Gaussian (4.6) | `defi/04` §4.3 |
| R-4.3 | Defect mass | `P(τ_b<∞)=e^{2mb/σ²}<1` when `m>0` (defective IG) | `defi/04` §4.3 |
| — | Asset routing | volatile → structural; pegged → hazard (`defi/05`) | `defi/03` §3.7 |

First passage **dominates** the terminal form
(`P(τ_b≤T) ≥ P(X_T≤b)`, gap G-3) and is the primary metric; the terminal PL is
retained as a lower bound.

---

## Implementation scope

- `structural/merton` — Merton PD, DD; equity↔asset inversion via 2-D
  Newton–Raphson / Duan iteration (`defi/10` §10.3). The inversion is
  **disabled by default** for DeFi positions where `C_t,B_t` are observed on-chain
  (`defi/03` §3.2), and reserved only for the unobservable-balance-sheet case.
- `structural/dtl` — health factor, DTL, terminal PL, drop-to-liquidation,
  multi-horizon term structure, interest-adjusted drift (R-3.3).
- `structural/firstpassage` — first-passage CDF (D-4.1), inverse-Gaussian density
  (D-4.2), defect-mass branch (R-4.3); exposes the primary per-position PL and the
  timing density.
- `structural/routing` — dispatch by asset type (volatile vs pegged).

All evaluations use the tail-accurate `Φ` (N-1) and the short-horizon drift policy
from Phase 2; no new numerics.

---

## Dependencies

- Phase 1: tail-accurate `Φ`, root-finders, validity utilities.
- Phase 2: `σ` / `σ(T)`, drift policy.

## Inputs

- On-chain position state: `C_t=Q·P_t`, `B_t`, `ℓ`, `Q`, `P_t`, borrow rate `r_b`.
- `σ` (and `σ(T)`) from Phase 2; horizon grid `{T}`.
- For the reserved Merton inversion only: `S_0, σ_S, D, r, T`.

## Outputs

- Per-position: DTL, terminal PL, **first-passage PL (primary)**, `δ*`,
  inverse-Gaussian timing density, and the term structure `{PL(T)}`.
- Marginal liquidation probabilities `PD_i` to be consumed by the dependence
  layer (Phase 5) — the exact marginal choice/horizon is flagged GAP-5.

---

## Validation requirements

- Merton inversion well-posedness: Jacobian non-singular on the economic domain
  (`defi/12` §A-2).
- DTL strictly increasing in `H_0` ⇒ PL decreasing (`defi/12` §A-3).
- Interest-adjusted drift `μ→μ−r_b` exact via ratio process (`defi/12` §A-3, R-3.3).
- First-passage CDF re-derived by the PDE/method-of-images route; defect mass
  `e^{2mb/σ²}` confirmed in the `m>0` limit (`defi/12` §A-4).
- Probabilistic validity: `PD,PL∈[0,1]`; first-passage ≥ terminal; IG density ≥0
  and integrates to `≤1` (defective when `m>0`) (`defi/12` §B).
- Dimensional sweep of (2.3), (3.3), (4.5) (`defi/12` §C).

## Completion criteria

- Ledger rows D-2.1, D-2.2, D-3.1, D-3.2, R-3.3, D-4.1, D-4.2, R-4.3 reach
  **verified** (`defi/12` §E).
- First-passage PL established as the primary per-position output; terminal PL
  retained as documented lower bound (G-3 resolved).
- Asset-routing dispatch operational; pegged assets handed to Phase 4.

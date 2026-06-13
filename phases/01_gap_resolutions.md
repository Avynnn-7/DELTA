# Gap Resolutions — Definitions for the Flagged Items (GAP-1 … GAP-9)

> Companion to `phases/00_roadmap_overview.md` §6. This file **defines** each
> flagged gap so that planning can proceed. Nothing here overrides the
> specifications in `defi/00`–`defi/12`; it only fills items those files leave
> undefined.
>
> Each resolution is tagged:
> - **[derived]** — forced by the mathematics already present in `defi/00`–`defi/12`.
> - **[input]** — the files leave it open; resolved as an explicit, declared input
>   contract with a documented default, consistent with the stated assumptions.
>
> No external model, estimator, or formula is introduced beyond what the cited
> results already justify.

---

## GAP-1 — Exposure at default `EAD_j` · [derived]

`defi/00` §0.2 defines `EAD` as exposure at default (currency) and `defi/08`
§8.2 Step 4 uses it in `L^{(s)}=Σ LGD_j·EAD_j`. For an over-collateralized lending
position the protocol's exposure is the outstanding **debt** at the liquidation
instant. Using the debt-accrual law already in `defi/03` §3.6
(`B_t=B_0 e^{r_b t}`):

$$
\mathrm{EAD}_j = B_{\tau_j} = B_{0,j}\,e^{r_{b,j}\,\tau_j},
$$

where `τ_j` is the position's liquidation time within the scenario (the cascade
round at which `H_j≤1`). For a single-period scenario this collapses to the debt
at the shock instant `B_{0,j}`.

**Contract.** `EAD_j` is computed inside the cascade from the position's own
`B_{0,j}, r_{b,j}` and the round index; it is not an external input.

---

## GAP-2 — Recovery `R_j` and loss given default `LGD_j=1−R_j` · [input, structurally constrained]

`defi/00` §0.5 A6 fixes recovery as **deterministic**; `defi/05` §5.5 and
`defi/09` consume it. The files never assign a value. Resolution keeps recovery
deterministic (A6) but ties it to the seized-collateral proceeds already modeled
by the cascade, so it is internally consistent rather than free:

$$
R_j = \min\!\Big(1,\ \frac{\text{recovered collateral value}_j}{\mathrm{EAD}_j}\Big),
\qquad
\mathrm{LGD}_j = 1 - R_j,
$$

with recovered collateral value = seized collateral value **net of fire-sale
slippage** (GAP-4). At the liquidation barrier `H_j=1 ⇒ ℓ_j C_{\tau_j}=B_{\tau_j}`,
so gross collateral is `C_{\tau_j}=B_{\tau_j}/ℓ_j` and

$$
\text{recovered}_j = \frac{B_{\tau_j}}{\ell_j}\,(1-\mathrm{slip}_j),
\qquad
R_j = \min\!\Big(1,\ \frac{1-\mathrm{slip}_j}{\ell_j}\Big).
$$

**Contract.** Where a position is calibrated through the credit triangle
(`defi/05` §5.5, `λ≈s/(1−R)`), `R_j` is instead supplied directly as a declared
per-asset constant (still deterministic, A6). The two uses are disjoint: collateral
recovery for liquidation losses; declared `R` for de-peg-spread calibration.

---

## GAP-3 — Price-impact parameters `η`, `V`, `σ_window` · [input]

`defi/08` §8.3 (D-8.1) states `ΔP/P ≈ −η σ √(q/V)` with `η=O(1)`, and L-IMP
mandates **stressing** `η`. The files give no numeric values. Resolution as a
declared input bundle with documented defaults consistent with the cited stylized
fact:

| Symbol | Meaning | Source | Default / contract |
|--------|---------|--------|--------------------|
| `η` | impact coefficient | `defi/08` §8.3, L-IMP | baseline `η=1` (the `O(1)` value), swept over a stress range as an explicit scenario parameter |
| `V` | daily traded volume of the asset | `defi/08` §8.3 | per-asset data input from the data-acquisition layer |
| `σ_window` | fractional return volatility over the execution window | `defi/08` §8.3, `defi/12` §A-8 | derived from Phase 2 `σ` rescaled to the execution-window length (not annualized) |

**Contract.** `η` is never a hidden constant; every reported cascade number
carries the `η` value used, and the engine exposes the stress sweep over `η`
(L-IMP).

---

## GAP-4 — Fire-sale slippage term · [derived]

`defi/08` §8.2 Step 4 adds "fire-sale slippage" to scenario loss but gives no
formula. The only impact law in the file is the square-root kernel (D-8.1), so the
slippage on liquidating quantity `q_j` of an asset must be that kernel applied to
the seized notional:

$$
\mathrm{slip}_j = \eta\,\sigma_{\text{window}}\,\sqrt{\frac{q_j}{V}},
\qquad
\text{slippage cost}_j = C_{\tau_j}\cdot \mathrm{slip}_j,
$$

where `q_j` is the collateral quantity sold and `C_{\tau_j}=Q_jP_{a(j)}` its value.
This is exactly the relative price move of (8.2) multiplied by the sold notional,
so the slippage entering the loss and the price move feeding the cascade loop are
the **same** kernel — no second impact model is introduced.

**Contract.** Scenario loss is
`L^{(s)} = Σ_{liquidated} LGD_j·EAD_j + Σ_{liquidated} C_{τ_j}·slip_j`, with `slip_j`
also driving the within-scenario price update (`defi/08` §8.2 Step 3).

---

## GAP-5 — Copula marginal choice and portfolio horizon `T` · [derived + input]

`defi/07` §7.2 sets the trigger `default_i ⇔ X_i<Φ⁻¹(PD_i)` but does not say which
`PD_i` or which horizon. The asset-routing rule already fixed in `defi/03` §3.7
determines the marginal by asset type:

$$
\mathrm{PD}_i =
\begin{cases}
\mathbb P(\tau_{b,i}\le T) & \text{volatile collateral (first-passage PL, D-4.1, the *primary* metric)}\\[4pt]
1 - S_i(T) & \text{pegged asset (hazard PD, D-5.1)}
\end{cases}
$$

evaluated at a **single declared portfolio horizon** `T`.

**Contract.** `T` is one tenor chosen from the multi-horizon grid of `defi/03`
§3.5 (e.g. `T=7\text{d}` in annualized units), declared once and applied uniformly
to all names so the marginals entering the copula are mutually consistent. The
marginal *type* is derived (first-passage vs hazard); only the horizon value is a
declared input.

---

## GAP-6 — GARCH-implied return marginal `F_i` · [derived]

`defi/08` §8.2 uses `r_i=F_i^{-1}(U_i)` without pinning `F_i`. `defi/06` §6.6–§6.7
already selects the marginal: the recommended **GJR-GARCH(1,1)-t** with
**Student-t innovations**, multi-horizon variance from the mean-reverting forecast
(D-6.4, eq 6.5). Hence:

$$
F_i = \text{c.d.f. of } r_i = \mu_i + \sigma_i(T)\,z_i,\quad z_i\sim t_{\nu_i},
$$

with `σ_i(T)` the GARCH variance term structure (D-6.4) over the GAP-5 horizon `T`
and `μ_i` set by the short-horizon drift rule (GAP-8). The innovation degrees of
freedom `ν_i` come from the GJR-GARCH-t fit (`defi/06` §6.5 QMLE).

**Contract.** `F_i` is the fitted GJR-GARCH-t return law at horizon `T`; no
separate marginal model is introduced. The copula tail parameter `ν` of `defi/07`
§7.5 is distinct from the per-asset innovation `ν_i` here and is kept separate.

---

## GAP-7 — Explicit CIR survival functions `A(t)`, `b(t)` · [derived]

`defi/05` §5.4 (D-5.4) states `S(t)=A(t)e^{-b(t)λ_0}` with `A,b` "solving Riccati
ODEs" and notes the affine structure **borrows directly** from affine short-rate
theory, i.e. the bond-price form `E[e^{-∫λ}]`. The closed form is therefore the
one already implied by the stated CIR dynamics
`dλ=κ(θ−λ)dt+ν√λ\,dW` (5.5). With

$$
\gamma=\sqrt{\kappa^2+2\nu^2},
$$

the survival functions solving the affine Riccati system are

$$
b(t)=\frac{2\big(e^{\gamma t}-1\big)}{(\gamma+\kappa)\big(e^{\gamma t}-1\big)+2\gamma},
\qquad
A(t)=\left[\frac{2\gamma\,e^{(\kappa+\gamma)t/2}}{(\gamma+\kappa)\big(e^{\gamma t}-1\big)+2\gamma}\right]^{2\kappa\theta/\nu^2}.
$$

These are the unique solutions of the Riccati ODEs generated by the affine ansatz
on (5.5); the Feller condition `2κθ≥ν²` (already required in D-5.4) keeps the
exponent well-defined and `λ_t>0`.

**Contract.** Implemented as stated; verified by the probabilistic-validity sweep
(`defi/12` §B: `S∈(0,1]`, non-increasing) and the dimensional check
(`Λ`, `b(t)λ_0` dimensionless, `defi/12` §C).

---

## GAP-8 — Short-horizon drift threshold (`μ≈0` / `μ=r_b`) · [derived]

`defi/03` §3.6 and `defi/06` §6.6 (L-DRIFT) prescribe setting `μ≈0` because drift
is not estimable over short windows (Merton, 1980), while `defi/03` §3.6 R-3.3
shows the **ratio** `C_t/B_t` has drift `μ−r_b`. The estimability argument fixes
the rule without a free threshold:

$$
\text{set the ratio drift to zero: } \mu := r_b \ \Rightarrow\ \mu-r_b=0,
\quad\text{for every liquidation-risk horizon used by the engine.}
$$

This is the conservative, estimation-robust default applied across all term-structure
tenors of `defi/03` §3.5 (the engine reports no horizon long enough for drift to be
reliably estimable per Merton, 1980), so no numeric cutoff is needed.

**Contract.** Default `μ=r_b` (zero ratio drift) everywhere in the structural and
first-passage metrics; a non-zero `μ` is admitted only as an explicit override and
is flagged when used.

---

## GAP-9 — Asset universe and factor loadings `ρ_i` · [derived + input]

`defi/07` §7.6 gives the estimation route (Kendall `τ` → `ρ=sin(πτ/2)`, D-7.4) but
not the asset set. The set is **data-determined**, not invented:

- **Asset universe** `{1,…,d}` = the distinct collateral/borrow assets actually
  present in the supplied position set; the position→asset map `a(j)` of
  `defi/08` §8.2 assigns each position to its collateral asset.
- **Correlation matrix** `R` = `sin(πτ̂/2)` applied elementwise to the empirical
  Kendall-`τ` matrix of asset log-returns (D-7.4), then repaired to the nearest
  positive-definite matrix (N-2, `defi/10` §10.4).
- **Factor loadings** `ρ_i` = the one-factor loadings consistent with `R` via
  `Corr(X_i,X_j)=√(ρ_iρ_j)` (D-7.1); for the homogeneous case `ρ_i=ρ`, otherwise
  obtained from the leading-factor decomposition of `R`.

**Contract.** The position set (and hence the universe) is a declared data input;
everything downstream (`R`, `ρ_i`, `ν`) is estimated by the already-specified
rank-based procedure.

---

## Summary table

| Gap | Item | Resolution kind | Anchored to |
|-----|------|-----------------|-------------|
| GAP-1 | `EAD_j` | derived | `defi/00` §0.2, `defi/03` §3.6 |
| GAP-2 | `R_j`, `LGD_j` | input (A6-constrained) | `defi/00` A6, `defi/05` §5.5, `defi/08` §8.2 |
| GAP-3 | `η, V, σ_window` | input | `defi/08` §8.3, L-IMP |
| GAP-4 | fire-sale slippage | derived | `defi/08` §8.2–8.3 (D-8.1) |
| GAP-5 | marginal & horizon `T` | derived + input | `defi/03` §3.5/§3.7, `defi/04`, `defi/05`, `defi/07` §7.2 |
| GAP-6 | marginal law `F_i` | derived | `defi/06` §6.6–6.7, `defi/08` §8.2 |
| GAP-7 | CIR `A(t),b(t)` | derived | `defi/05` §5.4 (D-5.4) |
| GAP-8 | short-horizon drift | derived | `defi/03` §3.6, `defi/06` §6.6 (L-DRIFT) |
| GAP-9 | asset universe, `ρ_i` | derived + input | `defi/07` §7.6 (D-7.4), `defi/10` §10.4 (N-2) |

Every **[input]** item is a declared contract with a documented default; every
**[derived]** item is forced by results already verified in `defi/12` §E. No gap is
filled by an unsupported assumption.

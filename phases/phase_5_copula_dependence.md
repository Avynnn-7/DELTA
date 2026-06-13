# Phase 5 — Dependence Structure: Copulas & Factor Model

> File: `defi/07` (copula dependence).
> Module: M-Copula.

Independent per-position risk badly understates portfolio risk because crypto
assets crash together (`defi/07`). This phase couples the marginal liquidation /
de-peg probabilities of Phases 3–4 into a joint structure via Sklar's theorem and
the one-factor model, and supplies the Vasicek closed-form loss distribution used
as a control variate and sanity check by the cascade (Phase 6).

---

## Objectives

1. Implement Sklar's separation of marginals from dependence.
2. Implement the one-factor Gaussian model, its default trigger, and the Vasicek
   large-portfolio loss CDF (analytic backbone).
3. Implement the Student-t copula with positive tail dependence — the recommended
   dependence model — retaining Gaussian only for its analytic Vasicek limit.
4. Implement rank-based dependence estimation (Kendall τ ↔ ρ) with nearest-PD
   repair.

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| Thm 7.1 | Sklar | `H(x)=C(F_1(x_1),…,F_d(x_d))`; `C` unique for continuous marginals | `defi/07` §7.1 |
| def | Gaussian copula | `C_R^Gauss(u)=Φ_R(Φ⁻¹(u_1),…,Φ⁻¹(u_d))` | `defi/07` §7.2 |
| — | One-factor model | `X_i=√ρ_i Z+√(1−ρ_i)ε_i`, `Z,ε_i~N(0,1)` | `defi/07` §7.2 |
| D-7.1 | Factor correlation | `Corr(X_i,X_j)=√(ρ_iρ_j)`; `Var(X_i)=1` | `defi/07` §7.2 |
| — | Default trigger | `default_i ⇔ X_i<Φ⁻¹(PD_i)=c_i`; preserves marginal | `defi/07` §7.2 |
| D-7.2 | Vasicek loss CDF | `P(L≤x)=Φ((√(1−ρ)Φ⁻¹(x)−Φ⁻¹(PD))/√ρ)` | `defi/07` §7.3 |
| — | Conditional default prob | `p(z)=Φ((Φ⁻¹(PD)−√ρ z)/√(1−ρ))` | `defi/07` §7.3 |
| Def 7.4 | Lower tail dependence | `λ_L=lim_{u↓0} C(u,u)/u` | `defi/07` §7.4 |
| Thm 7.2 | Gaussian `λ_L=0` | Gaussian copula asymptotically independent in extremes (L-COP) | `defi/07` §7.4 |
| def | t-copula | `C_{R,ν}^t(u)=t_{R,ν}(t_ν⁻¹(u_1),…)` | `defi/07` §7.5 |
| D-7.3 | t-copula tail dep | `λ_L=λ_U=2t_{ν+1}(−√(ν+1)√((1−ρ)/(1+ρ)))>0`; →0 as `ν→∞` | `defi/07` §7.5 |
| — | t-factor mixing | `X_i=√(ν/S)(√ρ Z+√(1−ρ)ε_i)`, `S~χ²_ν` (shared mixing) | `defi/07` §7.5 |
| D-7.4 | Kendall ↔ ρ | `ρ=sin(πτ/2)` (rank-based, robust) | `defi/07` §7.6 |

Selection mandated by `defi/07` §7.7: **t-copula with one-factor structure**;
Gaussian retained only for the Vasicek closed form.

---

## Implementation scope

- `dependence/copula` — Gaussian and Student-t copulas built on `Φ`, `Φ⁻¹`, the
  MVN/t CDF (Genz) and χ² mixing from Phase 1.
- `dependence/factor` — one-factor sampler (`O(d)` fast path, no Cholesky needed
  per `defi/10` §10.4) for both Gaussian and the t-mixing form; full-matrix path
  uses Phase 1 Cholesky + nearest-PD when a structured `R` is unavailable.
- `dependence/vasicek` — closed-form loss CDF (D-7.2) and conditional default
  probability `p(z)`; exposed as the control variate / sanity check for Phase 6.
- `dependence/estimation` — Kendall τ → ρ (D-7.4); tail-index `ν` fit by ML on
  joint exceedances or method-of-moments via (7.10); nearest-PD repair (N-2).

---

## Dependencies

- Phase 1: `Φ`, `Φ⁻¹`, MVN/t CDF, χ², Cholesky, nearest-PD.
- Phase 2: GARCH return marginals (for the marginal transform).
- Phase 3 / Phase 4: per-name marginal probabilities `PD_i` (the trigger thresholds).

## Inputs

- Marginal `PD_i` per position/asset from Phases 3–4 (**GAP-5**: the choice among
  terminal PL / first-passage PL / hazard PD and the portfolio horizon `T` must be
  fixed by an explicit contract here).
- Per-asset factor loadings `ρ_i` and the assignment of positions to the `d`
  assets (**GAP-9**: asset universe is required input; only the τ→ρ estimation
  route is given).
- Rank-correlation data (for Kendall τ); degrees of freedom `ν` (or its target).
- GARCH-implied return marginals `F_i` (**GAP-6**: innovation law and multi-horizon
  construction must be fixed before the `r_i=F_i⁻¹(U_i)` transform of Phase 6).

## Outputs

- Correlation matrix `R` (from Kendall τ, repaired to PD).
- One-factor t-copula sampler (shared `Z`, `χ²_ν` mixing, idiosyncratic `ε_i`).
- Vasicek analytic loss CDF and conditional `p(z)` (control variate for Phase 6).
- Tail-dependence coefficients `λ_L(ρ,ν)`.

---

## Validation requirements

- Factor correlation `√(ρ_iρ_j)` and `Var(X_i)=1` re-derived (`defi/12` §A-7).
- Vasicek inversion re-derived with the explicit monotonicity flip (`defi/12` §A-7).
- Gaussian `λ_L=0` (Thm 7.2) vs t-copula `λ_L>0` (D-7.3); `ν→∞` recovers Gaussian.
- Cholesky correctness for the full-matrix path (`defi/12` §A-10).
- Probabilistic validity: Vasicek CDF valid on `[0,1]`; `λ_L∈(0,1]`; correlation
  `√(ρ_iρ_j)∈[−1,1]` (`defi/12` §B).
- Dimensional sweep of the Vasicek argument (all `Φ⁻¹` terms dimensionless)
  (`defi/12` §C, eq 7.7).

## Completion criteria

- Ledger rows Thm 7.1, D-7.1, D-7.2, Thm 7.2, D-7.3, D-7.4 reach **verified**
  (`defi/12` §E).
- GAP-5, GAP-6, GAP-9 resolved via explicit input contracts for the marginal,
  marginal law, and asset universe.
- t-copula sampler and Vasicek control variate ready for the cascade engine.

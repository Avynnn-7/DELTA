# Phase 7 — Risk Measures, Allocation & End-to-End Verification

> Files: `defi/09` (risk measures), `defi/11` (audit pass 1), `defi/12`
> (verification pass 2).
> Modules: M-Risk, M-Audit, M-Verify.

The simulated loss distribution (Phase 6) is summarized into protocol-level risk
numbers, with Expected Shortfall as the primary measure on coherence grounds. This
final engine phase also discharges the full two-pass audit and verification of the
assembled system, producing the canonical output artifacts that the frontend
(Phase 8) will consume. No presentation logic appears here.

---

## Objectives

1. Implement VaR, Expected Shortfall (integral and conditional forms), the
   coherence theory, spectral framing, and Euler/ES risk-contribution allocation.
2. Implement the Monte Carlo estimators and backtests.
3. Execute the end-to-end audit (`defi/11`) and independent verification
   (`defi/12`), driving every result's master-ledger row to **verified**.
4. Emit the canonical, read-only engine output artifacts for Phase 8.

---

## Mathematical scope

| ID | Result | Statement | Source |
|----|--------|-----------|--------|
| def | VaR | `VaR_α(L)=inf{x:P(L≤x)≥α}=F_L⁻¹(α)`; not subadditive | `defi/09` §9.1 |
| D-9.1 | ES forms | `ES_α=1/(1−α)∫_α^1 VaR_u du = E[L|L≥VaR_α]` (continuity); (9.2) coherent in general | `defi/09` §9.2 |
| Thm 9.1 | Coherence | ES coherent; VaR not (subadditivity fails); ES ≥ VaR | `defi/09` §9.3 |
| — | Spectral measures | `M_φ(L)=∫₀¹ φ(u)VaR_u du`; ES is `φ=1/(1−α)1_{u≥α}` | `defi/09` §9.4 |
| D-9.2 | ES contribution | `RC_i^ES=E[L_i|L≥VaR_α]`; Euler `ρ(L)=Σ RC_i` | `defi/09` §9.5 |
| D-9.3 | VaR estimator | `VaR̂_α=L_{(⌈αN⌉)}`; asymptotically normal | `defi/09` §9.6 |
| D-9.4 | ES estimator | `EŜ_α=1/(N−⌈αN⌉) Σ_{k>⌈αN⌉} L_{(k)}`; consistent | `defi/09` §9.6 |
| — | Backtesting | Kupiec POF; Christoffersen conditional coverage; Acerbi–Székely ES Z-tests; Fissler–Ziegel joint (VaR,ES) elicitability | `defi/09` §9.7 |

Adopted choice (`defi/09` §9.8): **ES_α primary**, VaR_α reported alongside with
the coherence caveat; Euler/ES contributions for systemic-position attribution.

---

## Verification scope (`defi/11`, `defi/12`)

| Obligation | Content | Source |
|------------|---------|--------|
| Audit pass 1 | derivation/notation/measure/assumption review; limitations ledger L-1…L-DRIFT | `defi/11` §A–§H |
| Independent re-derivation | every result re-derived by a second route | `defi/12` §A |
| Probabilistic-validity sweep | probabilities `∈[0,1]`, survival monotone, densities ≥0, Feller, ES ≥ VaR | `defi/12` §B |
| Dimensional sweep | all `exp/ln/Φ/t_ν` arguments dimensionless | `defi/12` §C |
| Literature cross-checks | each boxed result reconciled with a primary source | `defi/12` §D |
| Master ledger | two-pass **verified** status for every result | `defi/12` §E |
| Error budget | `ε_num ≪ ε_MC ≪ ε_param` end-to-end | `defi/10` §10.7 |

---

## Implementation scope

- `risk/var_es` — VaR (9.1), ES integral form (9.2) and conditional form (9.3);
  ES ≥ VaR enforced; spectral framing.
- `risk/allocation` — Euler/ES risk contributions `RC_i^ES` from the per-scenario
  per-position losses of Phase 6 (average `L_i` over the worst `(1−α)N` scenarios).
- `risk/estimators` — empirical-quantile VaR (D-9.3), tail-average ES (D-9.4) with
  importance-sampling-reduced standard errors (Phase 6).
- `risk/backtest` — Kupiec, Christoffersen, Acerbi–Székely / Fissler–Ziegel.
- `validation/audit` — automated checks mirroring `defi/11` §A–§G.
- `validation/verify` — independent re-derivation harness and the §B/§C/§D sweeps;
  emits the master ledger (`defi/12` §E).
- `risk/artifacts` — serializes the canonical engine outputs (read-only) for the
  frontend: per-position metrics, survival curves, loss distribution, VaR/ES, and
  ES contributions.

The coherence theorem is backed by the explicit VaR non-subadditivity
counterexample (`defi/12` §A-9), which must be present as a regression test.

---

## Dependencies

- Phase 6: loss distribution `{L^{(s)}}` and per-position `L_i^{(s)}`.
- Phases 1–5: all modules, for the end-to-end verification sweep.

## Inputs

- Simulated loss distribution and per-position losses (Phase 6).
- Confidence level `α` (e.g. 0.99); realized-outcome series for backtesting.

## Outputs

- `ES_α` (primary), `VaR_α` (secondary), spectral measures.
- Per-position ES contributions / concentration ranking.
- Backtest statistics (coverage, ES Z-tests).
- The completed master verification ledger and error-budget report.
- The canonical read-only output artifact set consumed by Phase 8.

---

## Validation requirements

- ES coherence; VaR non-subadditivity counterexample reproduced (`defi/12` §A-9).
- Euler allocation additivity `Σ RC_i=ES_α` (`defi/12` §A-9, D-9.2).
- VaR/ES estimator consistency and asymptotic normality (D-9.3, D-9.4).
- Backtests pass on validation data (Kupiec/Christoffersen/Acerbi–Székely).
- Every master-ledger row (`defi/12` §E) reaches **verified**; the registered
  limitations (L-1, L-COP, L-IMP, L-6, L-7, L-V1, L-DRIFT) are documented as
  accepted caveats, not silent assumptions.

## Completion criteria

- Ledger rows D-9.1–D-9.4, Thm 9.1 reach **verified** (`defi/12` §E).
- The complete two-pass verification ledger is **verified** for the assembled
  engine; error-budget ordering demonstrated.
- Canonical engine output artifacts are emitted and frozen as the **only**
  interface to the frontend (no engine code reachable from `web/`).

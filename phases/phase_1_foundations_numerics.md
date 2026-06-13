# Phase 1 — Foundations: Conventions & Numerical Primitives

> Files: `defi/00` (notation & conventions), `defi/10` (numerical methods).
> Modules: M0 (conventions), M-Num (Φ/Φ⁻¹, special functions, RNG, linear algebra).

Every downstream metric is a function of the standard normal CDF `Φ` and its
quantile `Φ⁻¹`, evaluated in the deep tail, plus the unit conventions of
`defi/00`. Nothing structural can be computed correctly until these primitives
meet the accuracy requirements of `defi/10`. This phase builds no financial
model — only the exact substrate the models stand on.

---

## Objectives

1. Encode the notation, units, and probabilistic conventions of `defi/00` as the
   single shared vocabulary for the engine.
2. Implement tail-accurate `Φ`, `Φ⁻¹`, and supporting special functions to the
   accuracy mandated by N-1.
3. Provide the random-number and linear-algebra primitives required by the later
   sampling and dependence layers (N-2, N-3, D-10.1).
4. Establish the dimensional and probabilistic-validity checking utilities used by
   every later phase (`defi/12` §B, §C).

---

## Mathematical scope

| Item | Statement | Source |
|------|-----------|--------|
| Probability/measure conventions | `(Ω,F,(F_t),P)`; `P` (physical) vs `Q` (pricing) separation | `defi/00` §0.1 |
| Core symbols & units | symbol table; units carried for dimensional checks | `defi/00` §0.2, §0.4 |
| Log-return & annualization | `r=ln(P_{t+Δ}/P_t)`; `Var=σ²Δ`; `σ_ann=σ_period√n` | `defi/00` §0.3 |
| Sign convention | DD/DTL "larger = safer", `PD=Φ(−DD)`; `α`=confidence | `defi/00` §0.3 |
| `Φ` (N-1) | `Φ(x)=½erfc(−x/√2)`; Cody rational-Chebyshev `erf`; `erfc` in left tail | `defi/10` §10.1 |
| `Φ⁻¹` (N-1) | Wichura AS 241 (~1e-16) or Acklam+Halley / Moro tail accuracy | `defi/10` §10.2 |
| Cholesky (D-10.1) | `R=LL^T`, `X=Lz ⇒ Cov(X)=R`; SPD existence/uniqueness | `defi/10` §10.4 |
| Nearest-PD (N-2) | repair empirical `R` to nearest positive-definite (Higham) / eigenvalue floor | `defi/10` §10.4 |
| Parallel RNG (N-3) | counter-based Philox substreams; normal-by-inversion | `defi/10` §10.5 |
| Special functions | incomplete gamma / χ² (Lentz continued fractions); MVN/t CDF (Genz QMC) | `defi/10` §10.6 |
| Stability rules | log-space arithmetic, `log1p`/`expm1`, `erfc` over `1−erf` | `defi/10` §10.6 |
| Error budget | `ε ≤ ε_model+ε_param+ε_MC+ε_num`; target `ε_num ≪ ε_MC ≪ ε_param` | `defi/10` §10.7 |

The 1-D and 2-D root-finders (Newton–Raphson, Brent) of `defi/10` §10.3 are part
of M-Num but are exercised first in later calibration phases; only the scalar
safeguarded solver (Brent) needed by no Phase-1 result is deferred to its first
consumer.

---

## Implementation scope

- `conventions/` — constants (annualization factors incl. 24/7 `n_yr`), unit tags,
  measure tags (`P`/`Q`), sign conventions. No logic beyond definitions.
- `numerics/normal` — `erf`, `erfc`, `Φ`, `Φ⁻¹` with tail-accurate paths (N-1).
- `numerics/special` — incomplete gamma, χ² CDF/quantile, MVN/t CDF via Genz.
- `numerics/rng` — Philox counter-based generator, inversion-based normal draws.
- `numerics/linalg` — Cholesky factorization, nearest-PD repair.
- `numerics/stability` — `log1p`/`expm1`/log-space helpers.
- `validation/dimensional` — argument-dimensionlessness checker (`defi/12` §C).
- `validation/probabilistic` — range/monotonicity/non-negativity assertions
  (`defi/12` §B).

---

## Dependencies

None (root of the dependency graph). Consumes only `defi/00` and `defi/10`.

## Inputs

- The specifications `defi/00`, `defi/10`.
- Reference values for accuracy testing (high-precision `Φ`, `Φ⁻¹`).

## Outputs

- A numerical-primitive library with documented accuracy guarantees.
- Shared conventions/units module.
- Dimensional- and probabilistic-validity utilities consumed by Phases 2–7.

---

## Validation requirements

- `Φ`, `Φ⁻¹` relative error in the tail meets N-1 (erfc-based; Wichura/Moro);
  absolute-error A&S 7.1.26 explicitly rejected for deep tails (`defi/10` §10.1).
- Cholesky correctness `Cov(Lz)=R` re-derived (`defi/12` §A-10).
- Nearest-PD repair produces an SPD matrix (N-2).
- Philox substreams reproducible and decorrelated across threads (N-3).
- χ² / incomplete-gamma routines validated against the closed forms used by the
  CIR survival and t-copula mixing variable (`defi/05` §5.4, `defi/07` §7.5).

## Completion criteria

- N-1, N-2, N-3, D-10.1 implemented and their `defi/12` §E ledger rows
  (D-10.1) reach **verified**.
- Dimensional and probabilistic-validity utilities operational and adopted as the
  test substrate for all later phases.
- Error-budget instrumentation in place so `ε_num` can be shown subordinate to
  `ε_MC` and `ε_param` downstream (`defi/10` §10.7).

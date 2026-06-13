# Phase 8 — Presentation & User Interaction (`web/`)

> Source: the dashboard flows explicitly referenced by the mathematics —
> position inspector (`defi/03` §3.5), term-structure / survival curve
> (`defi/05` §5.8), contagion-map / concentration view (`defi/09` §9.5).
> Modules: none. This phase implements **no mathematics**.

The frontend consumes the canonical, read-only output artifacts produced by
Phase 7 and renders them. All UI code, assets, pages, components, and supporting
frontend infrastructure reside inside `web/`. No calculation is replicated here;
the layer is a pure view over precomputed engine outputs.

---

## Objectives

1. Render the engine's per-position, per-asset, and portfolio risk artifacts.
2. Surface exactly the views the mathematics names — nothing speculative.
3. Enforce the architectural boundary: zero mathematical logic in `web/`; the
   frontend imports no engine module and performs no recomputation.

---

## Mathematical scope

None. Per constraint 6, no mathematical logic is implemented in the frontend.
Per constraint 7, the frontend consumes engine outputs rather than computing them.

The only "scope" is the set of quantities to display, each already computed
upstream:

| View | Displays (precomputed) | Produced by | Referenced in |
|------|------------------------|-------------|----------------|
| Position inspector | DTL, first-passage PL (primary), terminal PL, `δ*`, timing density, term structure `{PL(T)}` | Phase 3 | `defi/03` §3.5 |
| Survival / term-structure | survival curve `S(t)`, de-peg `PD(t)` | Phase 4 | `defi/05` §5.8 |
| Portfolio risk | loss distribution, `VaR_α`, `ES_α` | Phases 6–7 | `defi/09` |
| Contagion / concentration map | per-position ES contributions `RC_i^ES` | Phase 7 | `defi/09` §9.5 |

---

## Implementation scope (all inside `web/`)

- `web/` data-consumption layer — reads the frozen Phase 7 artifact schema
  (per-position metrics, survival curves, loss distribution, VaR/ES, ES
  contributions). Read-only; no fetching of raw market/on-chain data and no
  computation.
- `web/` views — position inspector, survival/term-structure view, portfolio loss
  distribution with VaR/ES markers, contagion/concentration map.
- `web/` components and assets — presentational only.

No estimator, sampler, copula, cascade, or risk-measure code is permitted in
`web/`; any such need indicates the artifact is missing from Phase 7 and must be
added there, not in the frontend.

---

## Dependencies

- Phase 7: the canonical read-only output artifact set (the sole interface).

## Inputs

- The Phase 7 artifact schema instances (per-position metrics, survival curves,
  loss distribution, VaR/ES, ES contributions).

## Outputs

- A web application in `web/` presenting the four mandated views.

---

## Validation requirements

- Every displayed value equals the corresponding Phase 7 artifact value with no
  transformation beyond formatting (contract/schema conformance tests).
- Static and dependency checks confirm `web/` imports no engine module and
  contains no mathematical computation (boundary enforcement).
- The four named views render solely from the artifact set; no view requires a
  quantity absent from the schema.

## Completion criteria

- All four mathematically-referenced views render from Phase 7 artifacts only.
- Boundary verified: no mathematical logic and no engine imports inside `web/`;
  the frontend is fully isolated from the core engine.
- Artifact schema conformance tests pass; displayed numbers match engine outputs
  exactly.

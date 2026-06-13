# 11 — Audit Pass 1: Derivation, Notation, Assumption & Gap Review

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

This is the **first** of two independent review passes. Its mandate (from the brief): verify
derivations step-by-step, check notation consistency, validate assumptions, and identify logical
gaps, unjustified approximations, and unsupported claims. Pass 2
([12](12_verification_pass_2.md)) then re-derives critical results independently. Each finding
is recorded with a status and a resolution.

Legend: ✅ verified · ⚠️ caveat/limitation (legitimate, documented) · 🔧 fixed in-text · ❗ open item.

---

## §A. Notation consistency

| Check | Finding | Status |
|-------|---------|--------|
| Single symbol per concept | $\lambda$ is overloaded: hazard rate ([05](05_reduced_form_hazard.md)), EWMA decay ([06](06_volatility_estimation.md)), Kyle's lambda ([08](08_monte_carlo_cascade.md)). | ⚠️ Disambiguated by subscripts ($\lambda_{\text{EWMA}}$, $\lambda_{\text{Kyle}}$) and local context; flagged here so no cross-file confusion. |
| $\Phi$ argument sign | DD/DTL use $\mathrm{PD}=\Phi(-\mathrm{DD})$ consistently; sign convention "larger = safer" holds in [02](02_merton_structural_model.md)–[04](04_first_passage_barrier.md). | ✅ |
| $\alpha$ = confidence (not tail mass) | Used consistently in [09](09_risk_measures.md); tail is $1-\alpha$. | ✅ |
| Drift symbol | $\mu$ (physical) vs $r$ (risk-free) separated; risk-neutral variant explicitly marked in [02](02_merton_structural_model.md) §2.3. | ✅ |
| $m=\mu-\tfrac12\sigma^2$ | Defined once (4.1) and reused; matches the log-drift in (1.3). | ✅ |
| Units | Dimensional table ([00](00_notation_and_conventions.md) §0.4) consistent with every $\Phi/\exp/\ln$ argument. | ✅ (re-checked numerically in Pass 2 §C) |

---

## §B. Measure consistency ($\mathbb P$ vs $\mathbb Q$)

| Item | Finding | Status |
|------|---------|--------|
| A-2: Merton PD | Physical PD (2.3) uses $\mu_V$; risk-neutral $d_2$ form (for *pricing*) uses $r$. Both stated, not conflated. | ✅ |
| Risk *measurement* under $\mathbb P$ | VaR/ES/PD all computed under $\mathbb P$; only calibration to traded prices (CDS spread (5.6), equity-as-option (2.5)) touches $\mathbb Q$. | ✅ Correct separation. |
| Girsanov equivalence | Almost-sure statements (e.g. first-passage event) are measure-independent; used legitimately. | ✅ |

---

## §C. Derivation-by-derivation checks

| ID | Result | Check performed | Status |
|----|--------|-----------------|--------|
| D-1.1 | GBM solution | Itô on $\ln P$; price-level cancellation in drift & diffusion verified termwise. | ✅ |
| D-1.3 | $\mathbb E[P_t]=P_0e^{\mu t}$ | Log-normal mean $e^{m+s^2/2}$ with $m=(\mu-\tfrac12\sigma^2)t$, $s^2=\sigma^2 t$ ⇒ $+\tfrac12\sigma^2 t$ cancels $-\tfrac12\sigma^2 t$. | ✅ Volatility drag correctly placed. |
| D-2.1 | Merton PD | Standardization of $\ln V_T$; sign of barrier term; $=\Phi(-\mathrm{DD})$. | ✅ |
| D-2.2 | Inversion system | Two equations (BS + Itô-vol), two unknowns; delta identity $\partial S/\partial V=\Phi(d_1)$. | ✅ Solvability deferred to Pass 2 §A-2 (Jacobian non-singularity). |
| D-3.1 | Liquidation prob | Same standardization with barrier $B/\ell$; reduces to DTL form via $H_0=\ell C_0/B$. | ✅ |
| D-3.2 | Drop-to-liquidation | Pure accounting; $\delta^\ast=1-1/H_0$; boundary $H_0=1\Rightarrow0$. | ✅ |
| **G-3** | Terminal vs path | (3.3) is a **terminal** probability; liquidation is path-dependent ⇒ (3.3) **understates** risk. | 🔧 Resolved by first-passage (4.5) as the *primary* metric; inequality $\mathbb P(\tau_b\le T)\ge\mathbb P(X_T\le b)$ proved. |
| D-4.1 | First-passage CDF | Reflection + Girsanov tilt; checked against driftless limit, terminal-term match, $H_0\to1$ limit. | ✅ Independent re-derivation in Pass 2 §A-4. |
| D-4.2 | IG density | $d/dT$ of (4.5); matches Borodin–Salminen. | ✅ |
| **A-4** | Defective IG | For $m>0$, $\mathbb P(\tau<\infty)=e^{2mb/\sigma^2}<1$; density integrates to <1. | ⚠️ Correct & essential; explicitly verified Pass 2 §A-4 (R-4.3). |
| D-5.1/5.2 | Survival–hazard, Cox | $S=e^{-\Lambda}$ via ODE; Cox construction with $E\sim\mathrm{Exp}(1)$. | ✅ |
| D-5.5 | Credit triangle | First-order par-spread equality $s\approx\lambda(1-R)$. | ⚠️ Approximation — exact leg-PV form noted; flagged as such. |
| D-6.1 | RV → QV | Quadratic-variation convergence; constant-$\sigma$ limit $\sigma^2T$. | ✅ |
| D-6.3 | GARCH long-run var | Stationarity expectation ⇒ $\bar\sigma^2=\omega/(1-\alpha-\beta)$; $\alpha+\beta<1$. | ✅ |
| D-7.1 | Factor correlation | $\mathrm{Var}(X_i)=1$; $\mathrm{Corr}=\sqrt{\rho_i\rho_j}$ via independence. | ✅ |
| D-7.2 | Vasicek loss CDF | Conditional indep ⇒ $p(z)$; invert decreasing $p$; **monotonicity flip** of inequality. | ✅ Flip is the subtle step; re-derived Pass 2 §A-7. |
| Thm 7.2 | Gaussian $\lambda_L=0$ | Cited (Embrechts et al., 2002; Sibuya, 1960). | ✅ ⚠️ Drives limitation L-COP. |
| D-7.3 | t-copula $\lambda_L>0$ | Formula (7.10); $\nu\to\infty$ limit →0. | ✅ |
| D-8.3 | MC CLT | SE $=\varsigma/\sqrt N$; finite-variance proviso. | ✅ |
| D-9.1 | ES forms | (9.2) integral vs (9.3) conditional; equal under continuity. | ✅ Atom caveat documented. |
| Thm 9.1 | ES coherent, VaR not | Cited (Artzner et al., 1999; Acerbi & Tasche, 2002). | ✅ Counterexample in Pass 2 §A-9. |
| D-9.2 | ES contribution | Euler + homogeneity ⇒ tail conditional expectation. | ✅ |
| D-10.1 | Cholesky | $\mathrm{Cov}(L\mathbf z)=LL^\top=R$. | ✅ |

No derivation was found to be **incorrect**. Items G-3 and the approximations (D-5.5) are
resolved or explicitly flagged rather than left implicit.

---

## §D. Assumption validation

Each load-bearing assumption (A1–A7, [00](00_notation_and_conventions.md) §0.5) is assessed for
*validity in the DeFi setting* and whether the document handles its violation honestly:

| # | Assumption | Valid in crypto? | Handled? |
|---|-----------|------------------|----------|
| A1 | Frictionless/continuous trading | ❌ (gas, slippage, fragmented liquidity) | ✅ Price impact ([08](08_monte_carlo_cascade.md)); idealization flagged |
| A2 | GBM constant $\sigma$ | ❌ (clustering, regimes) | ✅ Time-varying $\hat\sigma$ ([06](06_volatility_estimation.md)) |
| A3 | Gaussian / no jumps | ❌ (heavy tails, de-peg jumps) | ⚠️ L-1: t-copula tails ([07](07_copula_dependence.md)), EVT ([05](05_reduced_form_hazard.md)); jump-diffusion noted as future work |
| A4 | Default only at $T$ | ❌ (continuous liquidation) | ✅ First passage ([04](04_first_passage_barrier.md)) |
| A5 | One factor / Gaussian copula | ❌ (multi-sector, tail co-movement) | ✅ t-copula + multi-factor noted ([07](07_copula_dependence.md)) |
| A6 | Deterministic recovery | ❌ (stochastic, MEV-dependent) | ⚠️ L-6: stochastic-recovery extension noted |
| A7 | Oracle=true, instant liquidation | ❌ (Chainlink latency, keeper/MEV) | ⚠️ L-7: latency/MEV in [08](08_monte_carlo_cascade.md); idealized bound |

**Verdict:** every materially-violated assumption is either relaxed by a more general model in
the document or explicitly logged as a named limitation. None is silently assumed away.

---

## §E. Registered limitations (the "honest inadequacies" ledger)

| ID | Limitation | Where it bites | Principled response in-text |
|----|-----------|----------------|------------------------------|
| **L-1** | Gaussian tails understate extremes | every structural PD/PL | t-copula tails, EVT de-peg sizing, KMV-style empirical mapping noted |
| **L-COP** | Gaussian copula has **zero** tail dependence (Thm 7.2) | portfolio cascade | **t-copula adopted** (D-7.3); Gaussian kept only for Vasicek closed form |
| **L-IMP** | Price-impact kernel fragile; liquidity vanishes in crashes | cascade severity ([08](08_monte_carlo_cascade.md)) | stress $\eta$; scenario analysis; flagged not hidden |
| **L-6** | Deterministic recovery | EAD·LGD losses | stochastic recovery noted |
| **L-7** | Oracle latency / MEV / keeper dynamics | liquidation timing | idealized first-passage bound; latency model noted |
| **L-V1** | Microstructure noise biases RV | $\sigma$ input | noise-robust RV / optimal sampling ([06](06_volatility_estimation.md)) |
| **L-DRIFT** | $\mu$ poorly estimable short-horizon | DD/DTL | set $\mu\approx0$ conservatively (Merton, 1980) |

---

## §F. Model-selection justifications (are the "preferred" choices defended?)

| Decision | Defensible? | Basis |
|----------|-------------|-------|
| Structural for collateral, reduced-form for de-pegs | ✅ | each applied where its assumptions hold ([03](03_distance_to_liquidation.md) vs [05](05_reduced_form_hazard.md)) |
| First passage over terminal Merton | ✅ | liquidation is path-dependent ([04](04_first_passage_barrier.md)) |
| t-copula over Gaussian copula | ✅ | tail dependence (Thm 7.2 vs D-7.3); empirical superiority (Demarta & McNeil, 2005) |
| GJR-GARCH-$t$ over plain GARCH | ✅ | asymmetry + heavy tails ([06](06_volatility_estimation.md) §6.7) |
| ES over VaR (primary) | ✅ | coherence (Thm 9.1); FRTB |
| Importance sampling for tail | ✅ | rare-event efficiency (Glasserman & Li, 2005) |

All "preferred" selections cite empirical and/or theoretical grounds; none rests on convenience.

---

## §G. Numerics review

| Item | Finding | Status |
|------|---------|--------|
| Tail accuracy of $\Phi,\Phi^{-1}$ | Liquidation probs are deep-tail ⇒ `erfc`-based + Wichura/Moro required (N-1). | 🔧 Specified in [10](10_numerical_methods.md). |
| Empirical $R$ not PD | Repair to nearest PD (N-2). | 🔧 Specified. |
| Parallel RNG correctness | Counter-based substreams avoid correlation across threads (N-3). | 🔧 Specified. |
| Error budget ordering | $\epsilon_{\text{num}}\ll\epsilon_{\text{MC}}\ll\epsilon_{\text{param}}$ targeted. | ✅ (10.1) |

---

## §H. Open items carried to Pass 2

1. Independent re-derivation of **D-4.1** (first passage) from the heat equation / Girsanov,
   plus explicit **defect-mass** check (A-4 / R-4.3).
2. Independent re-derivation of the **Vasicek** inversion **D-7.2** incl. the monotonicity flip.
3. Explicit **VaR non-subadditivity counterexample** (supports Thm 9.1).
4. Full **dimensional sweep** of all boxed equations.
5. **Probabilistic-validity** checks: every probability in $[0,1]$, survival monotone, density
   non-negative, Feller condition for CIR.

These are discharged in [12 — Verification Pass 2](12_verification_pass_2.md).

---

Previous: [10 — Numerical Methods](10_numerical_methods.md) · Next: [12 — Verification Pass 2](12_verification_pass_2.md)

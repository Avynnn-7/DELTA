# 05 — Reduced-Form (Intensity) Models: De-Peg & Term-Structure Risk

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

Structural models ([02](02_merton_structural_model.md)–[04](04_first_passage_barrier.md)) tie
default to an observable barrier. For events with **no clean asset barrier** — chiefly
**stablecoin de-pegs** and protocol/credit events — the **reduced-form** (intensity) approach
of Jarrow & Turnbull (1995), Lando (1998), and Duffie & Singleton (1999) is the academically
defensible choice: default is the first jump of a point process with stochastic intensity. This
file develops survival/hazard theory and its calibration.

---

## 5.1 Hazard rate, cumulative hazard, survival

Let $\tau$ be the (random) event time. Define on $[0,\infty)$:

**Definition 5.1 (Survival function).** $S(t) = \mathbb{P}(\tau > t)$.

**Definition 5.2 (Hazard rate).** The instantaneous event rate given survival,

$$
\lambda(t) = \lim_{\Delta\downarrow0}\frac{\mathbb{P}(t < \tau \le t+\Delta \mid \tau > t)}{\Delta}
= \frac{f(t)}{S(t)} = -\frac{d}{dt}\ln S(t), \tag{5.1}
$$

where $f$ is the density of $\tau$ (Cox & Oakes, 1984, §2). The last equality follows from
$f(t) = -S'(t)$ and the chain rule. ✔

**Derivation of the survival–hazard relation.** Integrating (5.1),
$\ln S(t) - \ln S(0) = -\int_0^t \lambda(s)\,ds$ with $S(0)=1$, hence

$$
\boxed{\ S(t) = \exp\!\Big(-\int_0^t \lambda(s)\,ds\Big) = e^{-\Lambda(t)},\quad \Lambda(t):=\int_0^t\lambda(s)\,ds.\ } \tag{5.2}
$$

This is **Result D-5.1**. The cumulative hazard $\Lambda(t)$ is dimensionless ✔ (since
$\lambda$ has units yr$^{-1}$, [00](00_notation_and_conventions.md) §0.4).

**Default probability over $[0,t]$:** $\mathrm{PD}(t) = 1 - S(t) = 1 - e^{-\Lambda(t)}$.

---

## 5.2 The Cox process (doubly-stochastic) formulation

In the general reduced-form model (Lando, 1998), $\tau$ is the first jump of a **Cox process**:
conditional on the intensity path $\{\lambda_s\}$, jumps are Poisson. The fundamental survival
formula generalizes (5.2) to an expectation over intensity paths:

$$
S(t) = \mathbb{E}\!\left[\exp\!\Big(-\int_0^t \lambda_s\,ds\Big)\right]. \tag{5.3}
$$

**Construction (canonical).** Let $E\sim\mathrm{Exp}(1)$ be independent of $\{\lambda_s\}$, and
set $\tau = \inf\{t: \Lambda(t) \ge E\}$. Then
$\mathbb{P}(\tau>t\mid\{\lambda_s\}) = \mathbb{P}(E>\Lambda(t)) = e^{-\Lambda(t)}$, and taking
expectations gives (5.3). This is **Result D-5.2** (verified in
[12](12_verification_pass_2.md) §A-5). The construction is also the basis of the standard
*simulation* of default times (draw $E$, integrate $\lambda$ until threshold) used in
[08](08_monte_carlo_cascade.md).

This formula is **structurally identical** to the bond-pricing formula
$P(0,t)=\mathbb{E}[e^{-\int_0^t r_s ds}]$, which is why affine intensity models borrow directly
from affine short-rate theory (§5.4).

---

## 5.3 Constant and piecewise-constant intensity

**Constant $\lambda$:** $S(t) = e^{-\lambda t}$, so $\tau\sim\mathrm{Exp}(\lambda)$ with mean
$1/\lambda$ (the expected time to a de-peg). Memoryless — a strong assumption, but a useful
baseline.

**Piecewise-constant (the calibration workhorse).** Given a tenor grid
$0=t_0<t_1<\dots<t_K$ with $\lambda(t)=\lambda_k$ on $(t_{k-1},t_k]$,

$$
\Lambda(t_K) = \sum_{k=1}^{K}\lambda_k(t_k - t_{k-1}),\qquad
S(t_j) = \exp\!\Big(-\sum_{k=1}^{j}\lambda_k\,\Delta t_k\Big). \tag{5.4}
$$

This **bootstrap** form (Result D-5.3) lets us strip $\lambda_k$ sequentially from a term
structure of de-peg quotes/spreads (§5.5).

---

## 5.4 Affine intensity (CIR) for stochastic, mean-reverting risk

To let de-peg risk vary stochastically and revert, model $\lambda_t$ as a CIR process
(Cox, Ingersoll & Ross, 1985):

$$
d\lambda_t = \kappa(\theta - \lambda_t)\,dt + \nu\sqrt{\lambda_t}\,dW_t,\qquad 2\kappa\theta\ge\nu^2, \tag{5.5}
$$

where the **Feller condition** $2\kappa\theta\ge\nu^2$ keeps $\lambda_t>0$ (Feller, 1951) — a
hard requirement since a negative intensity is meaningless (probabilistic-validity check, Pass 2
§B). The affine structure yields closed-form survival
$S(t)=\mathbb{E}[e^{-\int_0^t\lambda_s ds}] = A(t)e^{-Bb(t)\lambda_0}$ with $A,b$ solving Riccati
ODEs (Duffie, Pan & Singleton, 2000). Result D-5.4; the Riccati solution is stated and
dimensionally checked in [12](12_verification_pass_2.md) §A-5.

---

## 5.5 Calibration from spreads (CDS-style / de-peg insurance)

The classic **credit-triangle** approximation links a par credit spread $s$ to hazard and
recovery. Under constant $\lambda$ and recovery $R$, equating protection and premium legs of a
CDS gives, to first order (Hull & White, 2000; O'Kane, 2008),

$$
\boxed{\ \lambda \approx \frac{s}{1-R}.\ } \tag{5.6}
$$

This is **Result D-5.5**. *Derivation sketch* (full version in
[12](12_verification_pass_2.md) §A-5): the premium leg pays $s$ per unit time while alive
($\approx s\,S(t)$), the protection leg pays $(1-R)$ at default (density
$\approx \lambda S(t)$); over a short horizon, par ($\text{PV}_{\text{prem}}=\text{PV}_{\text{prot}}$)
gives $s \approx \lambda(1-R)$. For DeFi, the analog of $s$ is the cost of de-peg protection
(e.g. options/insurance market premia, or implied from depeg-swap quotes). Where no such market
exists, $\lambda$ is estimated statistically (§5.6).

---

## 5.6 Statistical estimation of de-peg intensity

Absent a protection market, calibrate $\lambda$ to realized peg-deviation data:

- **Threshold-exceedance / Poisson MLE.** Treat de-peg events ($|P_t-1|>\theta$) as a Poisson
  process; the MLE of a constant intensity is
  $\hat\lambda = (\#\text{events})/(\text{total exposure time})$ — the standard occurrence-rate
  estimator (Cox & Lewis, 1966). Result R-5.6 (Pass 2).
- **Peace-of-mind via extreme value theory.** Model the *magnitude* of deviations with a
  Generalized Pareto tail (Pickands, 1975; peaks-over-threshold, Embrechts, Klüppelberg &
  Mikosch, 1997) to capture de-peg *severity*, separate from frequency $\lambda$. This is the
  academically correct treatment of the heavy-tailed de-peg size and is recommended over
  assuming Gaussian deviations (limitation L-1).
- **Logistic hazard (discrete time).** For per-epoch de-peg probability conditioned on
  covariates (peg deviation, reserve ratio, volume), a discrete-time logistic hazard
  (Shumway, 2001) is defensible and maps cleanly to a fast inference path.

---

## 5.7 Bridge: structural ⇒ implied hazard (consistency)

The first-passage density (D-4.2) implies a hazard for the *structural* liquidation event via
$\lambda^{\mathrm{struct}}(t) = f_{\tau_b}(t)/S_{\tau_b}(t)$ with
$S_{\tau_b}(t)=1-\mathbb P(\tau_b\le t)$ from (4.5). This lets the engine express *both*
volatile-collateral liquidation and stablecoin de-peg on a **common hazard scale**, enabling a
unified survival curve per position/asset. Consistency of the two routes is checked in
[12](12_verification_pass_2.md) §A-5 (Result R-5.7).

---

## 5.8 Why reduced-form (and how it complements structural)

- **No artificial barrier.** De-pegs are driven by reserve quality, liquidity, and confidence —
  not a collateral threshold — so an intensity model is the *honest* representation
  (Jarrow & Turnbull, 1995).
- **Term structure for free.** (5.2)/(5.4) yield a full survival curve, matching the
  multi-horizon dashboard (Flow D).
- **Calibration-driven.** Reduced-form is designed to *fit observed prices/data*, the opposite
  philosophy to structural's *explain from fundamentals*. Using **structural for collateral
  liquidation** ([03](03_distance_to_liquidation.md)) and **reduced-form for de-pegs** (here)
  applies each where its assumptions hold — the rigorous choice.

---

## 5.9 Assumptions and limitations

| Assumption | Limitation | Mitigation |
|------------|-----------|------------|
| $\tau$ is totally inaccessible (no warning) | De-pegs sometimes have observable precursors (reserve drain) | Add covariates (logistic/Cox regression, §5.6) |
| Constant/affine $\lambda$ | Real intensity is regime-switching | Piecewise-constant (5.4) or regime models |
| Independence of $E$ and $\{\lambda_s\}$ | Wrong-way risk (intensity ↑ with exposure) | Correlated intensity in copula layer ([07](07_copula_dependence.md)) |
| Deterministic recovery $R$ (A6) | Recovery is stochastic, correlated with default | Stochastic-recovery extension; L-6 in [11](11_audit_pass_1.md) |
| Credit-triangle (5.6) is first-order | Breaks for large spreads / long tenor | Use full leg PVs (O'Kane, 2008); exact form in Pass 2 |

---

## 5.10 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| D-5.1 | Survival–hazard | $S(t)=e^{-\Lambda(t)}$, $\lambda=-\frac{d}{dt}\ln S$ |
| D-5.2 | Cox survival | $S(t)=\mathbb E[e^{-\int_0^t\lambda_s ds}]$ |
| D-5.3 | Bootstrap | piecewise-constant (5.4) |
| D-5.4 | CIR affine survival | $S(t)=A(t)e^{-b(t)\lambda_0}$, Feller $2\kappa\theta\ge\nu^2$ |
| D-5.5 | Credit triangle | $\lambda\approx s/(1-R)$ |
| R-5.6 | Poisson MLE | $\hat\lambda=\#\text{events}/\text{exposure time}$ (Pass 2) |
| R-5.7 | Structural↔hazard bridge | $\lambda^{\mathrm{struct}}=f_{\tau_b}/S_{\tau_b}$ (Pass 2) |

---

Previous: [04 — First-Passage](04_first_passage_barrier.md) · Next: [06 — Volatility Estimation](06_volatility_estimation.md)

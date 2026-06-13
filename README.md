# DELTA — Crypto Default & Contagion Risk Analyser

A quantitative risk engine for over-collateralized DeFi lending and stablecoin systems.
DELTA estimates single-position liquidation risk, term-structure de-peg risk, and
portfolio-level loss under correlated, contagious liquidation cascades, then aggregates
these into coherent risk measures.

All measurement is performed under the physical measure $\mathbb{P}$; the risk-neutral
measure $\mathbb{Q}$ is used only where a contingent claim is priced or calibrated. The
distinction is enforced throughout.

---

## 1. Project Overview

DELTA translates the established structural and reduced-form credit-risk apparatus into the
on-chain lending and stablecoin setting and supplies the risk-aggregation theory needed to
quantify protocol-level risk. The system answers three questions:

1. **Single position** — how close is a collateralized position to liquidation, and what is
   its probability of liquidation over a horizon $T$?
2. **Term structure** — for a pegged asset, what is the probability of a de-peg by each
   maturity $t$?
3. **Portfolio** — what is the distribution of aggregate loss $L$ when positions default in
   a correlated, contagious manner, and what are the resulting $\mathrm{VaR}_\alpha$ and
   $\mathrm{ES}_\alpha$?

The repository separates the mathematical engine (`engine/`), independent validation
(`validation/`), the formal mathematical reference (`defi/`), and a read-only presentation
layer (`web/`).

---

## 2. Mathematical Objective

Given a portfolio of $d$ collateralized positions with prices $(P_t^i)$, the system estimates
the distribution of horizon loss

$$
L = \sum_{i=1}^{d} \mathrm{LGD}_i \cdot \mathrm{EAD}_i \cdot \mathbf{1}\{\tau_i \le T\} \; + \; (\text{contagion-induced slippage losses}),
$$

where $\tau_i$ is the liquidation/default stopping time of position $i$, and to summarize
this distribution by coherent risk measures. The primary deliverables are the survival
functions $S_i(t) = \mathbb{P}(\tau_i > t)$, the loss distribution of $L$, and the risk
functionals $\mathrm{VaR}_\alpha$, $\mathrm{ES}_\alpha$ with their per-position Euler
contributions.

---

## 3. Methodology

### 3.1 Price process

Asset log-prices follow geometric Brownian motion,
$dP_t = \mu P_t\,dt + \sigma P_t\,dW_t$, so log-returns over $[t, t+\Delta]$ are exactly
Gaussian, $\ln(P_{t+\Delta}/P_t) \sim \mathcal{N}\big((\mu - \tfrac12\sigma^2)\Delta,\,\sigma^2\Delta\big)$.
This is the input process for the structural models. Marginal returns in the simulation use a
standardized Student-$t$ to admit heavier tails than the Gaussian baseline.

### 3.2 Structural single-name risk (Merton; Black–Cox)

Liquidation is modeled structurally. The health factor $H_t$ maps to a first-passage problem
with absorbing barrier $b = -\ln H_0$ for the driftless-adjusted log-health process. Two
quantities are produced:

- **Distance-to-liquidation** $\mathrm{DTL}$, the number of volatility units between the
  current state and the liquidation boundary (the lending analogue of Merton's
  distance-to-default).
- **First-passage probability** $\mathbb{P}(\tau \le T)$ via the Black–Cox reflection
  principle, yielding an inverse-Gaussian hitting-time law. The first-passage probability is
  the primary risk number; the terminal (Merton) probability is reported as a lower bound,
  since $\mathbb{P}(\tau \le T) \ge \mathbb{P}(H_T \le 1)$.

**Assumptions:** constant $\mu, \sigma$ over the horizon; continuous monitoring of the
barrier; collateral value following GBM.

### 3.3 Reduced-form term-structure risk (Cox / intensity)

De-peg risk for pegged assets is modeled with a hazard intensity $\lambda_t$, giving the
survival function $S(t) = \exp(-\Lambda_t)$ with cumulative hazard
$\Lambda_t = \int_0^t \lambda_s\,ds$ and de-peg probability $\mathrm{PD}(t) = 1 - e^{-\Lambda_t}$.
Intensities are calibrated in CDS-style fashion from observed spreads/quotes.

**Assumptions:** default is a doubly-stochastic (Cox) process; the intensity is
$\mathcal{F}_t$-measurable and independent of the default indicator given its path.

### 3.4 Volatility estimation

The $\sigma$ input is estimated from realized variance, EWMA, and GARCH(1,1) via maximum
likelihood. GARCH supplies the volatility term structure used to scale horizon variance.

**Assumptions:** stationarity of the variance process over the estimation window; correct
specification of the GARCH recursion.

### 3.5 Dependence (copulas; factor model)

Cross-position dependence is specified by a copula via Sklar's theorem. Gaussian and
Student-$t$ copulas are supported; the $t$-copula introduces lower-tail dependence

$$
\lambda_L = 2\,t_{\nu+1}\!\left(-\sqrt{\nu+1}\,\sqrt{\tfrac{1-\rho}{1+\rho}}\right),
$$

which the Gaussian copula ($\lambda_L = 0$) cannot represent. A latent one-factor or
full-matrix decomposition $X_i = \sqrt{\rho_i}\,Z + \sqrt{1-\rho_i}\,\varepsilon_i$ links a
systematic factor $Z$ to idiosyncratic shocks $\varepsilon_i$. Correlations are recovered
from Kendall's $\tau$ ($\rho = \sin(\tfrac{\pi}{2}\tau)$) with nearest-correlation repair for
positive-definiteness; $\nu$ is fitted by matching empirical tail dependence.

**Assumptions:** the chosen copula family captures the true dependence structure; the factor
decomposition is rank-consistent with the calibrated correlation matrix.

### 3.6 Monte Carlo cascade

The portfolio loss distribution is generated by simulation:

1. Draw correlated latent factors (Gaussian or $t$, the latter via a gamma mixing variable).
2. Map to copula-uniforms and then to marginal returns and price shocks.
3. Recompute health factors; mark positions with $H \le 1$ as liquidated.
4. Apply price impact from forced selling — square-root market-impact slippage
   $\eta\,\sigma\sqrt{q/V}$ (capped at 1) and a Kyle-linear alternative — and re-evaluate
   health, iterating the **contagion cascade** until no further liquidations occur
   (terminates in at most $d$ rounds).
5. Accumulate per-scenario loss, combining credit loss and slippage cost.

Variance reduction includes antithetic variates, control variates (Vasicek conditional
loss), conditional Monte Carlo, importance sampling via exponential tilting, and
Sobol' quasi-Monte Carlo. Convergence is reported through standard errors, confidence
intervals, and effective sample size.

**Assumptions:** slippage is a deterministic function of liquidated quantity relative to
market depth; the cascade resolves within the horizon; scenarios are i.i.d. draws of the
factor model.

### 3.7 Risk measures and allocation

From the simulated loss sample, the system computes

$$
\mathrm{VaR}_\alpha(L) = \inf\{x : \mathbb{P}(L \le x) \ge \alpha\},
\qquad
\mathrm{ES}_\alpha(L) = \frac{1}{1-\alpha}\int_\alpha^1 \mathrm{VaR}_u(L)\,du .
$$

$\mathrm{ES}_\alpha$ is coherent (sub-additive); $\mathrm{VaR}_\alpha$ is not, and an explicit
counterexample is retained in validation. Per-position risk is allocated by the Euler rule,
$\mathrm{ES}_\alpha = \sum_i \mathrm{RC}_i^{\mathrm{ES}}$, where $\mathrm{RC}_i^{\mathrm{ES}}$
is the mean loss of position $i$ over tail scenarios $\{L \ge \mathrm{VaR}_\alpha\}$.
Estimator standard errors (order-statistic VaR with kernel-density denominator; tail-average
ES) and backtests (Kupiec, Christoffersen, Acerbi–Székely, Fissler–Ziegel) are provided.

**Assumptions:** the loss sample is representative of the horizon distribution; tail
estimators are evaluated where their asymptotics are informative ($N$ large relative to
$1-\alpha$).

---

## 4. Key Assumptions

- Risk is measured under $\mathbb{P}$; $\mathbb{Q}$ is used only for pricing/calibration, and
  every measure change is explicit.
- Parameters $\mu, \sigma$ are constant over a given horizon; volatility dynamics enter only
  through the term structure used to scale variance.
- Dependence is fully described by the calibrated copula and factor decomposition.
- Market impact is a known deterministic function of size and depth; liquidation is
  continuously monitored.
- Monte Carlo estimates carry sampling error quantified by reported standard errors; they are
  not exact.

---

## 5. System Workflow

```
prices, positions, market depth
        │
        ▼
volatility estimation (σ)  ──►  structural single-name risk (DTL, first-passage PD)
        │                                   │
        ▼                                   ▼
dependence calibration            reduced-form term structure (S(t), de-peg PD(t))
(copula, factor loadings)
        │
        ▼
Monte Carlo cascade  ──►  loss distribution L  ──►  risk measures (VaR, ES, RC_i^ES)
        │
        ▼
frozen artifact (schema-versioned)  ──►  presentation layer (web/)
```

Data flows one way: the engine produces a single canonical, read-only artifact (position
metrics, survival curves, loss distribution and histogram, VaR/ES, and ES contributions),
and the presentation layer renders it without recomputation.

---

## 6. Technical Overview (Brief)

- `engine/` — the mathematical core. Submodules: `process` (GBM), `structural`
  (distance-to-liquidation, first passage), `hazard` (Cox/intensity, survival),
  `volatility` (realized variance, EWMA, GARCH), `dependence` (copulas, factor model,
  estimation), `cascade` (sampler, impact, cascade loop, convergence, variance reduction),
  `risk` (VaR/ES, estimators, Euler allocation, backtests, artifacts), and `numerics`
  (normal/special functions, linear algebra, RNG).
- `validation/` — independent re-derivations, dimensional and probabilistic consistency
  checks, limitation and assumption ledgers, and a verified master results ledger.
- `defi/` — the formal mathematical reference, derived from first principles and reviewed in
  two independent passes.
- `web/` — a read-only presentation layer consuming the engine artifact; it contains no
  mathematics and imports no engine module.

**Computational considerations.** Tail risk estimation requires $N$ large relative to
$1-\alpha$; variance-reduction techniques target this regime. Correlation matrices are
repaired to the nearest positive-definite matrix before factorization. Random number
generation uses counter-based streams for reproducibility.

---

## 7. Limitations

- Constant-parameter structural models do not capture intra-horizon regime shifts in $\mu$ or
  $\sigma$ beyond the volatility term structure.
- The market-impact model is a reduced-form deterministic approximation; it does not model
  the order book or strategic liquidator behavior.
- Copula and factor calibration are only as accurate as the input correlation and tail-
  dependence estimates; misspecification propagates to the loss tail.
- Monte Carlo outputs are estimates with quantified sampling error, not closed-form values.
- Reduced-form intensities calibrated from market quotes inherit any risk premia embedded in
  those quotes.

A complete limitation registry and assumption ledger are maintained in `validation/`.

---

## 8. References

Primary frameworks underlying the methodology:

- Merton (1974) — structural default; Black & Cox (1976) — first-passage barrier.
- Jarrow & Turnbull (1995); Lando (1998) — reduced-form intensity models.
- Li (2000); Sklar (1959) — copula dependence; Embrechts, McNeil & Straumann (2002) — tail
  dependence.
- Vasicek (1987, 2002) — single-factor portfolio loss.
- Artzner, Delbaen, Eber & Heath (1999) — coherent risk measures; Rockafellar & Uryasev
  (2000, 2002) — Expected Shortfall; Acerbi & Tasche (2002) — ES estimation and allocation.
- McNeil, Frey & Embrechts (2015) — quantitative risk management synthesis.

Full bibliography: [defi/13_references.md](defi/13_references.md). Mathematical reference:
[defi/README.md](defi/README.md).

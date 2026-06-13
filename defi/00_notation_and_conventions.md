# 00 — Notation, Conventions, and Probabilistic Setup

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

This file fixes notation used throughout. Consistency of notation is itself an audit
criterion (see [11_audit_pass_1.md](11_audit_pass_1.md) §A).

---

## 0.1 Probability space and filtration

We work on a filtered probability space $(\Omega, \mathcal{F}, (\mathcal{F}_t)_{t\ge 0}, \mathbb{P})$
satisfying the **usual conditions** (right-continuity and completeness), as required for the
stochastic calculus of continuous semimartingales (Protter, 2005, Ch. I; Karatzas & Shreve,
1991, §1.1). $(\mathcal{F}_t)$ is the natural (augmented) filtration of the driving Brownian
motion unless stated otherwise.

- $\mathbb{P}$ — the **physical / real-world** measure. Risk *measurement* (VaR, ES, PD) is
  performed under $\mathbb{P}$.
- $\mathbb{Q}$ — an **equivalent martingale measure** (risk-neutral). Used only where we
  *price* a contingent claim (e.g. equity-as-option in Merton, CDS-style calibration). The
  distinction is essential and is a frequent source of error; we flag every measure change.
- $\mathbb{E}[\cdot]$, $\mathbb{E}^{\mathbb{Q}}[\cdot]$ — expectation under the indicated measure.

By the Girsanov theorem (Karatzas & Shreve, 1991, §3.5), $\mathbb{P}$ and $\mathbb{Q}$ are
equivalent on $\mathcal{F}_T$ for finite $T$ under the standard market-price-of-risk
conditions; they agree on null sets, so *almost-sure* statements are measure-independent.

---

## 0.2 Core symbols

| Symbol | Meaning | Units / range |
|--------|---------|---------------|
| $t, T$ | current time, horizon | years (annualized) |
| $\tau$ | default / liquidation time (a stopping time) | years, $\tau \in (0,\infty]$ |
| $V_t$ | firm asset value (Merton) | currency |
| $C_t$ | collateral value of a lending position | currency (USD) |
| $B_t$ | borrowed (debt) value | currency (USD) |
| $D$ | face value of debt / default barrier | currency |
| $S_t$ | equity value (Merton) or asset price (generic) | currency |
| $P_t$ | price of a crypto asset | USD |
| $\ell$ | liquidation threshold (a.k.a. liquidation LTV) | $\in (0,1)$ |
| $H_t$ | health factor of a position | $>0$; liquidation at $H_t \le 1$ |
| $\mathrm{LTV}_t$ | loan-to-value ratio $= B_t / C_t$ | $\in (0,\infty)$ |
| $\mu$ | drift of log-price (physical) | yr$^{-1}$ |
| $r$ | risk-free rate | yr$^{-1}$ |
| $\sigma$ | volatility (annualized std. of log-returns) | yr$^{-1/2}$ |
| $W_t$ | standard Brownian motion (Wiener process) | — |
| $\Phi(\cdot)$ | standard normal CDF | $\in (0,1)$ |
| $\phi(\cdot)$ | standard normal PDF | — |
| $\Phi^{-1}(\cdot)$ | standard normal quantile function | $\mathbb{R}$ |
| $\mathrm{DD}$ | distance-to-default | dimensionless ($\sigma$-units) |
| $\mathrm{DTL}$ | distance-to-liquidation | dimensionless |
| $\lambda_t$ | default/hazard intensity | yr$^{-1}$ |
| $\Lambda_t$ | cumulative hazard $\int_0^t \lambda_s\,ds$ | dimensionless |
| $S(t)$ | survival probability $\mathbb{P}(\tau > t)$ | $\in [0,1]$ |
| $R$ | recovery rate | $\in [0,1]$ |
| $\mathrm{LGD}$ | loss given default $= 1-R$ | $\in [0,1]$ |
| $\mathrm{EAD}$ | exposure at default | currency |
| $\rho, \rho_{ij}$ | correlation (asset or latent factor) | $\in [-1,1]$ |
| $Z$ | systematic (common) factor | std. normal |
| $\varepsilon_i$ | idiosyncratic factor for name $i$ | std. normal |
| $C(\cdot)$ | a copula function | $[0,1]^d \to [0,1]$ |
| $L$ | portfolio loss | currency |
| $\mathrm{VaR}_\alpha$ | Value-at-Risk at level $\alpha$ | currency |
| $\mathrm{ES}_\alpha$ | Expected Shortfall at level $\alpha$ | currency |
| $\alpha$ | confidence level | $\in (0,1)$, e.g. $0.99$ |
| $N$ | number of Monte Carlo scenarios | $\in \mathbb{N}$ |
| $d$ | number of names / assets | $\in \mathbb{N}$ |

---

## 0.3 Conventions

**Log-returns.** The log-return over $[t, t+\Delta]$ is
$r_{t,\Delta} = \ln(P_{t+\Delta}/P_t)$. Continuously-compounded returns are the modeling
default because they are additive in time and, under GBM, exactly Gaussian (see
[01](01_geometric_brownian_motion.md)).

**Annualization.** With $\Delta$ expressed in years, variance scales linearly in time under
the i.i.d.-increment assumption: $\mathrm{Var}(r_{t,\Delta}) = \sigma^2 \Delta$. For data
sampled $n$ times per year, $\sigma_{\text{annual}} = \sigma_{\text{period}}\sqrt{n}$. The
$\sqrt{\text{time}}$ rule is exact under GBM and only approximate under
autocorrelated/heteroskedastic returns (Diebold et al., 1997) — flagged in
[06](06_volatility_estimation.md).

**Sign convention for distance measures.** $\mathrm{DD}$ and $\mathrm{DTL}$ are defined so
that **larger = safer** and $\mathrm{PD} = \Phi(-\mathrm{DD})$. A negative distance means the
barrier is already breached in expectation.

**Confidence level.** We write VaR/ES at level $\alpha$ close to 1 (e.g. $\alpha = 0.99$);
$\mathrm{VaR}_\alpha$ is the $\alpha$-quantile of the loss. Some texts parameterize by the tail
mass $1-\alpha$; we always state $\alpha$ explicitly to avoid the off-by-tail error flagged in
[11](11_audit_pass_1.md).

**Indicator.** $\mathbf{1}_{A}$ is $1$ on event $A$, else $0$.

---

## 0.4 Dimensional bookkeeping (a verification tool)

We track units to catch errors (used in [12_verification_pass_2.md](12_verification_pass_2.md) §C):

- Arguments of $\exp$, $\ln$, $\Phi$ **must be dimensionless**.
- $\sigma$ carries units yr$^{-1/2}$, so $\sigma\sqrt{T}$ is dimensionless and
  $\sigma^2 T$ is dimensionless. ✔ consistent with $\Phi$ arguments.
- $\mu T$, $r T$, $\lambda T$, $\Lambda$ are dimensionless. ✔
- $\ln(C\ell/B)$: $C, B$ share currency units which cancel; $\ell$ is dimensionless ⇒ argument
  dimensionless. ✔
- Distance measures $\mathrm{DD}, \mathrm{DTL}$ are dimensionless ($\sigma$-standardized). ✔

Any expression failing these checks is flagged as an error in Pass 2.

---

## 0.5 Standing modeling assumptions (and where they are relaxed)

| # | Assumption | First used | Relaxed / critiqued in |
|---|-----------|-----------|------------------------|
| A1 | Frictionless, continuous trading | [01](01_geometric_brownian_motion.md) | [08](08_monte_carlo_cascade.md) (price impact), [11](11_audit_pass_1.md) |
| A2 | Log-prices follow GBM (constant $\mu,\sigma$) | [01](01_geometric_brownian_motion.md) | [05](05_reduced_form_hazard.md), [06](06_volatility_estimation.md) (stoch. vol, jumps) |
| A3 | Gaussian increments / no jumps | [01](01_geometric_brownian_motion.md) | [06](06_volatility_estimation.md), [07](07_copula_dependence.md) (t-copula tails), [11](11_audit_pass_1.md) |
| A4 | Default only at horizon $T$ (Merton) | [02](02_merton_structural_model.md) | [04](04_first_passage_barrier.md) (first passage) |
| A5 | Dependence captured by a single factor / Gaussian copula | [07](07_copula_dependence.md) | [07](07_copula_dependence.md) (t-copula), [11](11_audit_pass_1.md) |
| A6 | Recovery $R$ deterministic | [05](05_reduced_form_hazard.md), [09](09_risk_measures.md) | [11](11_audit_pass_1.md) (stochastic recovery) |
| A7 | Oracle price = true price, instantaneous liquidation | [03](03_distance_to_liquidation.md) | [08](08_monte_carlo_cascade.md), [11](11_audit_pass_1.md) (latency, MEV) |

These are the load-bearing assumptions; the audit passes test each one.

---

Next: [01 — Geometric Brownian Motion](01_geometric_brownian_motion.md)

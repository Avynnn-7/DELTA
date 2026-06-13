# 06 — Volatility Estimation: The σ Input

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

Every structural metric (DD, DTL, first-passage PL) is a function of $\sigma$, the annualized
return volatility. A wrong $\sigma$ corrupts every downstream number, so its estimation deserves
the same rigor as the models it feeds. This file derives the estimators (realized variance,
EWMA, GARCH, MLE), their assumptions, and the crypto-specific caveats.

---

## 6.1 The estimand

Under GBM ([01](01_geometric_brownian_motion.md)), log-returns over disjoint intervals of
length $\Delta$ are i.i.d. $\mathcal{N}\big((\mu-\tfrac12\sigma^2)\Delta,\ \sigma^2\Delta\big)$.
The target is the **annualized** $\sigma$ with $\sigma^2\Delta = \mathrm{Var}(r)$ per period.

Let $r_i = \ln(P_{t_i}/P_{t_{i-1}})$, $i=1,\dots,n$, be equally-spaced log-returns.

---

## 6.2 Realized variance (the nonparametric anchor)

**Definition 6.1 (Realized variance).** Over a window of $n$ returns,

$$
\widehat{\mathrm{RV}} = \sum_{i=1}^{n} r_i^2,\qquad
\hat\sigma^2_{\text{period}} = \frac{1}{n-1}\sum_{i=1}^{n}(r_i-\bar r)^2. \tag{6.1}
$$

**Theoretical justification.** Realized variance converges to the **quadratic variation** of
the log-price as the sampling interval shrinks: for an Itô process,
$\sum_i r_i^2 \xrightarrow{p} \int_0^T \sigma_s^2\,ds$ as $\max\Delta_i\to0$
(Andersen, Bollerslev, Diebold & Labys, 2003; Barndorff-Nielsen & Shephard, 2002). Under
*constant* $\sigma$ this limit is $\sigma^2 T$, so RV is a consistent variance estimator. This
is **Result D-6.1**.

**Annualization.** $\hat\sigma_{\text{annual}} = \hat\sigma_{\text{period}}\sqrt{n_{\text{yr}}}$
where $n_{\text{yr}}$ is the number of periods per year (e.g. $365\times24$ for hourly crypto,
which trades 24/7 — unlike equities' 252 trading days). The $\sqrt{\cdot}$ rule is exact under
i.i.d. increments (D-1.2) and is dimensionally consistent ([00](00_notation_and_conventions.md)
§0.4). ✔

**Microstructure caveat.** As $\Delta\to0$, market-microstructure noise (bid–ask bounce,
discrete ticks) **biases RV upward** (Zhou, 1996; Aït-Sahalia, Mykland & Zhang, 2005). Optimal
sampling (e.g. 5-min in equities) or noise-robust estimators (two-scale RV; realized kernels,
Barndorff-Nielsen et al., 2008) are the principled fixes. Logged as limitation L-V1.

---

## 6.3 EWMA (RiskMetrics) — adapting to volatility clustering

Constant-$\sigma$ is violated: volatility **clusters** (Mandelbrot, 1963). The
exponentially-weighted moving average weights recent squared returns more:

$$
\hat\sigma_t^2 = (1-\lambda)\sum_{k=0}^{\infty}\lambda^{k} r_{t-1-k}^2
= \lambda\,\hat\sigma_{t-1}^2 + (1-\lambda)\,r_{t-1}^2, \tag{6.2}
$$

with decay $\lambda\in(0,1)$ (RiskMetrics uses $\lambda=0.94$ for daily; J.P. Morgan, 1996).
**Result D-6.2.** The recursive form makes it $O(1)$ per update — ideal for the streaming hot
path. EWMA is the $\omega=0$, $\alpha+\beta=1$ boundary case of GARCH (§6.4), i.e. **IGARCH**;
this nesting is verified in [12](12_verification_pass_2.md) §A-6.

---

## 6.4 GARCH(1,1) — the canonical conditional-variance model

**Definition 6.2 (GARCH(1,1)).** With $r_t = \mu + \epsilon_t$, $\epsilon_t = \sigma_t z_t$,
$z_t\stackrel{iid}{\sim}\mathcal{N}(0,1)$,

$$
\sigma_t^2 = \omega + \alpha\,\epsilon_{t-1}^2 + \beta\,\sigma_{t-1}^2,
\qquad \omega>0,\ \alpha,\beta\ge0. \tag{6.3}
$$

(Bollerslev, 1986; Engle, 1982 for ARCH.)

**Stationarity & long-run variance (derivation).** Taking unconditional expectations of (6.3)
with $\mathbb{E}[\epsilon_{t-1}^2]=\mathbb{E}[\sigma_{t-1}^2]=\bar\sigma^2$ (covariance
stationarity) gives $\bar\sigma^2 = \omega + \alpha\bar\sigma^2 + \beta\bar\sigma^2$, hence

$$
\bar\sigma^2 = \frac{\omega}{1-\alpha-\beta},\qquad\text{requiring } \alpha+\beta<1. \tag{6.4}
$$

**Result D-6.3.** The condition $\alpha+\beta<1$ is exactly covariance-stationarity; the
boundary $\alpha+\beta=1$ is IGARCH/EWMA (§6.3). Verified in
[12](12_verification_pass_2.md) §A-6.

**Forecast / term structure of variance.** The $h$-step-ahead conditional variance mean-reverts
to $\bar\sigma^2$:

$$
\mathbb{E}_t[\sigma_{t+h}^2] = \bar\sigma^2 + (\alpha+\beta)^{h-1}\big(\sigma_{t+1}^2 - \bar\sigma^2\big). \tag{6.5}
$$

This supplies a **horizon-dependent** $\sigma(T)$ for DTL across tenors (Result D-6.4),
replacing the crude $\sqrt{T}$-scaling and respecting mean reversion. Derived in Pass 2.

---

## 6.5 Maximum-likelihood estimation (the parametric tie-together)

For GBM/GARCH, parameters are estimated by ML. Under conditional normality the log-likelihood is

$$
\ell(\boldsymbol\theta) = -\frac{1}{2}\sum_{t=1}^{n}\left[\ln(2\pi) + \ln\sigma_t^2(\boldsymbol\theta) + \frac{\epsilon_t^2}{\sigma_t^2(\boldsymbol\theta)}\right]. \tag{6.6}
$$

(Bollerslev, 1986.) **Result D-6.5.** For plain GBM ($\sigma_t\equiv\sigma$) this reduces to the
closed-form MLE $\hat\sigma^2 = \frac1n\sum(r_t-\bar r)^2$ (the biased divisor $n$; the
$n-1$ form (6.1) is the unbiased correction — verified in Pass 2 §A-6, Result R-6.6). MLE is
consistent and asymptotically efficient under correct specification (Newey & McFadden, 1994);
QMLE remains consistent for the variance dynamics even under non-normal $z_t$
(Bollerslev & Wooldridge, 1992) — important given crypto's non-normal innovations.

---

## 6.6 Crypto-specific considerations (stated explicitly)

| Issue | Evidence | Engine response |
|-------|----------|-----------------|
| **Heavy-tailed innovations** | Crypto kurtosis ≫ 3 (Gkillas & Katsiampa, 2018) | Use Student-$t$ GARCH innovations; QMLE for robustness; feed t-copula tails ([07](07_copula_dependence.md)) |
| **Leverage/asymmetry** | Negative returns raise vol more (Black, 1976; crypto: Baur & Dimpfl, 2018) | GJR-GARCH (Glosten, Jagannathan & Runkle, 1993) or EGARCH (Nelson, 1991) |
| **24/7 trading** | No overnight gaps; $n_{\text{yr}}=365\times24\times\dots$ | Correct annualization factor (not 252) |
| **Jumps** | Exchange outages, de-pegs | Bipower variation to separate jumps from diffusion (Barndorff-Nielsen & Shephard, 2004) |
| **Unreliable drift** | $\mu$ needs decades of data (Merton, 1980) | Set $\mu\approx0$ for short-horizon DTL ([03](03_distance_to_liquidation.md) §3.6) — volatility is estimable from short windows, drift is not |

The asymmetry of estimability — **variance converges fast, drift converges slowly** (Merton,
1980) — is the theoretical justification for the engine's "trust $\hat\sigma$, distrust
$\hat\mu$" stance.

---

## 6.7 Model selection (rigorous comparison)

Competing estimators are compared by out-of-sample likelihood and information criteria
(AIC, Akaike 1974; BIC, Schwarz 1978), and by volatility-forecast loss (QLIKE/MSE against
realized variance; Patton, 2011, who shows QLIKE is robust to the noisy RV proxy). Recommended
default: **GJR-GARCH(1,1)-$t$** for risk metrics (captures clustering, asymmetry, heavy tails),
with **EWMA** as the $O(1)$ streaming fallback and **RV** as the model-free monitor. Justified
in [11](11_audit_pass_1.md) §model-selection.

---

## 6.8 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| D-6.1 | RV consistency | $\sum r_i^2\to\int\sigma_s^2 ds$ (quadratic variation) |
| D-6.2 | EWMA recursion | $\hat\sigma_t^2=\lambda\hat\sigma_{t-1}^2+(1-\lambda)r_{t-1}^2$ |
| D-6.3 | GARCH long-run var | $\bar\sigma^2=\omega/(1-\alpha-\beta)$, $\alpha+\beta<1$ |
| D-6.4 | GARCH var forecast | (6.5) mean-reverting term structure |
| D-6.5 | (Q)MLE | log-likelihood (6.6) |
| R-6.6 | GBM MLE vs unbiased | divisor $n$ (MLE) vs $n-1$ (unbiased) (Pass 2) |

---

Previous: [05 — Reduced-Form Hazard](05_reduced_form_hazard.md) · Next: [07 — Copula Dependence](07_copula_dependence.md)

# 09 — Risk Measures: VaR, Expected Shortfall, and Allocation

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

The simulated loss distribution ([08](08_monte_carlo_cascade.md)) is summarized into
protocol-level risk numbers. This file gives the formal definitions, the **coherence** theory
(Artzner et al., 1999) that explains *why Expected Shortfall is preferred to Value-at-Risk*, the
risk-contribution (Euler) allocation, and the estimator theory for both.

---

## 9.1 Value-at-Risk

**Definition 9.1 (VaR).** For loss $L$ and level $\alpha\in(0,1)$ (e.g. $0.99$), VaR is the
$\alpha$-quantile of the loss:

$$
\mathrm{VaR}_\alpha(L) = \inf\{x\in\mathbb R : \mathbb P(L\le x)\ge\alpha\} = F_L^{-1}(\alpha). \tag{9.1}
$$

(Jorion, 2006; McNeil, Frey & Embrechts, 2015, Def 2.8.) Interpretation: with probability
$\alpha$, the loss does not exceed $\mathrm{VaR}_\alpha$.

**The defect.** VaR says nothing about losses *beyond* the quantile, and — critically — it is
**not subadditive**: there exist $L_1,L_2$ with
$\mathrm{VaR}_\alpha(L_1+L_2)>\mathrm{VaR}_\alpha(L_1)+\mathrm{VaR}_\alpha(L_2)$
(Artzner et al., 1999, §3; Embrechts, McNeil & Straumann, 2002). Then VaR *penalizes
diversification* — economically perverse for a portfolio risk measure. This motivates ES.

---

## 9.2 Expected Shortfall

**Definition 9.2 (Expected Shortfall).** The average loss in the worst $(1-\alpha)$ tail:

$$
\mathrm{ES}_\alpha(L) = \frac{1}{1-\alpha}\int_\alpha^1 \mathrm{VaR}_u(L)\,du. \tag{9.2}
$$

(Acerbi & Tasche, 2002; Rockafellar & Uryasev, 2002.) For **continuous** $L$ this equals the
tail conditional expectation:

$$
\mathrm{ES}_\alpha(L) = \mathbb E\big[L \mid L\ge \mathrm{VaR}_\alpha(L)\big]. \tag{9.3}
$$

**Result D-9.1.** The equivalence (9.2)⇔(9.3) holds when $F_L$ is continuous at
$\mathrm{VaR}_\alpha$; for distributions with atoms the integral form (9.2) is the correct,
coherent definition while (9.3) can fail subadditivity (Acerbi & Tasche, 2002). The
distinction — and why the engine uses (9.2) — is verified in
[12](12_verification_pass_2.md) §A-9. Since $\mathrm{ES}_\alpha\ge\mathrm{VaR}_\alpha$ always
(it averages the quantiles *beyond* $\alpha$), ES is the more conservative number. ✔

---

## 9.3 Coherence (Artzner et al., 1999)

**Definition 9.3 (Coherent risk measure).** $\varrho$ is coherent if it satisfies, for all
losses $L_1,L_2$:

1. **Monotonicity:** $L_1\le L_2 \Rightarrow \varrho(L_1)\le\varrho(L_2)$.
2. **Translation invariance:** $\varrho(L+c)=\varrho(L)+c$ for constant $c$.
3. **Positive homogeneity:** $\varrho(\lambda L)=\lambda\varrho(L)$ for $\lambda\ge0$.
4. **Subadditivity:** $\varrho(L_1+L_2)\le\varrho(L_1)+\varrho(L_2)$ (diversification helps).

(Artzner, Delbaen, Eber & Heath, 1999, Def 2.4.)

**Theorem 9.1.** Expected Shortfall (9.2) is **coherent**; Value-at-Risk is **not** (it violates
subadditivity in general). *Reference:* Acerbi & Tasche (2002, Thm 4.1); Artzner et al. (1999).
This theorem is the decisive theoretical reason the Basel Committee moved the trading book from
VaR to ES (BCBS, 2016/2019, FRTB). **We adopt ES$_\alpha$ as the primary protocol risk measure,
reporting VaR$_\alpha$ alongside for interpretability.** The non-subadditivity of VaR is
demonstrated by explicit counterexample in [12](12_verification_pass_2.md) §A-9.

---

## 9.4 Spectral risk measures (the general family)

ES is the equal-weight average over the tail; more generally a **spectral** risk measure
weights quantiles by an admissible $\varphi$:

$$
M_\varphi(L) = \int_0^1 \varphi(u)\,\mathrm{VaR}_u(L)\,du, \tag{9.4}
$$

with $\varphi\ge0$, non-decreasing, $\int_0^1\varphi=1$. Spectral measures are exactly the
**law-invariant coherent comonotone-additive** measures (Acerbi, 2002; Kusuoka, 2001). ES is the
special case $\varphi(u)=\frac{1}{1-\alpha}\mathbf 1_{u\ge\alpha}$. This places ES in its proper
theoretical context (Result noted) and offers a principled way to encode stronger tail aversion
if desired.

---

## 9.5 Risk contributions (Euler allocation)

To attribute total risk to individual positions (which counterparty drives protocol risk?), use
the **Euler principle**, justified for positively-homogeneous $\varrho$ by Euler's theorem on
homogeneous functions (Tasche, 1999; Denault, 2001):

$$
\varrho(L) = \sum_{i=1}^d \mathrm{RC}_i,\qquad \mathrm{RC}_i = w_i\,\frac{\partial \varrho(L)}{\partial w_i}, \tag{9.5}
$$

where $L=\sum_i w_i L_i$. For ES, the contribution has the clean conditional-expectation form

$$
\mathrm{RC}_i^{\mathrm{ES}} = \mathbb E\big[\,L_i \mid L\ge\mathrm{VaR}_\alpha(L)\,\big], \tag{9.6}
$$

i.e. position $i$'s **average loss in the scenarios where the portfolio is in its tail**
(Tasche, 1999). **Result D-9.2.** This is directly estimable from the cascade simulation (average
$L_i^{(s)}$ over the worst $(1-\alpha)N$ scenarios) and powers the dashboard's contagion-map /
concentration view. Euler allocation is the *unique* allocation satisfying the RORAC-compatibility
fairness axioms (Tasche, 2008); derivation in Pass 2 §A-9.

---

## 9.6 Estimators from Monte Carlo (consistency)

Given ordered scenario losses $L_{(1)}\le\cdots\le L_{(N)}$ from
[08](08_monte_carlo_cascade.md):

**VaR estimator (empirical quantile).**

$$
\widehat{\mathrm{VaR}}_\alpha = L_{(\lceil \alpha N\rceil)}. \tag{9.7}
$$

Consistent and asymptotically normal with variance
$\frac{\alpha(1-\alpha)}{N f_L(\mathrm{VaR}_\alpha)^2}$ (Serfling, 1980, §2.3, sample-quantile
CLT). **Result D-9.3.**

**ES estimator (tail average).**

$$
\widehat{\mathrm{ES}}_\alpha = \frac{1}{N-\lceil\alpha N\rceil}\sum_{k=\lceil\alpha N\rceil+1}^{N} L_{(k)}. \tag{9.8}
$$

Strongly consistent for $\mathrm{ES}_\alpha$ (Acerbi & Tasche, 2002, Prop 4.1). **Result D-9.4.**
Both estimators' standard errors are reduced by the importance sampling of
[08](08_monte_carlo_cascade.md) §8.5, which is essential because the tail is rare. Consistency
proofs are re-checked in [12](12_verification_pass_2.md) §A-9.

---

## 9.7 Backtesting (model validation)

Risk numbers must be validated against realized outcomes:

- **VaR coverage:** Kupiec (1995) unconditional-coverage (POF) test — the count of VaR
  exceedances should match $1-\alpha$; and Christoffersen (1998) conditional-coverage test —
  exceedances should be *independent* (no clustering).
- **ES backtesting:** historically harder because ES was thought not **elicitable**
  (Gneiting, 2011). Resolved by joint (VaR, ES) elicitability via a joint scoring function
  (Fissler & Ziegel, 2016) and the Acerbi–Székely (2014) tests. The engine uses the
  Acerbi–Székely Z-tests for ES. Noted as validation procedure V-ES.

---

## 9.8 Why this set of measures

| Choice | Justification |
|--------|---------------|
| **ES$_\alpha$ primary** | Coherent (Thm 9.1); rewards diversification; Basel FRTB standard (BCBS, 2019) |
| VaR$_\alpha$ secondary | Ubiquitous, interpretable ("$x$ at risk"), but reported *with* the coherence caveat |
| Euler/ES contributions | Unique fair allocation (Tasche, 2008); identifies systemic positions |
| Spectral framing | Places ES in the coherent family; extensible tail aversion |
| Acerbi–Székely / Fissler–Ziegel backtests | Statistically valid ES validation despite non-elicitability of ES alone |

This adheres to the governing principle: ES is chosen for its **theoretical soundness
(coherence)**, not because VaR is computationally simpler.

---

## 9.9 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| def. | VaR | $\mathrm{VaR}_\alpha=F_L^{-1}(\alpha)$ |
| D-9.1 | ES forms | (9.2)=(9.3) under continuity; (9.2) coherent in general |
| Thm 9.1 | Coherence | ES coherent; VaR not (subadditivity fails) |
| D-9.2 | ES contribution | $\mathrm{RC}_i^{\mathrm{ES}}=\mathbb E[L_i\mid L\ge\mathrm{VaR}_\alpha]$ |
| D-9.3 | VaR estimator | empirical quantile (9.7), asymptotically normal |
| D-9.4 | ES estimator | tail average (9.8), consistent |

---

Previous: [08 — Monte Carlo Cascade](08_monte_carlo_cascade.md) · Next: [10 — Numerical Methods](10_numerical_methods.md)

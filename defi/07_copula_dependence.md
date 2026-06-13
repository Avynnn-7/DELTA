# 07 — Copula Dependence: Correlated Liquidations & Contagion

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

Independent per-position risk ([03](03_distance_to_liquidation.md)–[05](05_reduced_form_hazard.md))
badly understates portfolio risk because crypto assets are **highly correlated** and crash
*together*. Modeling the joint default/liquidation structure is the role of **copulas**
(Sklar, 1959; Li, 2000) and the **factor model** (Vasicek, 1987). This is the same machinery
that prices CDOs — applied here to correlated liquidations. This file is the dependence
foundation for the cascade simulation ([08](08_monte_carlo_cascade.md)).

---

## 7.1 Sklar's theorem (the foundation)

**Theorem 7.1 (Sklar, 1959).** Let $H$ be a $d$-dimensional joint CDF with marginals
$F_1,\dots,F_d$. There exists a copula $C:[0,1]^d\to[0,1]$ such that

$$
H(x_1,\dots,x_d) = C\big(F_1(x_1),\dots,F_d(x_d)\big). \tag{7.1}
$$

If the $F_i$ are continuous, $C$ is **unique**. Conversely, given any copula $C$ and marginals
$F_i$, (7.1) defines a valid joint CDF. *Reference:* Sklar (1959); Nelsen (2006, Thm 2.3.3);
McNeil, Frey & Embrechts (2015, Thm 7.3).

**Why this matters.** Sklar's theorem **separates** the marginal behavior (each asset's own law,
e.g. from GARCH, [06](06_volatility_estimation.md)) from the **dependence structure** (the
copula). We can model each position's liquidation probability marginally and *then* couple them.
This is the single most important structural idea in portfolio credit risk.

**Definition 7.2 (Copula).** $C:[0,1]^d\to[0,1]$ is a copula iff it is a joint CDF with
uniform $[0,1]$ marginals: grounded ($C=0$ if any $u_i=0$), $C(1,\dots,u,\dots,1)=u$, and
$d$-increasing (all rectangle measures $\ge0$). (Nelsen, 2006, Def 2.10.6.)

---

## 7.2 The Gaussian copula and the one-factor model

**Definition 7.3 (Gaussian copula).** For correlation matrix $R$,

$$
C_R^{\mathrm{Gauss}}(\mathbf u) = \Phi_R\big(\Phi^{-1}(u_1),\dots,\Phi^{-1}(u_d)\big), \tag{7.2}
$$

where $\Phi_R$ is the multivariate-normal CDF with correlation $R$ (Nelsen, 2006, §2.3; the
Wikipedia/McNeil form). Li (2000) introduced this for default-time dependence — the model that
became the CDO-market standard.

**The one-factor reduction (Vasicek, 1987).** Modeling a full $d\times d$ $R$ is infeasible for
large $d$; assume a single common driver. Each name has a latent **asset-return variable**

$$
\boxed{\ X_i = \sqrt{\rho_i}\,Z + \sqrt{1-\rho_i}\,\varepsilon_i,\quad Z,\varepsilon_i\stackrel{iid}{\sim}\mathcal N(0,1).\ } \tag{7.3}
$$

$Z$ is the **systematic factor** (crypto-market beta), $\varepsilon_i$ idiosyncratic. Then
$X_i\sim\mathcal N(0,1)$ (verify: $\mathrm{Var}=\rho_i+(1-\rho_i)=1$ ✔) and for $i\ne j$ the
pairwise correlation is

$$
\mathrm{Corr}(X_i,X_j) = \mathbb{E}[X_iX_j] = \sqrt{\rho_i\rho_j}\,\underbrace{\mathbb E[Z^2]}_{=1} = \sqrt{\rho_i\rho_j}, \tag{7.4}
$$

since the cross terms vanish by independence and $\mathbb E[Z]=\mathbb E[\varepsilon]=0$. With a
homogeneous $\rho_i=\rho$, $\mathrm{Corr}(X_i,X_j)=\rho$. **Result D-7.1** (verified
[12](12_verification_pass_2.md) §A-7).

**Default/liquidation trigger.** Name $i$ defaults by horizon when $X_i$ falls below a threshold
matched to its marginal PD$_i$:

$$
\text{default}_i \iff X_i < \Phi^{-1}(\mathrm{PD}_i) =: c_i. \tag{7.5}
$$

By construction $\mathbb P(\text{default}_i)=\mathbb P(X_i<c_i)=\Phi(c_i)=\mathrm{PD}_i$ ✔ — the
marginal is preserved exactly (Sklar), while $Z$ induces the dependence. This is the simulation
engine of [08](08_monte_carlo_cascade.md).

---

## 7.3 The Vasicek large-portfolio loss distribution (closed form)

For a homogeneous, infinitely-granular portfolio (equal PD, $\rho$, exposure), Vasicek (1987,
2002) derived the limiting loss distribution — the analytic backbone of **Basel II IRB**
(BCBS, 2005).

**Derivation.** Conditional on the factor $Z=z$, defaults are *independent* (only $\varepsilon_i$
remain), each with conditional probability

$$
p(z) = \mathbb P(X_i<c \mid Z=z)
= \mathbb P\!\Big(\varepsilon_i < \tfrac{c-\sqrt\rho z}{\sqrt{1-\rho}}\Big)
= \Phi\!\Big(\frac{\Phi^{-1}(\mathrm{PD}) - \sqrt\rho\,z}{\sqrt{1-\rho}}\Big). \tag{7.6}
$$

By the LLN, the portfolio loss fraction $\to p(Z)$ a.s. Since $Z\sim\mathcal N(0,1)$, the loss
CDF is, for $x\in(0,1)$,

$$
\mathbb P(L\le x) = \mathbb P(p(Z)\le x)
= \Phi\!\left(\frac{\sqrt{1-\rho}\,\Phi^{-1}(x) - \Phi^{-1}(\mathrm{PD})}{\sqrt\rho}\right), \tag{7.7}
$$

(using that $p(\cdot)$ is decreasing, so the inequality flips on inversion). **Result D-7.2** —
the **Vasicek distribution**; full inversion steps and the monotonicity flip are verified in
[12](12_verification_pass_2.md) §A-7. The conditional-independence trick (7.6) is *also* the key
to fast semi-analytic CDO pricing and to variance reduction in [08](08_monte_carlo_cascade.md).

---

## 7.4 Tail dependence and the Gaussian copula's fatal flaw

**Definition 7.4 (Coefficient of lower tail dependence).**

$$
\lambda_L = \lim_{u\downarrow0}\mathbb P\big(U_2\le u \mid U_1\le u\big)
= \lim_{u\downarrow0}\frac{C(u,u)}{u}. \tag{7.8}
$$

$\lambda_L$ measures the propensity to crash *together* in the extreme.

**Theorem 7.2 (Gaussian copula has zero tail dependence).** For the bivariate Gaussian copula
with $|\rho|<1$, $\lambda_L=\lambda_U=0$ (Embrechts, McNeil & Straumann, 2002; Sibuya, 1960).
*Consequence:* no matter how high $\rho$ is, the Gaussian copula assigns **asymptotically
independent** extremes — it cannot represent the joint crashes that define crypto contagion.
This is the precise mathematical content of the "formula that killed Wall Street" critique
(Salmon, 2009; Donnelly & Embrechts, 2010; MacKenzie & Spears, 2014). It is the **single most
important limitation** in this framework and is logged as L-COP.

---

## 7.5 The Student-t copula (the principled remedy)

**Definition 7.5 (t-copula).** With $t_\nu$ the univariate Student-$t_\nu$ CDF and $t_{R,\nu}$
the multivariate-$t$ CDF,

$$
C_{R,\nu}^{t}(\mathbf u) = t_{R,\nu}\big(t_\nu^{-1}(u_1),\dots,t_\nu^{-1}(u_d)\big). \tag{7.9}
$$

**Crucially, the t-copula has *positive* tail dependence** (Embrechts, McNeil & Straumann,
2002; Demarta & McNeil, 2005):

$$
\lambda_L = \lambda_U = 2\,t_{\nu+1}\!\left(-\sqrt{\nu+1}\,\sqrt{\tfrac{1-\rho}{1+\rho}}\right) > 0. \tag{7.10}
$$

**Result D-7.3.** As $\nu\to\infty$ the t-copula → Gaussian and $\lambda\to0$, recovering (and
diagnosing) the Gaussian case (verified in Pass 2 §A-7). The factor structure (7.3) extends to
t by mixing with a common $\chi^2_\nu$ shock:
$X_i=\sqrt{\nu/S}\,(\sqrt{\rho}Z+\sqrt{1-\rho}\varepsilon_i)$, $S\sim\chi^2_\nu$ — giving a
**single shared mixing variable** that makes *all* names jointly heavy-tailed (the systemic
crash mechanism). This is the recommended dependence model for the engine.

---

## 7.6 Estimating dependence (rank-based, robust)

Pearson correlation is not copula-invariant and is distorted by heavy tails. Use rank
correlations, which depend only on the copula (McNeil, Frey & Embrechts, 2015, §7.5):

- **Kendall's $\tau$** relates to the Gaussian/t copula correlation by
  $\rho = \sin\!\big(\tfrac{\pi}{2}\tau\big)$ (Lindskog, McNeil & Schmock, 2003) — **Result
  D-7.4**, a robust route to $R$ that is verified in Pass 2.
- **Tail-dependence estimation** for $\nu$: fit by ML on the joint exceedances, or method of
  moments via (7.10).

---

## 7.7 Why this is the academically defensible choice

| Competing approach | Verdict |
|--------------------|---------|
| Independent defaults | Rejected: ignores contagion; understates tail loss by orders of magnitude (Vasicek shows loss tail is driven by $\rho$) |
| Multivariate normal *returns* | Rejected: ties marginals and dependence together; zero tail dependence |
| **Gaussian copula** | Used as a tractable baseline & for Vasicek closed form, but **flagged** for zero tail dependence (L-COP) |
| **t-copula (recommended)** | Preferred: same factor tractability, *positive* tail dependence (7.10), nests Gaussian; empirically superior for financial extremes (Demarta & McNeil, 2005) |
| Archimedean (Clayton/Gumbel) | Clayton has lower-tail dependence and is a valid alternative for asymmetric crash risk (Nelsen, 2006); harder to scale in $d$ — noted as alternative |
| Vine copulas | Most flexible (Aas et al., 2009; Low et al., 2013) but heavier; noted as future extension |

The selection — **t-copula with one-factor structure, Gaussian retained only for its analytic
Vasicek limit** — directly follows the governing principle: correctness (tail dependence) over
convenience (Gaussian's simpler closed forms).

---

## 7.8 Assumptions and limitations

| Assumption | Limitation | Mitigation |
|------------|-----------|------------|
| Single common factor (7.3) | Multiple sectors (L1s, DeFi blue-chips, memecoins) | Multi-factor extension; block correlation matrix |
| Constant $\rho$ | Correlations spike in crashes (Longin & Solnik, 2001; Ang & Chen, 2002) | t-copula captures *extreme* co-movement; regime-switching $\rho$ as extension |
| Elliptical (Gaussian/t) symmetry | Crashes are *asymmetric* (down-correlation > up) | Clayton/skew-t copulas (noted) |
| Static copula | No dependence *dynamics* | Dynamic/conditional copulas (Patton, 2006) as extension |

---

## 7.9 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| Thm 7.1 | Sklar | $H=C(F_1,\dots,F_d)$, $C$ unique if marginals continuous |
| D-7.1 | Factor correlation | $\mathrm{Corr}(X_i,X_j)=\sqrt{\rho_i\rho_j}$ |
| D-7.2 | Vasicek loss CDF | (7.7) |
| Thm 7.2 | Gaussian tail dependence | $\lambda_L=\lambda_U=0$ for $|\rho|<1$ |
| D-7.3 | t-copula tail dependence | (7.10) $>0$; →0 as $\nu\to\infty$ |
| D-7.4 | Kendall↔correlation | $\rho=\sin(\tfrac\pi2\tau)$ |

---

Previous: [06 — Volatility Estimation](06_volatility_estimation.md) · Next: [08 — Monte Carlo Cascade](08_monte_carlo_cascade.md)

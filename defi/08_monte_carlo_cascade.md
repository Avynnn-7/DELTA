# 08 — Monte Carlo Cascade: Correlated Liquidations with Price Impact

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

This file assembles the dependence model ([07](07_copula_dependence.md)) into the engine's
signature computation: a **correlated Monte Carlo simulation of liquidation cascades** with
endogenous price impact. This is what turns independent liquidation probabilities into a
*systemic contagion* model — the iterative "liquidate → push price down → re-check" loop. It
also covers convergence theory and variance reduction needed for real-time use.

---

## 8.1 What a cascade is (and why naive MC misses it)

A single shock liquidates some positions; their forced collateral sales **depress prices**,
which pushes *other* positions below their barriers, and so on. The portfolio loss is therefore
a **fixed point** of a feedback map, not a sum of independent indicators. This endogenous
amplification is exactly the 2022 Luna/3AC/Celsius mechanism (and the 2008 fire-sale spiral of
Brunnermeier & Pedersen, 2009; Shleifer & Vishny, 1992). Ignoring it understates tail loss.

---

## 8.2 One simulation scenario (algorithm)

Given $d$ positions on assets with one-factor t-dependence ([07](07_copula_dependence.md)):

**Step 1 — sample correlated shocks.** Draw the common factor and idiosyncratics; for the
t-copula draw the shared mixing $S\sim\chi^2_\nu$:

$$
X_i = \sqrt{\tfrac{\nu}{S}}\Big(\sqrt{\rho_i}\,Z + \sqrt{1-\rho_i}\,\varepsilon_i\Big),\quad U_i = t_\nu(X_i),\quad r_i = F_i^{-1}(U_i), \tag{8.1}
$$

where $F_i^{-1}$ is the (GARCH-implied) return marginal of asset $i$
([06](06_volatility_estimation.md)). $r_i$ is the shock to asset $i$'s price.

**Step 2 — apply shock to prices.** $P_i \leftarrow P_i^{0}\,e^{r_i}$.

**Step 3 — cascade loop (the contagion core).** Repeat until no new liquidations:
1. Recompute every position's health $H_j = \ell_j Q_j P_{a(j)} / B_j$ ([03](03_distance_to_liquidation.md)).
2. Mark newly liquidatable positions ($H_j\le1$); seize and sell their collateral.
3. **Apply price impact** of the forced sales (next section), lowering affected $P_a$.
4. Loop (the price drop in 3 may trigger more liquidations in 1).

**Step 4 — record loss.** Total scenario loss
$L^{(s)} = \sum_{j\in\text{liquidated}} \mathrm{LGD}_j\cdot \mathrm{EAD}_j$ plus fire-sale
slippage. Repeat for $s=1,\dots,N$ to build the loss distribution.

---

## 8.3 Price-impact (market-impact) model

Forced selling moves price. Two academically grounded specifications:

**Linear (Kyle, 1985).** Kyle's lambda: price impact is linear in signed order flow,
$\Delta P = -\lambda_{\text{Kyle}}\,q$, where $q$ is quantity sold and $\lambda_{\text{Kyle}}$
is inverse market depth. Derived from a strategic-informed-trader equilibrium (Kyle, 1985);
appropriate for the *permanent* impact of liquidations.

**Square-root (Almgren et al., 2005; Gabaix et al., 2006).** Empirically, impact scales like
the square root of size relative to volume:

$$
\frac{\Delta P}{P} \approx -\,\eta\,\sigma\,\sqrt{\frac{q}{V}}, \tag{8.2}
$$

with daily volume $V$, volatility $\sigma$, and a constant $\eta=O(1)$. This **square-root law**
is one of the most robust stylized facts of market microstructure (Almgren et al., 2005;
Tóth et al., 2011) and is the recommended impact kernel. **Result D-8.1** (used as the cascade's
feedback function; dimensional check in [12](12_verification_pass_2.md) §A-8).

The cascade is the iteration of (8.2) coupled to the health recomputation — a monotone
decreasing price map, so the loop **terminates** (finitely many positions; each round
liquidates ≥1 new position or stops). Termination is proved in Pass 2 §A-8 (Result R-8.2).

---

## 8.4 Monte Carlo convergence theory

**LLN (consistency).** The estimator $\hat\theta_N = \frac1N\sum_{s=1}^N g(L^{(s)})$ (for any
risk functional $g$, e.g. mean loss, or $\mathbf 1_{L>x}$ for a tail probability) converges a.s.
to $\theta=\mathbb E[g(L)]$ by the strong law (Kolmogorov), provided $\mathbb E|g(L)|<\infty$
(Glasserman, 2004, §1.1). **Result D-8.2.**

**CLT (error rate).** If $\mathrm{Var}(g(L))=\varsigma^2<\infty$,

$$
\sqrt N\,(\hat\theta_N - \theta)\ \xrightarrow{d}\ \mathcal N(0,\varsigma^2),
\qquad \text{standard error} = \frac{\varsigma}{\sqrt N}. \tag{8.3}
$$

So the error decays at the **dimension-independent** rate $O(N^{-1/2})$ (Glasserman, 2004,
§1.1) — the reason Monte Carlo beats grids in high $d$. **Result D-8.3.** A $(1-\beta)$ CI is
$\hat\theta_N \pm z_{1-\beta/2}\,\hat\varsigma/\sqrt N$. This quantifies how many scenarios the
real-time engine needs for a target accuracy.

---

## 8.5 Variance reduction (making it real-time)

To hit accuracy targets with fewer scenarios (Glasserman, 2004, Ch. 4):

- **Antithetic variates.** Pair $(Z,\varepsilon)$ with $(-Z,-\varepsilon)$; valid since the
  factors are symmetric. Reduces variance when $g$ is monotone in the shocks (true for loss).
  Result R-8.4.
- **Control variates.** Use the *independent-default* loss (closed-form mean via marginal PDs)
  or the **Vasicek** analytic loss (D-7.2) as a control — strongly correlated with the cascade
  loss, yielding large variance reductions. This directly reuses [07](07_copula_dependence.md).
- **Importance sampling for the tail.** VaR/ES live in the rare tail; exponentially tilt the
  factor $Z$ toward the loss region (Glasserman & Li, 2005, the canonical IS scheme for portfolio
  credit risk). Essential because crude MC needs $O(1/(1-\alpha))$ samples just to see the
  $\alpha$-tail. Result R-8.5.
- **Conditional Monte Carlo.** Condition on $Z$ and use the analytic conditional loss (7.6),
  simulating only the residual — combines with IS (Glasserman & Li, 2005).
- **Quasi-Monte Carlo.** Sobol'/low-discrepancy points give $O((\log N)^d/N)$ for smooth
  integrands (Niederreiter, 1992), though cascade discontinuities (the liquidation indicator)
  temper the gain.

---

## 8.6 Estimating VaR/ES from the simulated loss distribution

The $N$ scenario losses $\{L^{(s)}\}$ feed the risk measures of [09](09_risk_measures.md):
the empirical $\alpha$-quantile estimates VaR, and the tail average estimates ES (formulas and
estimator consistency in [09](09_risk_measures.md) §9.6). The CLT (8.3) and IS (§8.5) control
their standard errors.

---

## 8.7 Assumptions and limitations (stated explicitly)

| Assumption | Limitation | Mitigation / note |
|------------|-----------|-------------------|
| Impact kernel (8.2) is correct & static | Real impact is state-dependent, depends on liquidity that *itself* evaporates in crashes (Brunnermeier & Pedersen, 2009) | Stress the impact parameter $\eta$; scenario analysis; documented as L-IMP |
| Liquidations are instantaneous at $H\le1$ | Oracle latency, keeper competition, gas auctions, MEV (Daian et al., 2020) delay/alter liquidation | Add latency & partial-liquidation logic; idealized loop is an approximation (A7) |
| Marginals & copula correctly specified | Mis-specified tails ⇒ mis-estimated cascade | t-copula + GARCH-$t$ marginals; backtest |
| Exogenous shock then deterministic cascade | Reflexivity: liquidations feed back into the *shock* distribution | Multi-period / agent-based extension noted |
| Fixed positions during a scenario | Borrowers may top-up collateral (deleveraging) | Behavioral response is a modeling extension |

The price-impact feedback is the model's most fragile empirical component; per the governing
principle it is treated as an explicit, stress-tested assumption, not a hidden constant.

---

## 8.8 Why simulation (vs. closed form)

The Vasicek closed form (D-7.2) assumes homogeneity, infinite granularity, **no price impact**,
and a single period — so it cannot represent heterogeneous positions, finite concentration, or
cascades. Monte Carlo lifts all four restrictions at the cost of $O(N^{-1/2})$ noise, which
variance reduction (§8.5) tames. We use Vasicek as a **control variate and sanity check**, and
simulation as the primary engine — each in its valid regime.

---

## 8.9 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| D-8.1 | Square-root impact | $\Delta P/P\approx-\eta\sigma\sqrt{q/V}$ |
| D-8.2 | MC consistency (LLN) | $\hat\theta_N\to\theta$ a.s. |
| D-8.3 | MC error (CLT) | SE $=\varsigma/\sqrt N$, rate $O(N^{-1/2})$ |
| R-8.2 | Cascade termination | monotone price map terminates (Pass 2) |
| R-8.4/8.5 | Variance reduction | antithetic/control/IS validity (Pass 2) |

---

Previous: [07 — Copula Dependence](07_copula_dependence.md) · Next: [09 — Risk Measures](09_risk_measures.md)

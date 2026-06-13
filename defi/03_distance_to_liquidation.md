# 03 — Distance-to-Liquidation: Merton Mapped to On-Chain Lending

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

This is the conceptual core of the engine: we transplant the Merton distance-to-default
([02](02_merton_structural_model.md)) onto over-collateralized DeFi lending (Aave, Compound,
MakerDAO). The mapping is mathematically exact and, crucially, *simpler* than corporate Merton
because the inputs are directly observable on-chain.

---

## 3.1 Mechanics of an over-collateralized position

A borrower deposits collateral worth $C_t = Q\cdot P_t$ ($Q$ units of a crypto asset at price
$P_t$) and borrows stable debt $B_t$. Protocols enforce a **liquidation threshold**
$\ell\in(0,1)$ (Aave's "liquidation threshold", Maker's inverse of the minimum collateralization
ratio). A position is liquidatable when the debt exceeds the threshold-adjusted collateral:

$$
\text{liquidatable} \iff B_t \ge \ell\, C_t \iff \underbrace{\frac{B_t}{\ell\,C_t}}_{\text{health}^{-1}} \ge 1. \tag{3.1}
$$

**Definition 3.1 (Health factor).**

$$
H_t = \frac{\ell\, C_t}{B_t} = \frac{\ell\, Q\, P_t}{B_t}. \tag{3.2}
$$

Liquidation is triggered at $H_t \le 1$. (This matches Aave's on-chain definition;
Aave, 2020.) Note $H_t$ is **linear in price** $P_t$ when $B_t$ and $Q$ are held fixed between
actions — a fact we exploit below.

---

## 3.2 The structural correspondence

| Merton (firm) | DeFi lending position | Identification |
|---------------|------------------------|----------------|
| Asset value $V_t$ | Collateral value $C_t = Q P_t$ | both GBM via $P_t$ |
| Debt face value $D$ | Liquidation barrier $B_t/\ell$ | barrier on collateral |
| Default $\{V_T<D\}$ | Liquidation $\{C_T < B_T/\ell\}$ | same inequality form |
| Asset volatility $\sigma_V$ | Collateral-price volatility $\sigma$ | observable from price |
| Distance-to-default DD | **Distance-to-liquidation DTL** | (3.4) |
| Observables hidden ⇒ invert (§2.4) | $C_t, B_t, \ell$ **observed on-chain** | inversion unnecessary |

The last row is the practical payoff: corporate Merton's hardest step (the equity↔asset
inversion, §2.4) **vanishes**, because collateral and debt are read directly from chain state.

---

## 3.3 Probability of liquidation (terminal-horizon form)

Treat the liquidation barrier over a short horizon $T$ as fixed at $B/\ell$ (debt $B$ roughly
constant absent new borrows/repays; we relax this in §3.6). The collateral value inherits the
GBM of its price: $C_T = C_0\exp[(\mu-\tfrac12\sigma^2)T + \sigma W_T]$. By the identical
derivation as Merton's PD (D-2.1), the **probability of liquidation by horizon $T$** is

$$
\boxed{\
\mathrm{PL}(T) = \mathbb{P}\!\Big(C_T < \tfrac{B}{\ell}\Big)
= \Phi\!\left( \frac{\ln\!\big(\frac{B}{\ell C_0}\big) - (\mu-\frac12\sigma^2)T}{\sigma\sqrt T}\right)
= \Phi(-\mathrm{DTL}).\ } \tag{3.3}
$$

This is **Result D-3.1**.

**Definition 3.2 (Distance-to-liquidation).**

$$
\mathrm{DTL}
= \frac{\ln\!\big(\frac{\ell C_0}{B}\big) + (\mu-\frac12\sigma^2)T}{\sigma\sqrt T}
= \frac{\ln H_0 + (\mu-\frac12\sigma^2)T}{\sigma\sqrt T}, \tag{3.4}
$$

using $H_0 = \ell C_0/B$ from (3.2). So **DTL is the standardized log-health-factor** — an
elegant, interpretable risk metric: how many return-standard-deviations of buffer the position
has. Larger DTL ⇒ safer; $\mathrm{PL}=\Phi(-\mathrm{DTL})$. ✔ (sign convention)

---

## 3.4 Instantaneous "price drop to liquidation"

A model-free companion metric, useful for dashboards. From (3.1), liquidation at the current
instant requires the price to fall to $P^\ast$ with $\ell Q P^\ast = B$, i.e.
$P^\ast = B/(\ell Q)$. The **relative drop to liquidation** is

$$
\delta^\ast = 1 - \frac{P^\ast}{P_0} = 1 - \frac{B}{\ell\,Q\,P_0} = 1 - \frac{B}{\ell\,C_0} = 1 - \frac{1}{H_0}. \tag{3.5}
$$

This is **Result D-3.2**. It requires *no* distributional assumption (it is pure accounting),
making it a robust complement to the model-based $\mathrm{PL}(T)$. Consistency check:
$H_0 = 1 \Rightarrow \delta^\ast = 0$ (already at the barrier). ✔

---

## 3.5 Multi-horizon risk profile

Because (3.3) is closed-form in $T$, the engine produces a **term structure of liquidation
probability** $\{\mathrm{PL}(T): T\in\{1\text{h},24\text{h},7\text{d},\dots\}\}$ by evaluating
$\Phi(-\mathrm{DTL}(T))$ at each horizon, with $T$ in annualized units (e.g.
$1\text{h} = 1/8760$ yr). This directly powers Flow C of the user design (the position
inspector). Monotonicity in $T$ is analyzed in [12](12_verification_pass_2.md) §A-3.

---

## 3.6 Refinements and limitations (stated explicitly)

1. **Barrier is hit *en route*, not only at $T$.** The terminal form (3.3) ignores
   intra-horizon breaches and therefore **understates** liquidation probability. The correct
   object is a **first-passage** probability, derived rigorously in
   [04](04_first_passage_barrier.md). We treat (3.3) as a lower bound and (4.x) as the primary
   metric. This is the most important caveat and is logged as gap G-3 in [11](11_audit_pass_1.md).

2. **Oracle vs. market price.** Liquidations trigger on the *oracle* price, which lags the
   market (Chainlink heartbeat/deviation thresholds; Aave uses Chainlink). The effective barrier
   is on the oracle process, introducing latency risk and MEV/liquidator dynamics not in the
   diffusion model (assumption A7). Flagged for [08](08_monte_carlo_cascade.md) and as
   limitation L-7.

3. **Debt drift / accruing interest.** $B_t$ grows with the borrow interest rate $r_b$:
   $B_t = B_0 e^{r_b t}$. This makes the barrier $B_t/\ell$ time-dependent. The fix is to use the
   **ratio** $C_t/B_t$, which is itself GBM with drift $\mu - r_b$ and the same $\sigma$:
   replace $\mu \to \mu - r_b$ in (3.4). Derived and verified in [12](12_verification_pass_2.md)
   §A-3 (Result R-3.3).

4. **Drift estimation is unreliable** over short horizons; $\mu$ is dominated by noise
   (Merton, 1980). Practice: for short $T$, set $\mu\approx 0$ (or $\mu = r_b$ so the ratio
   drift is $0$), making DTL conservative and estimation-robust. Discussed in
   [06](06_volatility_estimation.md) §6.6.

5. **Heavy tails (A3).** As in Merton, the Gaussian PL understates crash probability; crypto's
   fat tails make this acute. Mitigated at the portfolio level by the t-copula
   ([07](07_copula_dependence.md)) and by stress scenarios ([08](08_monte_carlo_cascade.md)).

---

## 3.7 Stablecoin positions: a boundary case

For a position collateralized by (or borrowing) a stablecoin, $\sigma$ of the stable leg is
near zero *until* a de-peg, which is a **jump**, not diffusion. The diffusion DTL is then
inappropriate, and de-peg risk must be modeled with the **reduced-form hazard** approach of
[05](05_reduced_form_hazard.md). The engine routes assets by type: volatile collateral →
structural DTL (this file); pegged assets → hazard model ([05](05_reduced_form_hazard.md)). This
routing is the principled response to assumption A2/A3 breaking for stablecoins.

---

## 3.8 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| def. | Health factor | $H_t = \ell C_t / B_t$; liquidation at $H_t\le1$ |
| D-3.1 | Probability of liquidation | $\mathrm{PL}(T)=\Phi(-\mathrm{DTL})$, (3.3) |
| def. | Distance-to-liquidation | $\mathrm{DTL}=\frac{\ln H_0+(\mu-\frac12\sigma^2)T}{\sigma\sqrt T}$ |
| D-3.2 | Drop-to-liquidation | $\delta^\ast = 1 - 1/H_0$ |
| R-3.3 | Interest-adjusted drift | replace $\mu\to\mu-r_b$ (verified in Pass 2) |

---

Previous: [02 — Merton](02_merton_structural_model.md) · Next: [04 — First-Passage / Barrier](04_first_passage_barrier.md)

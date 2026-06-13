# 01 — Geometric Brownian Motion: The Price-Process Foundation

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

Every structural model in this framework rests on a model of how collateral/asset value
evolves. The canonical choice — used by Merton (1973, 1974), Black & Scholes (1973), and the
entire structural credit literature — is **geometric Brownian motion (GBM)**. This file states
it formally, derives the log-return distribution from Itô's lemma, and records the assumptions
and their empirical limitations.

---

## 1.1 The Wiener process (formal definition)

**Definition 1.1 (Standard Brownian motion).** A standard Brownian motion (Wiener process)
$\{W_t\}_{t\ge0}$ is a stochastic process with:

1. $W_0 = 0$ a.s.;
2. independent increments: for $0 \le t_0 < \cdots < t_n$, the increments
   $W_{t_{k}}-W_{t_{k-1}}$ are independent;
3. Gaussian increments: $W_{t}-W_{s} \sim \mathcal{N}(0,\, t-s)$ for $s<t$;
4. continuous sample paths a.s.

*Reference:* Karatzas & Shreve (1991, §2.1); Øksendal (2003, §2.2). Existence is the
Wiener (1923) construction.

Key scaling property: $\mathrm{Var}(W_t - W_s) = t-s$, i.e. **standard deviation grows like
$\sqrt{\text{time}}$**. This single fact propagates into every $\sigma\sqrt{T}$ term downstream.

---

## 1.2 The GBM stochastic differential equation

**Definition 1.2 (GBM).** The asset price $P_t$ follows GBM if it solves the linear SDE

$$
dP_t = \mu\, P_t\, dt + \sigma\, P_t\, dW_t, \qquad P_0 > 0, \tag{1.1}
$$

with constant drift $\mu \in \mathbb{R}$ and volatility $\sigma > 0$.

**Economic justification.** Equation (1.1) states that *instantaneous returns* $dP_t/P_t$ are
i.i.d. with mean $\mu\,dt$ and variance $\sigma^2 dt$. Modeling returns (rather than price
levels) as the stationary object is what guarantees $P_t>0$ — essential for a price — and makes
the model scale-invariant (doubling $P_0$ doubles $P_t$ pathwise). This is precisely the
behavior Samuelson (1965) argued for in "rational" warrant pricing, and it is the foundation
of Black–Scholes (1973) and Merton (1973).

---

## 1.3 Solution via Itô's lemma (complete derivation)

**Lemma 1.3 (Itô's formula, 1-D).** For $f \in C^{1,2}$ and an Itô process
$dX_t = a_t\,dt + b_t\,dW_t$,

$$
df(t,X_t) = \Big(\partial_t f + a_t\,\partial_x f + \tfrac12 b_t^2\,\partial_{xx} f\Big)dt
+ b_t\,\partial_x f\,dW_t. \tag{1.2}
$$

*Reference:* Itô (1951); Øksendal (2003, Thm 4.1.2). The extra
$\tfrac12 b_t^2 \partial_{xx}f$ term — absent in ordinary calculus — arises because
$(dW_t)^2 = dt$ (quadratic variation of Brownian motion).

**Derivation of the GBM solution.** Apply (1.2) to $f(P) = \ln P$, with
$a_t = \mu P_t$, $b_t = \sigma P_t$. The partial derivatives are
$\partial_t f = 0$, $\partial_x f = 1/P$, $\partial_{xx} f = -1/P^2$. Substituting:

$$
d(\ln P_t)
= \Big(0 + \mu P_t \cdot \tfrac{1}{P_t} + \tfrac12 \sigma^2 P_t^2 \cdot \big(-\tfrac{1}{P_t^2}\big)\Big)dt
+ \sigma P_t \cdot \tfrac{1}{P_t}\,dW_t.
$$

The price levels cancel cleanly:

$$
d(\ln P_t) = \Big(\mu - \tfrac12 \sigma^2\Big)dt + \sigma\,dW_t. \tag{1.3}
$$

Integrating (1.3) from $0$ to $t$ (the RHS has constant coefficients, so this is exact):

$$
\ln P_t - \ln P_0 = \Big(\mu - \tfrac12\sigma^2\Big)t + \sigma W_t,
$$

hence

$$
\boxed{\,P_t = P_0 \exp\!\Big[\big(\mu - \tfrac12\sigma^2\big)t + \sigma W_t\Big].\,} \tag{1.4}
$$

This is **Result D-1.1** (verified in [11](11_audit_pass_1.md) §D-1 and re-derived in
[12](12_verification_pass_2.md) §A-1).

---

## 1.4 The log-return distribution

From (1.4), since $W_t \sim \mathcal{N}(0,t)$, the log-return is exactly normal:

$$
\ln\!\frac{P_t}{P_0} \sim \mathcal{N}\!\Big(\big(\mu-\tfrac12\sigma^2\big)t,\ \sigma^2 t\Big). \tag{1.5}
$$

Consequently $P_t$ is **log-normally distributed**. Two consequences used downstream:

- **First moment (the Itô / convexity correction).** Using the log-normal mean
  $\mathbb{E}[e^{X}] = e^{m + s^2/2}$ with $m = (\mu-\tfrac12\sigma^2)t$, $s^2 = \sigma^2 t$:

  $$
  \mathbb{E}[P_t] = P_0\, e^{(\mu - \frac12\sigma^2)t + \frac12\sigma^2 t} = P_0\, e^{\mu t}. \tag{1.6}
  $$

  The $-\tfrac12\sigma^2$ in the exponent (1.4) is exactly what is needed so that the
  *arithmetic* mean grows at rate $\mu$. The gap between the median growth rate
  $\mu-\tfrac12\sigma^2$ and the mean growth rate $\mu$ is the **volatility drag**, a
  recurring and frequently mishandled subtlety (we re-verify it in
  [12](12_verification_pass_2.md) §A-1).

- **Variance.** $\mathrm{Var}(P_t) = P_0^2\, e^{2\mu t}\big(e^{\sigma^2 t}-1\big)$
  (standard log-normal variance; verified in Pass 2).

---

## 1.5 Why GBM is theoretically justified here

1. **Positivity.** Collateral and asset prices are non-negative; GBM keeps $P_t>0$ a.s.,
   unlike arithmetic Brownian motion. (Merton, 1973.)
2. **Stationary, scale-free returns.** Empirically, asset *returns* are far closer to
   stationary than price *levels*; GBM encodes exactly this.
3. **Analytic tractability.** The Gaussian log-return (1.5) yields closed-form PD via $\Phi$
   ([02](02_merton_structural_model.md), [03](03_distance_to_liquidation.md)) and closed-form
   first-passage laws ([04](04_first_passage_barrier.md)).
4. **It is the literature's lingua franca.** Merton (1974), Black–Cox (1976), Vasicek (1987),
   and the Basel IRB framework (BCBS, 2005) all build on the Gaussian-latent-variable structure
   that GBM induces, enabling direct reuse of their results.

---

## 1.6 Assumptions and their empirical limitations (stated, not hidden)

GBM assumes (A1–A3 of [00](00_notation_and_conventions.md) §0.5):

| Assumption | Empirical reality in crypto | Consequence / mitigation |
|------------|-----------------------------|--------------------------|
| Constant $\sigma$ | Volatility clusters & is regime-dependent (Mandelbrot, 1963; Cont, 2001) | Use time-varying $\hat\sigma_t$ (EWMA/GARCH, [06](06_volatility_estimation.md)); treat $\sigma$ as a slowly-varying input |
| Gaussian increments | Returns are **heavy-tailed & leptokurtic**, crypto especially (Cont, 2001; Gkillas & Katsiampa, 2018) | PD from Gaussian tails *understates* extreme moves; use t-copula tails ([07](07_copula_dependence.md)) and stress horizons; documented as limitation L-1 in [11](11_audit_pass_1.md) |
| Continuous paths | Crypto exhibits **jumps** (exchange outages, de-pegs, flash crashes) | First-passage/PD are lower bounds near jumps; jump-diffusion (Merton, 1976; Kou, 2002) is the principled extension, noted as future work |
| Independent increments | Mild autocorrelation & long memory in $|r|$ | Affects $\sqrt{t}$-scaling (Diebold et al., 1997); flagged in [06](06_volatility_estimation.md) |

These limitations are *acknowledged as inadequacies of the model*, consistent with the
governing principle that mathematical correctness outranks convenience: we use GBM for its
tractable closed forms while explicitly recording where it breaks.

---

## 1.7 Summary of results established here

| ID | Result | Statement |
|----|--------|-----------|
| D-1.1 | GBM solution | $P_t = P_0 \exp[(\mu-\tfrac12\sigma^2)t + \sigma W_t]$ |
| D-1.2 | Log-return law | $\ln(P_t/P_0)\sim\mathcal N((\mu-\tfrac12\sigma^2)t,\ \sigma^2 t)$ |
| D-1.3 | Mean | $\mathbb{E}[P_t]=P_0 e^{\mu t}$ |
| D-1.4 | Variance | $\mathrm{Var}(P_t)=P_0^2 e^{2\mu t}(e^{\sigma^2 t}-1)$ |

---

Previous: [00 — Notation](00_notation_and_conventions.md) · Next: [02 — Merton Structural Model](02_merton_structural_model.md)

# 02 — The Merton Structural Model

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

The Merton (1974) model is the seminal **structural** credit-risk model: default is an
endogenous consequence of the firm's asset value falling below its debt. It supplies the
**distance-to-default** concept that we transplant to on-chain lending in
[03](03_distance_to_liquidation.md). This file gives the full derivation, the equity↔asset
inversion that makes the model operational, and its assumptions.

---

## 2.1 Setup and the limited-liability insight

A firm finances assets $V_t$ with equity $S_t$ and a single zero-coupon debt of face value $D$
maturing at $T$. Asset value follows GBM under $\mathbb{P}$ (cf. [01](01_geometric_brownian_motion.md)):

$$
dV_t = \mu_V V_t\,dt + \sigma_V V_t\,dW_t. \tag{2.1}
$$

At maturity, equity holders (limited liability) receive the residual:

$$
S_T = \max(V_T - D,\ 0) = (V_T - D)^+. \tag{2.2}
$$

**This is the payoff of a European call option on $V$ with strike $D$.** (Merton, 1974;
Black & Scholes, 1973.) Default occurs iff $V_T < D$.

---

## 2.2 Probability of default under $\mathbb{P}$ (derivation)

Default event: $\{V_T < D\}$. Using the GBM solution (D-1.1) under the **physical** measure,

$$
V_T = V_0 \exp\!\Big[\big(\mu_V - \tfrac12\sigma_V^2\big)T + \sigma_V W_T\Big],
\qquad W_T \sim \mathcal{N}(0,T).
$$

Then

$$
\mathrm{PD} = \mathbb{P}(V_T < D)
= \mathbb{P}\!\Big(\ln V_T < \ln D\Big).
$$

Since $\ln V_T \sim \mathcal{N}\big(\ln V_0 + (\mu_V-\tfrac12\sigma_V^2)T,\ \sigma_V^2 T\big)$,
standardize by subtracting the mean and dividing by the std $\sigma_V\sqrt{T}$:

$$
\mathrm{PD}
= \mathbb{P}\!\left( \underbrace{\frac{\ln V_T - [\ln V_0 + (\mu_V-\frac12\sigma_V^2)T]}{\sigma_V\sqrt T}}_{=\,Z\,\sim\,\mathcal N(0,1)}
< \frac{\ln D - \ln V_0 - (\mu_V-\frac12\sigma_V^2)T}{\sigma_V\sqrt T}\right).
$$

Therefore

$$
\boxed{\ \mathrm{PD}
= \Phi\!\left(\frac{\ln(D/V_0) - (\mu_V-\frac12\sigma_V^2)T}{\sigma_V\sqrt T}\right)
= \Phi(-\mathrm{DD}).\ } \tag{2.3}
$$

This is **Result D-2.1**.

---

## 2.3 Distance-to-default

**Definition 2.1 (Distance-to-default).**

$$
\mathrm{DD}
= \frac{\ln(V_0/D) + \big(\mu_V - \tfrac12\sigma_V^2\big)T}{\sigma_V\sqrt T}. \tag{2.4}
$$

Interpretation: $\mathrm{DD}$ is the number of **standard deviations** by which expected
log-asset-value at $T$ exceeds the log-default-barrier. By (2.3), $\mathrm{PD} = \Phi(-\mathrm{DD})$,
so larger DD ⇒ smaller PD (sign convention of [00](00_notation_and_conventions.md) §0.3). ✔

**Risk-neutral variant.** Replacing $\mu_V\to r$ gives the $\mathbb{Q}$-measure default
probability used for *pricing* the debt/credit spread (Merton, 1974):
$\mathrm{PD}^{\mathbb{Q}} = \Phi\!\big(-d_2\big)$ with
$d_2 = \frac{\ln(V_0/D)+(r-\frac12\sigma_V^2)T}{\sigma_V\sqrt T}$, exactly the Black–Scholes
$d_2$. For risk *measurement* we keep $\mu_V$ (physical). The measure distinction is recorded
as audit item A-2 in [11](11_audit_pass_1.md).

> **KMV note.** Moody's KMV operationalizes this by setting the default point between
> short- and long-term debt (typically short-term debt + ½·long-term debt) and mapping DD to an
> empirical "Expected Default Frequency" rather than $\Phi(-\mathrm{DD})$, precisely because the
> Gaussian tail understates real default rates (Crosbie & Bohn, 2003). This is direct empirical
> evidence for limitation L-1 ([11](11_audit_pass_1.md)).

---

## 2.4 The equity↔asset inversion (making it operational)

The difficulty: $V_0$ and $\sigma_V$ are **not observable** — only equity $S_0$ and equity
volatility $\sigma_S$ are. Merton closes the system with two equations.

**Equation 1 — equity as a call (Black–Scholes).** With $S_t = C^{BS}(V_t,\dots)$,

$$
S_0 = V_0\,\Phi(d_1) - D\,e^{-rT}\,\Phi(d_2), \tag{2.5}
$$

$$
d_1 = \frac{\ln(V_0/D) + (r+\tfrac12\sigma_V^2)T}{\sigma_V\sqrt T},\qquad d_2 = d_1 - \sigma_V\sqrt T. \tag{2.6}
$$

**Equation 2 — equity volatility from Itô.** Since $S=S(V)$, Itô's lemma (Lemma 1.3) gives the
diffusion coefficient of $S$ as $\partial_V S \cdot \sigma_V V$. Matching to $\sigma_S S$:

$$
\sigma_S\, S_0 = \frac{\partial S_0}{\partial V_0}\,\sigma_V\, V_0 = \Phi(d_1)\,\sigma_V\,V_0, \tag{2.7}
$$

using the standard identity $\partial S_0/\partial V_0 = \Phi(d_1)$ (the option delta).

**The system.** Equations (2.5) and (2.7) are two nonlinear equations in the two unknowns
$(V_0,\sigma_V)$, given observables $(S_0,\sigma_S,D,r,T)$. They are solved jointly — typically
by 2-D Newton–Raphson or the Duan (1994) MLE / iterative KMV scheme (see numerics in
[10](10_numerical_methods.md)). This is **Result D-2.2** (the inversion system); its solvability
and Jacobian are checked in [12](12_verification_pass_2.md) §A-2.

---

## 2.5 Assumptions and limitations

| Assumption | Role | Limitation | Addressed in |
|------------|------|-----------|--------------|
| Single zero-coupon debt, default only at $T$ (A4) | Gives the clean call payoff (2.2) | Real debt has multiple maturities; default can occur *before* $T$ | First-passage relaxation: [04](04_first_passage_barrier.md) (Black–Cox) |
| Asset value $V_t$ is GBM (A2) | Closed-form PD | Jumps/stoch-vol violate it | [01](01_geometric_brownian_motion.md) §1.6; jump-diffusion noted |
| Frictionless markets, constant $r$ (A1) | Black–Scholes pricing (2.5) | Crypto frictions, variable funding | [08](08_monte_carlo_cascade.md) |
| Gaussian tail for PD (A3) | $\mathrm{PD}=\Phi(-\mathrm{DD})$ | Understates extreme PD (KMV uses empirical EDF) | L-1 in [11](11_audit_pass_1.md) |

---

## 2.6 Why Merton (vs. alternatives) — and what we keep

- **vs. reduced-form (Jarrow–Turnbull, 1995):** Merton is *economically interpretable*
  (default has a cause: $V<D$) and needs no traded credit instrument to calibrate — ideal for
  the DeFi setting where collateral/debt are *directly observable on-chain* (unlike a corporate
  balance sheet, which must be inferred via §2.4). We therefore use the **structural** form for
  per-position liquidation risk ([03](03_distance_to_liquidation.md)) and the **reduced-form**
  ([05](05_reduced_form_hazard.md)) for stablecoin de-peg intensity, where there is no asset
  barrier.
- **What transfers to DeFi:** the distance-to-default *machinery* (2.3)–(2.4). In DeFi the
  inversion (§2.4) is **unnecessary** because $C_t$ (collateral) and $B_t$ (debt) are observed
  on-chain in real time — a genuine simplification that *strengthens* the model's applicability.
  This is the key insight formalized next.

---

## 2.7 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| D-2.1 | Merton PD | $\mathrm{PD}=\Phi\big(\frac{\ln(D/V_0)-(\mu_V-\frac12\sigma_V^2)T}{\sigma_V\sqrt T}\big)=\Phi(-\mathrm{DD})$ |
| D-2.2 | Equity↔asset system | (2.5) & (2.7) jointly determine $(V_0,\sigma_V)$ |
| def. | Distance-to-default | (2.4) |

---

Previous: [01 — GBM](01_geometric_brownian_motion.md) · Next: [03 — Distance-to-Liquidation](03_distance_to_liquidation.md)

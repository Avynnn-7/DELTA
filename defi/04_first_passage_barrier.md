# 04 — First-Passage (Barrier) Models: Liquidation Before the Horizon

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

The terminal-horizon liquidation probability (3.3) ignores breaches that occur *during*
$[0,T]$. The mathematically correct object is the **first-passage probability** of the
collateral process to the liquidation barrier. This is the Black & Cox (1976) extension of
Merton, and it yields the inverse-Gaussian first-passage law. Because DeFi liquidation is a
*continuously-monitored, path-dependent* event, this — not the terminal form — is the
**primary** per-position metric.

---

## 4.1 The first-passage time

Let $X_t = \ln(C_t/C_0)$ be the log-collateral process. From (1.3),

$$
X_t = m t + \sigma W_t, \qquad m := \mu - \tfrac12\sigma^2, \tag{4.1}
$$

an **arithmetic Brownian motion** with drift $m$ and volatility $\sigma$. Liquidation first
occurs when $C_t$ hits $B/\ell$ from above, i.e. when $X_t$ hits the barrier

$$
b := \ln\!\Big(\frac{B}{\ell C_0}\Big) = -\ln H_0 < 0 \quad(\text{for a healthy position, } H_0>1). \tag{4.2}
$$

**Definition 4.1 (First-passage time).**

$$
\tau_b = \inf\{t \ge 0 : X_t \le b\}. \tag{4.3}
$$

The liquidation-by-$T$ probability is $\mathrm{PL}^{\mathrm{FP}}(T) = \mathbb{P}(\tau_b \le T)$,
which **dominates** the terminal form: $\mathbb{P}(\tau_b\le T) \ge \mathbb{P}(X_T\le b)$ since
$\{X_T\le b\}\subseteq\{\tau_b\le T\}$. ✔ (This inequality is the formal statement of gap G-3.)

---

## 4.2 The reflection principle and the hitting-time law (derivation)

**Driftless case first ($m=0$).** For standard BM scaled by $\sigma$, the reflection principle
(Karatzas & Shreve, 1991, §2.6) gives the running minimum law. With $b<0$,

$$
\mathbb{P}\big(\min_{0\le s\le t} \sigma W_s \le b\big)
= 2\,\mathbb{P}(\sigma W_t \le b)
= 2\,\Phi\!\Big(\frac{b}{\sigma\sqrt t}\Big). \tag{4.4}
$$

**With drift ($m\ne0$): the Girsanov / Cameron–Martin tilt.** Changing measure to remove the
drift introduces an exponential weight $e^{mb/\sigma^2}$ on the reflected path (the
Cameron–Martin–Girsanov density). The classical result (Harrison, 1985, §1.8; Borodin &
Salminen, 2002, formula 2.0.2) for the first passage of $X_t = mt+\sigma W_t$ to level $b<0$ is

$$
\boxed{\
\mathbb{P}(\tau_b \le T)
= \Phi\!\left(\frac{b - mT}{\sigma\sqrt T}\right)
+ e^{\,2 m b/\sigma^2}\,\Phi\!\left(\frac{b + mT}{\sigma\sqrt T}\right).\ } \tag{4.5}
$$

This is **Result D-4.1**. Substituting $b=-\ln H_0$ and $m=\mu-\tfrac12\sigma^2$ gives the
liquidation probability in engine variables (worked out and verified in
[12](12_verification_pass_2.md) §A-4).

**Sanity checks (also in Pass 2):**
- First term equals the terminal form (3.3): $\Phi\big(\frac{b-mT}{\sigma\sqrt T}\big)=\mathbb P(X_T\le b)$. The second term, being positive, is exactly the **path correction** — confirming $\mathrm{PL}^{\mathrm{FP}}\ge\mathrm{PL}$. ✔
- Driftless limit $m\to0$: (4.5) → $2\Phi(b/\sigma\sqrt T)$, matching (4.4). ✔
- $H_0\to1^+ \Rightarrow b\to0^- \Rightarrow$ both terms $\to\Phi(\mp mT/\sigma\sqrt T)$ summing to a value $\to 1$ as the buffer vanishes (verified). ✔

---

## 4.3 The density: inverse Gaussian

Differentiating (4.5) in $T$ (or directly, Schrödinger 1915; Folks & Chhikara 1978) gives the
first-passage **density**, which is the **inverse Gaussian** distribution:

$$
f_{\tau_b}(t) = \frac{|b|}{\sigma\sqrt{2\pi t^3}}\,
\exp\!\left(-\frac{(b - m t)^2}{2\sigma^2 t}\right), \qquad t>0. \tag{4.6}
$$

This is **Result D-4.2**. The IG law is the canonical hitting-time distribution of Brownian
motion with drift (Chhikara & Folks, 1989), giving the engine an exact distribution of *when*
liquidation occurs — usable for expected-time-to-liquidation and hazard extraction
([05](05_reduced_form_hazard.md) §5.7).

**Defective-distribution subtlety (important).** If the drift pushes *away* from the barrier
($m>0$, i.e. $\mu>\tfrac12\sigma^2$), the barrier may never be hit:
$\mathbb{P}(\tau_b<\infty) = e^{2mb/\sigma^2} < 1$ (since $b<0$). The IG density (4.6) then
integrates to $e^{2mb/\sigma^2}$, not 1 — a **defective** distribution. This is mathematically
essential and a classic source of error; it is explicitly verified in
[12](12_verification_pass_2.md) §A-4 (Result R-4.3) and noted as audit item A-4.

---

## 4.4 Why Black–Cox/first-passage is the right model for DeFi

1. **Liquidations are continuously monitored.** Keepers can liquidate the instant
   $H_t\le1$; the event is genuinely path-dependent, exactly what first passage captures and
   the terminal Merton form does not (Black & Cox, 1976, introduced this for *safety covenants*
   — economically the same as a liquidation threshold).
2. **Closed form.** (4.5) is analytic, so the hot path stays $O(1)$ per position (a few $\Phi$
   evaluations), preserving the real-time requirement without sacrificing correctness.
3. **Exact timing law.** (4.6) supports time-to-liquidation analytics no terminal model can
   provide.

---

## 4.5 Assumptions and limitations

| Assumption | Limitation | Mitigation |
|------------|-----------|------------|
| Continuous monitoring & instant liquidation (A7) | Oracle latency, keeper delay, gas spikes mean liquidation is *not* instantaneous | Latency/MEV modeled in [08](08_monte_carlo_cascade.md); (4.5) is an idealized bound |
| Constant barrier $b$ | Debt accrues interest (barrier moves) | Use ratio process, $\mu\to\mu-r_b$ (R-3.3); barrier constant in ratio coordinates |
| GBM / no jumps (A2,A3) | De-pegs & flash-crashes jump over the barrier | Jump-diffusion first passage (Kou & Wang, 2003) noted as principled extension |
| Single barrier | Multi-collateral positions have a barrier *surface* | Portfolio simulation ([08](08_monte_carlo_cascade.md)) handles joint barriers |

---

## 4.6 Results established here

| ID | Result | Statement |
|----|--------|-----------|
| def. | First-passage time | $\tau_b=\inf\{t:X_t\le b\}$, $b=-\ln H_0$ |
| D-4.1 | First-passage CDF | $\mathbb P(\tau_b\le T)=\Phi(\frac{b-mT}{\sigma\sqrt T})+e^{2mb/\sigma^2}\Phi(\frac{b+mT}{\sigma\sqrt T})$ |
| D-4.2 | First-passage density | inverse Gaussian, (4.6) |
| R-4.3 | Defect mass | $\mathbb P(\tau_b<\infty)=e^{2mb/\sigma^2}$ when $m>0$ (Pass 2) |

---

Previous: [03 — Distance-to-Liquidation](03_distance_to_liquidation.md) · Next: [05 — Reduced-Form Hazard](05_reduced_form_hazard.md)

# 10 — Numerical Methods

> **DELTA** — Crypto Default & Contagion Risk Analyser · Mathematical Framework

Every closed form above ($\Phi$, $\Phi^{-1}$, the Merton inversion, copula sampling) must be
evaluated numerically with controlled error. This file records the algorithms, their accuracy
guarantees, and their assumptions — the bridge from mathematics to a correct implementation.
Numerical inaccuracy is a legitimate source of *mathematical* error, so each method's error
bound is stated.

---

## 10.1 Standard normal CDF $\Phi$

$\Phi$ appears in every PD/PL/DD/DTL formula. Options:

- **Via the error function:** $\Phi(x) = \tfrac12\big(1 + \mathrm{erf}(x/\sqrt2)\big)$. Use a
  vendor `erf`/`erfc`; `erfc` is preferred in the **left tail** to avoid catastrophic
  cancellation when $\Phi(x)\approx0$ (use $\Phi(x)=\tfrac12\mathrm{erfc}(-x/\sqrt2)$).
- **Cody (1969) rational Chebyshev** approximation for `erf`: the standard
  machine-precision ($\sim10^{-16}$) algorithm used by most libraries.
- **Tail accuracy matters here.** Liquidation probabilities live in the tail; relative error in
  $\Phi(-\mathrm{DTL})$ for large DTL must stay small, so absolute-error approximations
  (e.g. Abramowitz & Stegun 7.1.26, $\sim10^{-7}$ absolute) are **insufficient** for deep tails.
  Recommendation: `erfc`-based evaluation. Noted as numerical requirement N-1.

Reference: Cody (1969); Abramowitz & Stegun (1964, Ch. 7).

---

## 10.2 Inverse normal CDF $\Phi^{-1}$ (quantile)

Needed for copula thresholds (7.5), default barriers, VaR levels, and Gaussian sampling.

- **Acklam's algorithm:** rational approximation with relative error $\sim1.15\times10^{-9}$,
  refinable to machine precision with one Halley step. Widely used and fast.
- **Moro (1995):** the finance-standard hybrid (Beasley–Springer central region + Chebyshev
  tails), accurate to $\sim10^{-9}$ in the tails — designed precisely for the deep-tail accuracy
  that risk applications need.
- **Wichura (1988) AS 241:** $\sim10^{-16}$, the reference-grade choice.

Recommendation: **Wichura AS 241** (or Acklam + Halley refinement) for tail fidelity consistent
with N-1. Reference: Moro (1995); Wichura (1988); Acklam (2003).

---

## 10.3 Root-finding for the Merton inversion

The equity↔asset system (D-2.2, eqs 2.5 & 2.7) is solved for $(V_0,\sigma_V)$.

- **2-D Newton–Raphson.** Quadratic local convergence (Nocedal & Wright, 2006, Thm 11.2) given a
  good start; the Jacobian uses $\partial S_0/\partial V_0=\Phi(d_1)$ (vega/delta entries known
  in closed form). Start from $V_0\approx S_0+De^{-rT}$, $\sigma_V\approx\sigma_S S_0/V_0$.
- **Duan (1994) MLE / KMV iteration.** A globally more robust fixed-point alternative that
  iterates implied asset values to convergence; preferred when Newton diverges.
- **1-D safeguarded methods** (Brent, 1973) for any scalar calibration (e.g. implied vol, hazard
  bootstrap): combine bisection's guaranteed convergence with superlinear secant/IQI speed.

For DeFi, recall this inversion is **usually unnecessary** ([03](03_distance_to_liquidation.md)):
$C_0,B_0$ are observed on-chain, so root-finding is reserved for parameter calibration
(GARCH MLE, hazard bootstrap, t-copula $\nu$). Reference: Nocedal & Wright (2006); Brent (1973);
Duan (1994).

---

## 10.4 Cholesky factorization for correlated sampling

To draw correlated normals $\mathbf X\sim\mathcal N(0,R)$ for the copula
([07](07_copula_dependence.md)): factor $R = LL^\top$ (lower-triangular $L$) and set
$\mathbf X = L\mathbf z$ with $\mathbf z\sim\mathcal N(0,I)$. Then
$\mathrm{Cov}(\mathbf X)=L\,\mathrm{Cov}(\mathbf z)\,L^\top = LL^\top = R$ ✔. **Result D-10.1**
(verified in [12](12_verification_pass_2.md) §A-10).

- Exists & is unique for **symmetric positive-definite** $R$ (Golub & Van Loan, 2013, Thm 4.2.7);
  cost $O(d^3)$, done **once** then reused across all $N$ scenarios.
- **One-factor shortcut:** with structure (7.3) no factorization is needed — sample $Z$ and
  $\varepsilon_i$ directly in $O(d)$ per scenario. This is the engine's fast path.
- **Near-singular $R$** (empirical correlation matrices often are): repair to the nearest PD
  matrix (Higham, 2002) or use an eigenvalue floor before factorization. Noted as N-2.

Reference: Golub & Van Loan (2013); Higham (2002); Glasserman (2004, §2.3.3).

---

## 10.5 Random number generation

MC quality depends on the RNG (Glasserman, 2004, §2.1):

- **Mersenne Twister** (Matsumoto & Nishimura, 1998): period $2^{19937}-1$, the long-standing
  default; adequate but fails some empirical tests and is slow to seed.
- **PCG** (O'Neill, 2014) / **xoshiro256\*\*** (Blackman & Vigna, 2018): faster, better
  statistical quality, small state — preferred for high-throughput simulation.
- **Counter-based (Philox)** (Salmon et al., 2011): trivially parallel and reproducible across
  threads — ideal for the multithreaded cascade, since each scenario/thread can draw an
  independent, reproducible substream **without** synchronization. Recommended for the parallel
  engine. Noted as N-3.
- **Normal generation:** invert via $\Phi^{-1}$ (§10.2, preserves low-discrepancy structure for
  QMC) rather than Box–Muller when using Sobol' points.

Reference: L'Ecuyer (1999); Matsumoto & Nishimura (1998); Salmon et al. (2011).

---

## 10.6 Numerical integration & special functions

- **Multivariate normal/t CDF** ($\Phi_R$, $t_{R,\nu}$ in the copula): no closed form for
  $d>2$; use the Genz (1992) separation-of-variables QMC algorithm (the standard `mvtnorm`
  method).
- **Incomplete gamma / chi-square** (for the t-copula mixing $S\sim\chi^2_\nu$ and CIR survival):
  Lentz continued fractions (Press et al., 2007, §6.2).
- **Numerical stability rules** (applied throughout): compute in **log-space** where possible
  (avoid under/overflow in products of small probabilities); use `log1p`/`expm1` for
  $\ln(1+x)$, $e^x-1$ near 0; prefer `erfc` over `1-erf` in tails (§10.1).

Reference: Genz (1992); Press et al. (2007).

---

## 10.7 Error budget (end-to-end)

The total error in a reported risk number decomposes as

$$
\text{error} \le \underbrace{\epsilon_{\text{model}}}_{\text{spec. error (Parts 1–9)}}
+ \underbrace{\epsilon_{\text{param}}}_{\text{estimation, }O(1/\sqrt{n_{\text{data}}})}
+ \underbrace{\epsilon_{\text{MC}}}_{O(1/\sqrt N),\ \text{(8.3)}}
+ \underbrace{\epsilon_{\text{num}}}_{\text{float/approx, §10.1–10.6}}. \tag{10.1}
$$

The engineering goal is to make $\epsilon_{\text{num}}\ll\epsilon_{\text{MC}}\ll
\epsilon_{\text{param}}$, so that **numerical error never dominates** and the binding
uncertainty is statistical (controllable via $N$ and data). This budget is the practical
statement of "mathematical correctness first": we refuse to let avoidable floating-point or
approximation error contaminate the result. Discussed in [11](11_audit_pass_1.md) §numerics.

---

## 10.8 Results / requirements established here

| ID | Item | Statement |
|----|------|-----------|
| D-10.1 | Cholesky correctness | $\mathbf X=L\mathbf z$, $R=LL^\top \Rightarrow \mathrm{Cov}(\mathbf X)=R$ |
| N-1 | Tail-accurate $\Phi,\Phi^{-1}$ | `erfc`-based; Wichura/Moro for quantile tails |
| N-2 | PD repair | nearest-PD (Higham) for empirical $R$ |
| N-3 | Parallel RNG | counter-based (Philox) substreams |

---

Previous: [09 — Risk Measures](09_risk_measures.md) · Next: [11 — Audit Pass 1](11_audit_pass_1.md)

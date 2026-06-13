import numpy as np
from scipy import stats

from engine.structural import dtl, firstpassage


def _bridge_corrected_passage(b, m, sigma, T, n_paths, n_steps, seed):
    dt = T / n_steps
    gen = np.random.default_rng(seed)
    x = np.zeros(n_paths)
    crossed = np.zeros(n_paths, dtype=bool)
    for _ in range(n_steps):
        increment = m * dt + sigma * np.sqrt(dt) * gen.standard_normal(n_paths)
        x_next = x + increment
        hit_endpoint = x_next <= b
        above = (~crossed) & (~hit_endpoint) & (x > b)
        bridge_prob = np.zeros(n_paths)
        bridge_prob[above] = np.exp(-2.0 * (x[above] - b) * (x_next[above] - b) / (sigma**2 * dt))
        bridge_hit = gen.random(n_paths) < bridge_prob
        crossed |= hit_endpoint | bridge_hit
        x = x_next
    return crossed.mean()


def test_first_passage_dominates_terminal():
    h0, mu, sigma = 1.5, 0.0, 0.5
    horizons = np.array([0.05, 0.1, 0.5, 1.0])
    fp = firstpassage.first_passage_cdf(h0, mu, sigma, horizons)
    terminal = firstpassage.terminal_cdf(h0, mu, sigma, horizons)
    assert np.all(fp >= terminal)
    assert np.all(fp[:-1] <= fp[1:] + 1e-12)


def test_terminal_cdf_matches_dtl_probability():
    h0, mu, sigma, T = 1.6, 0.0, 0.4, 0.5
    assert np.isclose(
        firstpassage.terminal_cdf(h0, mu, sigma, T),
        dtl.probability_of_liquidation(h0, mu, sigma, T),
    )


def test_driftless_limit_is_reflection_formula():
    h0, sigma, T = 1.5, 0.5, 0.7
    mu = 0.5 * sigma**2
    b = -np.log(h0)
    expected = 2.0 * stats.norm.cdf(b / (sigma * np.sqrt(T)))
    assert np.isclose(firstpassage.first_passage_cdf(h0, mu, sigma, T), expected)


def test_first_passage_cdf_matches_bridge_corrected_mc():
    h0, mu, sigma, T = 1.4, 0.0, 0.6, 0.5
    b = -np.log(h0)
    m = mu - 0.5 * sigma**2
    empirical = _bridge_corrected_passage(b, m, sigma, T, 300000, 400, 0)
    analytic = firstpassage.first_passage_cdf(h0, mu, sigma, T)
    assert abs(analytic - empirical) < 3e-3


def test_density_integrates_to_cdf():
    h0, mu, sigma, T = 1.5, -0.1, 0.5, 2.0
    t = np.linspace(1e-4, T, 200000)
    density = firstpassage.first_passage_density(h0, mu, sigma, t)
    integral = np.trapezoid(density, t)
    assert np.isclose(integral, firstpassage.first_passage_cdf(h0, mu, sigma, T), atol=2e-3)


def test_density_is_non_negative():
    h0, mu, sigma = 1.5, 0.2, 0.4
    t = np.linspace(1e-3, 5.0, 1000)
    assert np.all(firstpassage.first_passage_density(h0, mu, sigma, t) >= 0.0)


def test_defect_mass_when_drift_pushes_away():
    h0, sigma = 1.5, 0.3
    mu = 0.2
    m = mu - 0.5 * sigma**2
    assert m > 0.0
    b = -np.log(h0)
    expected = np.exp(2.0 * m * b / sigma**2)
    assert np.isclose(firstpassage.defect_mass(h0, mu, sigma), expected)
    assert expected < 1.0


def test_defect_mass_unit_when_drift_toward_barrier():
    h0, mu, sigma = 1.5, -0.1, 0.4
    assert np.isclose(firstpassage.defect_mass(h0, mu, sigma), 1.0)


def test_cdf_limit_equals_defect_mass():
    h0, mu, sigma = 1.5, 0.2, 0.3
    far = firstpassage.first_passage_cdf(h0, mu, sigma, 1e6)
    assert np.isclose(far, firstpassage.defect_mass(h0, mu, sigma), atol=1e-3)


def test_density_integrates_to_defect_mass_when_defective():
    h0, mu, sigma = 1.5, 0.2, 0.3
    t = np.linspace(1e-3, 4000.0, 4_000_000)
    density = firstpassage.first_passage_density(h0, mu, sigma, t)
    integral = np.trapezoid(density, t)
    assert np.isclose(integral, firstpassage.defect_mass(h0, mu, sigma), atol=3e-3)
    assert integral < 1.0

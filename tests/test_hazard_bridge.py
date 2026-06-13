import numpy as np

from engine.hazard import bridge
from engine.structural import firstpassage


def test_structural_survival_complements_first_passage():
    h0, mu, sigma = 1.5, -0.1, 0.5
    t = np.linspace(0.05, 2.0, 40)
    survival = bridge.structural_survival(h0, mu, sigma, t)
    cdf = firstpassage.first_passage_cdf(h0, mu, sigma, t)
    np.testing.assert_allclose(survival, 1.0 - cdf)


def test_structural_hazard_is_density_over_survival():
    h0, mu, sigma = 1.5, -0.1, 0.5
    t = np.linspace(0.05, 2.0, 40)
    hazard = bridge.structural_hazard(h0, mu, sigma, t)
    density = firstpassage.first_passage_density(h0, mu, sigma, t)
    survival = bridge.structural_survival(h0, mu, sigma, t)
    np.testing.assert_allclose(hazard, density / survival)


def test_integrated_structural_hazard_reproduces_survival():
    h0, mu, sigma = 1.5, -0.1, 0.5
    t = np.linspace(1e-4, 1.5, 400000)
    hazard = bridge.structural_hazard(h0, mu, sigma, t)
    cumulative = np.concatenate(([0.0], np.cumsum(0.5 * (hazard[1:] + hazard[:-1]) * np.diff(t))))
    implied_survival = np.exp(-cumulative)
    direct_survival = bridge.structural_survival(h0, mu, sigma, t)
    np.testing.assert_allclose(implied_survival, direct_survival, atol=2e-3)

import numpy as np
from scipy import stats

from engine.risk import var_es


def test_var_normal_quantile():
    generator = np.random.default_rng(0)
    losses = generator.standard_normal(2000000)
    alpha = 0.99
    estimate = var_es.value_at_risk(losses, alpha)
    assert abs(estimate - stats.norm.ppf(alpha)) < 5e-3


def test_es_conditional_normal():
    generator = np.random.default_rng(1)
    losses = generator.standard_normal(4000000)
    alpha = 0.975
    estimate = var_es.expected_shortfall_conditional(losses, alpha)
    analytic = stats.norm.pdf(stats.norm.ppf(alpha)) / (1.0 - alpha)
    assert abs(estimate - analytic) < 5e-3


def test_es_integral_equals_conditional_continuous():
    generator = np.random.default_rng(2)
    losses = generator.standard_normal(2000000)
    alpha = 0.95
    integral = var_es.expected_shortfall_integral(losses, alpha)
    conditional = var_es.expected_shortfall_conditional(losses, alpha)
    assert abs(integral - conditional) < 5e-3


def test_es_ge_var():
    generator = np.random.default_rng(3)
    losses = generator.standard_exponential(500000)
    alpha = 0.99
    var = var_es.value_at_risk(losses, alpha)
    es = var_es.expected_shortfall_conditional(losses, alpha)
    assert es >= var


def test_spectral_recovers_es():
    generator = np.random.default_rng(4)
    losses = generator.standard_normal(1000000)
    alpha = 0.95
    spectrum = var_es.expected_shortfall_spectrum(alpha)
    spectral = var_es.spectral_risk(losses, spectrum, nodes=4096)
    conditional = var_es.expected_shortfall_conditional(losses, alpha)
    assert abs(spectral - conditional) < 1e-2


def test_es_integral_exponential():
    generator = np.random.default_rng(5)
    losses = generator.standard_exponential(2000000)
    alpha = 0.99
    es = var_es.expected_shortfall_integral(losses, alpha)
    analytic = -np.log(1.0 - alpha) + 1.0
    assert abs(es - analytic) < 2e-2

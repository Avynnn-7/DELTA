import numpy as np
from scipy import stats

from engine.hazard import calibration


def test_credit_triangle():
    s, r = 0.02, 0.4
    assert np.isclose(calibration.credit_triangle_intensity(s, r), s / (1.0 - r))


def test_credit_triangle_rejects_full_recovery():
    try:
        calibration.credit_triangle_intensity(0.02, 1.0)
    except ValueError:
        return
    raise AssertionError("expected recovery>=1 to raise")


def test_poisson_mle():
    assert np.isclose(calibration.poisson_mle_intensity(7, 35.0), 0.2)


def test_poisson_mle_matches_simulation():
    lam_true = 0.5
    exposure = 100000.0
    gen = np.random.default_rng(0)
    count = gen.poisson(lam_true * exposure)
    estimate = calibration.poisson_mle_intensity(count, exposure)
    assert abs(estimate - lam_true) < 0.01


def test_gpd_fit_recovers_parameters():
    shape_true, scale_true = 0.25, 0.5
    exceedances = stats.genpareto.rvs(shape_true, scale=scale_true, size=200000, random_state=1)
    fit = calibration.fit_gpd(exceedances)
    assert abs(fit["shape"] - shape_true) < 0.03
    assert abs(fit["scale"] - scale_true) < 0.03


def test_gpd_loglik_matches_scipy():
    shape_true, scale_true = 0.2, 0.4
    exceedances = stats.genpareto.rvs(shape_true, scale=scale_true, size=20000, random_state=2)
    fit = calibration.fit_gpd(exceedances)
    direct = np.sum(stats.genpareto.logpdf(exceedances, fit["shape"], scale=fit["scale"]))
    assert np.isclose(fit["loglik"], direct, rtol=1e-8)


def test_gpd_tail_probability_matches_scipy():
    shape, scale, threshold, rate = 0.2, 0.4, 0.0, 0.05
    level = 1.5
    expected = rate * stats.genpareto.sf(level - threshold, shape, scale=scale)
    got = calibration.gpd_tail_exceedance_probability(level, threshold, shape, scale, rate)
    assert np.isclose(got, expected)


def test_logistic_hazard_recovers_coefficients():
    gen = np.random.default_rng(3)
    n = 200000
    covariate = gen.normal(size=n)
    design = np.column_stack([np.ones(n), covariate])
    beta_true = np.array([-1.0, 2.0])
    p = 1.0 / (1.0 + np.exp(-(design @ beta_true)))
    outcomes = (gen.random(n) < p).astype(float)
    fit = calibration.fit_logistic_hazard(design, outcomes)
    np.testing.assert_allclose(fit["coefficients"], beta_true, atol=0.03)


def test_logistic_hazard_probability():
    design = np.array([[1.0, 0.0], [1.0, 1.0]])
    beta = np.array([0.0, np.log(3.0)])
    probs = calibration.logistic_hazard_probability(design, beta)
    assert np.isclose(probs[0], 0.5)
    assert np.isclose(probs[1], 3.0 / 4.0)

import numpy as np
from scipy import special as sp
from scipy import stats

from engine.numerics import special


def test_incomplete_gamma_matches_scipy():
    a = 2.5
    x = np.linspace(0.1, 20.0, 50)
    np.testing.assert_allclose(special.lower_incomplete_gamma(a, x), sp.gammainc(a, x), rtol=1e-13)
    np.testing.assert_allclose(special.upper_incomplete_gamma(a, x), sp.gammaincc(a, x), rtol=1e-13)


def test_incomplete_gamma_inverse_roundtrip():
    a = 3.0
    p = np.linspace(0.01, 0.99, 50)
    x = special.lower_incomplete_gamma_inv(a, p)
    np.testing.assert_allclose(special.lower_incomplete_gamma(a, x), p, rtol=1e-12)


def test_chi2_cdf_and_ppf_match_scipy():
    for df in (1, 2, 5, 12):
        x = np.linspace(0.01, 30.0, 60)
        np.testing.assert_allclose(special.chi2_cdf(x, df), stats.chi2.cdf(x, df), rtol=1e-12)
        p = np.linspace(0.001, 0.999, 60)
        np.testing.assert_allclose(special.chi2_ppf(p, df), stats.chi2.ppf(p, df), rtol=1e-10)


def test_mvn_cdf_dim1_reduces_to_phi():
    est, err = special.mvn_cdf([0.5], [[1.0]])
    assert err == 0.0
    np.testing.assert_allclose(est, stats.norm.cdf(0.5), rtol=1e-12)


def test_mvn_cdf_dim2_matches_reference():
    rho = 0.5
    corr = [[1.0, rho], [rho, 1.0]]
    upper = [0.3, -0.7]
    est, err = special.mvn_cdf(upper, corr, samples=200000, seed=7)
    ref = stats.multivariate_normal(mean=[0.0, 0.0], cov=np.array(corr)).cdf(upper)
    assert abs(est - ref) < 5.0 * err + 1e-3


def test_mvt_cdf_dim1_matches_student_t():
    df = 6
    est, err = special.mvt_cdf([0.4], [[1.0]], df=df)
    assert err == 0.0
    np.testing.assert_allclose(est, stats.t.cdf(0.4, df), rtol=1e-12)


def test_mvt_cdf_dim2_matches_reference():
    df = 8
    rho = 0.3
    corr = [[1.0, rho], [rho, 1.0]]
    upper = [0.5, 0.2]
    est, err = special.mvt_cdf(upper, corr, df=df, samples=200000, seed=11)
    ref = stats.multivariate_t(loc=[0.0, 0.0], shape=np.array(corr), df=df).cdf(upper)
    assert abs(est - ref) < 5.0 * err + 5e-3


def test_error_budget_mc_dominates_numerical():
    rho = 0.4
    corr = [[1.0, rho], [rho, 1.0]]
    upper = [0.1, -0.2]
    est_a, err_a = special.mvn_cdf(upper, corr, samples=4000, seed=1)
    est_b, err_b = special.mvn_cdf(upper, corr, samples=400000, seed=1)
    assert err_a > 0.0 and err_b > 0.0
    assert err_b < err_a
    assert err_b > 1e-12


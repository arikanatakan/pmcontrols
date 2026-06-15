"""PERT: analytic three-point estimate and Monte Carlo schedule risk."""

import json
import pathlib

import pytest

import pmcontrols as pm

CASES = {
    c["id"]: c
    for c in json.loads(
        (pathlib.Path(__file__).parent / "validation_cases.json").read_text()
    )["cases"]
}


def test_hand_case_series():
    case = CASES["pert-hand-001"]
    r = pm.pert(case["inputs"]["activities"], n_sim=2000, seed=1)
    assert r.stats["expected_duration"] == pytest.approx(
        case["expected"]["expected_duration"], abs=case["tol"]
    )
    assert r.stats["sigma_critical_path"] == pytest.approx(
        case["expected"]["sigma_critical_path"], abs=1e-9
    )


def test_parallel_analytic():
    case = CASES["pert-parallel-002"]
    r = pm.pert(case["inputs"]["activities"], n_sim=2000, seed=1)
    assert r.stats["expected_duration"] == pytest.approx(8.0, abs=1e-9)
    assert r.stats["sigma_critical_path"] == pytest.approx(
        case["expected"]["sigma_critical_path"], abs=1e-9
    )


def test_monte_carlo_consistency():
    case = CASES["pert-hand-001"]
    r = pm.pert(case["inputs"]["activities"], n_sim=60_000, seed=7)
    assert r.stats["mc_mean"] == pytest.approx(7.0, abs=0.05)
    assert 3.0 <= r.stats["mc_p50"] <= 19.0


def test_criticality_index_general_foundry():
    acts = []
    for a in CASES["cpm-general-foundry-001"]["inputs"]["activities"]:
        d = a["duration"]
        acts.append(
            {
                "id": a["id"],
                "predecessors": a["predecessors"],
                "a": d * 0.8,
                "m": d,
                "b": d * 1.3,
            }
        )
    r = pm.pert(acts, n_sim=8000, seed=3)
    t = r.table.set_index("activity")
    assert t.loc["G", "criticality_index"] > t.loc["F", "criticality_index"]
    assert t.loc["E", "criticality_index"] > 0.5


def test_rejects_bad_three_point():
    with pytest.raises(ValueError):
        pm.pert([{"id": "A", "predecessors": [], "a": 5, "m": 2, "b": 9}])  # a > m


def test_monte_carlo_converges_to_analytic_mean():
    """The Monte Carlo mean converges to the analytic critical-path mean.

    The PERT-beta distribution is built so its mean equals te, so the sum over
    a series converges to the analytic expected duration. Variance is not
    asserted: the (b - a) / 6 standard deviation is an approximation that
    differs from the sampled beta's true variance, by design.
    """
    acts = [
        {"id": "A", "predecessors": [],    "a": 2, "m": 5, "b": 14},
        {"id": "B", "predecessors": ["A"], "a": 2, "m": 5, "b": 14},
        {"id": "C", "predecessors": ["B"], "a": 2, "m": 5, "b": 14},
    ]
    r = pm.pert(acts, n_sim=200_000, seed=0)
    assert r.stats["expected_duration"] == pytest.approx(18.0)   # 3 * te, te=6
    assert r.stats["mc_mean"] == pytest.approx(18.0, abs=0.1)
    assert r.stats["mc_p50"] < r.stats["mc_p80"] < r.stats["mc_p95"]


def test_monte_carlo_matches_analytic_beta():
    """A single activity: the simulated completion distribution matches the
    exact PERT-beta the sampler draws from, checked against scipy's closed-form
    beta (an independent reference). This validates the simulation engine: both
    the mean and an upper percentile converge to their analytic values.
    """
    from scipy.stats import beta as beta_dist

    a, m, b = 2.0, 5.0, 14.0
    alpha = 1 + 4 * (m - a) / (b - a)   # 2
    beta = 6 - alpha                    # 4
    r = pm.pert([{"id": "X", "predecessors": [], "a": a, "m": m, "b": b}],
                n_sim=300_000, seed=0)
    analytic_mean = a + (b - a) * alpha / (alpha + beta)
    analytic_p80 = a + (b - a) * beta_dist.ppf(0.80, alpha, beta)
    assert r.stats["mc_mean"] == pytest.approx(analytic_mean, abs=0.03)
    assert r.stats["mc_p80"] == pytest.approx(analytic_p80, abs=0.05)

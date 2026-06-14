"""EVM and earned schedule against a frozen PMB."""

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


def _pmb(case):
    return pm.plan(case["inputs"]["periods"], case["inputs"]["pv"])


def _check_expected(r, case):
    for k, v in case["expected"].items():
        assert r.stats[k] == pytest.approx(v, abs=case["tol"] * max(1, abs(v))), k


def test_hand_case_full_indicator_set():
    case = CASES["evm-hand-001"]
    r = pm.evm(_pmb(case), ev=case["inputs"]["ev"], ac=case["inputs"]["ac"],
               at=case["inputs"]["at"])
    _check_expected(r, case)


def test_on_plan_case():
    case = CASES["evm-on-plan-002"]
    r = pm.evm(_pmb(case), ev=case["inputs"]["ev"], ac=case["inputs"]["ac"],
               at=case["inputs"]["at"])
    assert r.ok  # CPI = SPI(t) = 1.0, no breach
    _check_expected(r, case)


def test_ahead_and_under_budget_case():
    case = CASES["evm-ahead-003"]
    r = pm.evm(_pmb(case), ev=case["inputs"]["ev"], ac=case["inputs"]["ac"],
               at=case["inputs"]["at"])
    assert r.ok
    assert r.stats["vac"] > 0  # under budget
    _check_expected(r, case)


def test_alerts_fire_below_threshold():
    case = CASES["evm-hand-001"]
    r = pm.evm(_pmb(case), ev=30_000, ac=35_000, at=4)
    assert not r.ok
    assert {a.indicator for a in r.alerts} == {"cpi", "spi_t"}


def test_on_plan_project_is_ok():
    case = CASES["evm-hand-001"]
    r = pm.evm(_pmb(case), ev=40_000, ac=40_000, at=4)
    assert r.ok
    assert r.stats["cpi"] == pytest.approx(1.0)
    assert r.stats["spi_t"] == pytest.approx(1.0)
    assert r.stats["ieac_t"] == pytest.approx(10.0)


def test_custom_thresholds():
    case = CASES["evm-hand-001"]
    # On-plan project, but a strict threshold should still flag nothing here.
    r = pm.evm(_pmb(case), ev=40_000, ac=40_000, at=4,
               thresholds={"cpi": 0.99, "spi_t": 0.99})
    assert r.ok


def test_earned_schedule_interpolation_linear():
    case = CASES["es-interp-001"]
    pmb = pm.plan(case["inputs"]["periods"], case["inputs"]["pv"])
    es = pm.earned_schedule(pmb, case["inputs"]["ev"])
    assert es == pytest.approx(case["expected"]["es"], abs=case["tol"])


def test_earned_schedule_interpolation_nonlinear():
    case = CASES["es-interp-003"]
    pmb = pm.plan(case["inputs"]["periods"], case["inputs"]["pv"])
    es = pm.earned_schedule(pmb, case["inputs"]["ev"])
    assert es == pytest.approx(case["expected"]["es"], abs=case["tol"])


def test_earned_schedule_identity_spi_t():
    case = CASES["evm-hand-001"]
    r = pm.evm(_pmb(case), ev=34_000, ac=34_000, at=5)
    assert r.stats["spi_t"] == pytest.approx(r.stats["es"] / 5)


def test_pmb_roundtrip(tmp_path):
    case = CASES["evm-hand-001"]
    pmb = _pmb(case)
    path = pmb.save(tmp_path / "pmb.json")
    loaded = pm.PMB.load(path)
    assert loaded.pv == pmb.pv and loaded.bac == pmb.bac
    r = pm.evm(str(path), ev=30_000, ac=35_000, at=4)
    assert r.stats["cpi"] == pytest.approx(6 / 7)


def test_pmb_rejects_decreasing_pv():
    with pytest.raises(ValueError):
        pm.plan([0, 1, 2], [0, 100, 50])


def test_pmb_requires_two_points():
    with pytest.raises(ValueError):
        pm.plan([0], [0])


def test_evm_rejects_ev_above_bac():
    case = CASES["evm-hand-001"]
    with pytest.raises(ValueError):
        pm.evm(_pmb(case), ev=200_000, ac=10_000, at=4)

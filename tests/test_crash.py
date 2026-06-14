"""Crashing: the minimum-cost time/cost trade-off linear program."""

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


def test_general_foundry_to_14():
    case = CASES["crash-general-foundry-001"]
    r = pm.crash(case["inputs"]["activities"], target=14)
    assert r.stats["total_crash_cost"] == pytest.approx(
        case["expected"]["cost_to_14"], abs=case["tol"]
    )
    assert r.stats["achieved_duration"] <= 14 + 1e-9


def test_general_foundry_to_13():
    case = CASES["crash-general-foundry-001"]
    r = pm.crash(case["inputs"]["activities"], target=13)
    assert r.stats["total_crash_cost"] == pytest.approx(
        case["expected"]["cost_to_13"], abs=case["tol"]
    )
    assert r.stats["achieved_duration"] <= 13 + 1e-9


def test_cost_monotone_in_target():
    acts = CASES["crash-general-foundry-001"]["inputs"]["activities"]
    costs = [pm.crash(acts, target=t).stats["total_crash_cost"] for t in (14, 13, 12)]
    assert costs[0] < costs[1] < costs[2]


def test_respects_bounds():
    acts = CASES["crash-general-foundry-001"]["inputs"]["activities"]
    r = pm.crash(acts, target=13)
    t = r.table.set_index("activity")
    for a in acts:
        max_crash = a["duration"] - a["crash_duration"]
        assert t.loc[a["id"], "crash_amount"] <= max_crash + 1e-9


def test_target_above_normal_raises():
    acts = CASES["crash-general-foundry-001"]["inputs"]["activities"]
    with pytest.raises(ValueError):
        pm.crash(acts, target=16)


def test_rejects_crash_longer_than_normal():
    with pytest.raises(ValueError):
        pm.crash(
            [
                {
                    "id": "A",
                    "predecessors": [],
                    "duration": 2,
                    "crash_duration": 3,
                    "crash_cost": 100,
                }
            ],
            target=1,
        )


def test_result_table_has_crash_columns():
    acts = CASES["crash-general-foundry-001"]["inputs"]["activities"]
    r = pm.crash(acts, target=14)
    for col in ("normal_duration", "crash_amount", "crash_cost"):
        assert col in r.table.columns

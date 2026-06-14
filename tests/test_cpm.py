"""CPM: forward/backward pass, slack, critical path."""

import json
import pathlib

import numpy as np
import pytest

import pmcontrols as pm

CASES = {
    c["id"]: c
    for c in json.loads(
        (pathlib.Path(__file__).parent / "validation_cases.json").read_text()
    )["cases"]
}


def test_general_foundry_full_schedule():
    case = CASES["cpm-general-foundry-001"]
    r = pm.cpm(case["inputs"]["activities"])
    assert r.stats["project_duration"] == pytest.approx(
        case["expected"]["project_duration"]
    )
    assert r.meta["critical_activities"] == case["expected"]["critical_path"]
    t = r.table.set_index("activity")
    for act, exp in case["expected"]["schedule"].items():
        for k, v in exp.items():
            assert t.loc[act, k] == pytest.approx(v, abs=case["tol"]), (act, k)


def test_series_parallel_critical_path():
    case = CASES["cpm-series-parallel-002"]
    r = pm.cpm(case["inputs"]["activities"])
    assert r.stats["project_duration"] == 9
    assert r.meta["critical_activities"] == ["A", "C", "D"]


def test_predecessors_as_comma_string():
    r = pm.cpm(
        [
            {"id": "A", "predecessors": "", "duration": 1},
            {"id": "B", "predecessors": "A", "duration": 1},
            {"id": "C", "predecessors": "A, B", "duration": 1},
        ]
    )
    assert r.stats["project_duration"] == 3


def test_rejects_unknown_predecessor():
    with pytest.raises(ValueError):
        pm.cpm([{"id": "A", "predecessors": ["Z"], "duration": 1}])


def test_rejects_cycle_with_clear_message():
    with pytest.raises(ValueError, match="cycle"):
        pm.cpm(
            [
                {"id": "A", "predecessors": ["B"], "duration": 1},
                {"id": "B", "predecessors": ["A"], "duration": 1},
            ]
        )


def test_rejects_negative_duration():
    with pytest.raises(ValueError):
        pm.cpm([{"id": "A", "predecessors": [], "duration": -1}])


def test_rejects_duplicate_id():
    with pytest.raises(ValueError):
        pm.cpm(
            [
                {"id": "A", "predecessors": [], "duration": 1},
                {"id": "A", "predecessors": [], "duration": 2},
            ]
        )


def test_slack_identity():
    r = pm.cpm(CASES["cpm-general-foundry-001"]["inputs"]["activities"])
    t = r.table
    assert np.allclose(t["slack"], t["ls"] - t["es"])
    assert np.allclose(t["slack"], t["lf"] - t["ef"])


def test_result_to_dict_is_json_safe():
    r = pm.cpm(CASES["cpm-general-foundry-001"]["inputs"]["activities"])
    d = r.to_dict()
    assert d["schema"] == 1 and d["method"] == "cpm"
    assert "project_duration" in d["stats"]
    json.dumps(d)  # must not raise

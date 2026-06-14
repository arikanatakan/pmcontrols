"""Generic driver: every case in validation_cases.json is reproduced by
the corresponding function, so new cases are covered automatically.

Each case ships with its full derivation in the JSON file; this module
turns the whole file into one parametrized check per method.
"""

import json
import pathlib

import pytest

import pmcontrols as pm

CASES = json.loads(
    (pathlib.Path(__file__).parent / "validation_cases.json").read_text()
)["cases"]


def _by(method):
    cases = [c for c in CASES if c["method"] == method]
    return {"argvalues": cases, "ids": [c["id"] for c in cases]}


@pytest.mark.parametrize("case", **_by("cpm"))
def test_cpm_cases(case):
    r = pm.cpm(case["inputs"]["activities"])
    exp = case["expected"]
    assert r.stats["project_duration"] == pytest.approx(
        exp["project_duration"], abs=case["tol"]
    )
    assert r.meta["critical_activities"] == exp["critical_path"]
    t = r.table.set_index("activity")
    for act, fields in exp["schedule"].items():
        for k, v in fields.items():
            assert t.loc[act, k] == pytest.approx(v, abs=case["tol"]), (
                case["id"], act, k
            )


@pytest.mark.parametrize("case", **_by("pert"))
def test_pert_cases(case):
    r = pm.pert(case["inputs"]["activities"], n_sim=2000, seed=1)
    for k, v in case["expected"].items():
        assert r.stats[k] == pytest.approx(v, abs=case["tol"]), (case["id"], k)


@pytest.mark.parametrize("case", **_by("evm"))
def test_evm_cases(case):
    inp = case["inputs"]
    pmb = pm.plan(inp["periods"], inp["pv"])
    r = pm.evm(pmb, ev=inp["ev"], ac=inp["ac"], at=inp["at"])
    for k, v in case["expected"].items():
        assert r.stats[k] == pytest.approx(v, abs=case["tol"] * max(1, abs(v))), (
            case["id"], k
        )


@pytest.mark.parametrize("case", **_by("earned_schedule"))
def test_earned_schedule_cases(case):
    inp = case["inputs"]
    pmb = pm.plan(inp["periods"], inp["pv"])
    es = pm.earned_schedule(pmb, inp["ev"])
    assert es == pytest.approx(case["expected"]["es"], abs=case["tol"])

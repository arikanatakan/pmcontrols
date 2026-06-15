"""Gantt plotting (optional matplotlib feature)."""

import pytest

import pmcontrols as pm

pytest.importorskip("matplotlib")

FOUNDRY = [
    {"id": "A", "predecessors": [], "duration": 2},
    {"id": "B", "predecessors": [], "duration": 3},
    {"id": "C", "predecessors": ["A"], "duration": 2},
    {"id": "D", "predecessors": ["B"], "duration": 4},
    {"id": "E", "predecessors": ["C"], "duration": 4},
    {"id": "F", "predecessors": ["C"], "duration": 3},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2},
]


def test_gantt_returns_figure_with_a_bar_per_activity():
    import matplotlib
    matplotlib.use("Agg")
    r = pm.cpm(FOUNDRY)
    fig, ax = pm.gantt(r)
    # one broken_barh collection per activity, plus the slack bars.
    assert len(ax.collections) >= len(FOUNDRY)
    assert ax.get_yticks().tolist() == list(range(len(FOUNDRY)))
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_gantt_works_on_a_crash_result():
    import matplotlib
    matplotlib.use("Agg")
    crash_acts = [
        {"id": "A", "predecessors": [], "duration": 2, "crash_duration": 1, "crash_cost": 1000},
        {"id": "B", "predecessors": ["A"], "duration": 4, "crash_duration": 2, "crash_cost": 1000},
    ]
    r = pm.crash(crash_acts, target=5)
    fig, ax = pm.gantt(r)
    assert ax.get_title()
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_gantt_rejects_non_schedule_result():
    pmb = pm.plan([0, 1, 2], [0, 50, 100])
    r = pm.evm(pmb, ev=40, ac=45, at=1)
    with pytest.raises(ValueError):
        pm.gantt(r)


def _three_point():
    return [
        {"id": a["id"], "predecessors": a["predecessors"],
         "a": a["duration"] * 0.8, "m": a["duration"], "b": a["duration"] * 1.3}
        for a in FOUNDRY
    ]


def test_evm_curve():
    import matplotlib
    matplotlib.use("Agg")
    pmb = pm.plan([0, 1, 2, 3, 4], [0, 25, 50, 75, 100])
    r = pm.evm(pmb, ev=40, ac=45, at=2)
    fig, ax = pm.evm_curve(pmb, r)
    assert ax.get_title()
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_network_diagram():
    import matplotlib
    matplotlib.use("Agg")
    fig, ax = pm.network_diagram(pm.cpm(FOUNDRY))
    assert ax.get_title()
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_criticality():
    import matplotlib
    matplotlib.use("Agg")
    fig, ax = pm.criticality(pm.pert(_three_point(), n_sim=2000, seed=1))
    assert ax.get_title()
    import matplotlib.pyplot as plt
    plt.close(fig)


def test_mc_distribution_requires_samples():
    import matplotlib
    matplotlib.use("Agg")
    with pytest.raises(ValueError):
        pm.mc_distribution(pm.pert(_three_point(), n_sim=1000, seed=1))
    r = pm.pert(_three_point(), n_sim=2000, seed=1, keep_samples=True)
    fig, ax = pm.mc_distribution(r)
    assert ax.get_title()
    import matplotlib.pyplot as plt
    plt.close(fig)

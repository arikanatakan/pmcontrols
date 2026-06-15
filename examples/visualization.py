"""Render every pmcontrols chart to a PNG.

Visualization is optional and lives behind the plotting extra:

    pip install "pmcontrols[plot]"

Run with:

    python examples/visualization.py
"""

import pmcontrols as pm

# The standard General Foundry network (schedule), reused for the schedule
# charts, plus a three-point version for the risk charts.
ACTIVITIES = [
    {"id": "A", "predecessors": [],         "duration": 2},
    {"id": "B", "predecessors": [],         "duration": 3},
    {"id": "C", "predecessors": ["A"],      "duration": 2},
    {"id": "D", "predecessors": ["B"],      "duration": 4},
    {"id": "E", "predecessors": ["C"],      "duration": 4},
    {"id": "F", "predecessors": ["C"],      "duration": 3},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2},
]

THREE_POINT = [
    {"id": a["id"], "predecessors": a["predecessors"],
     "a": a["duration"] * 0.8, "m": a["duration"], "b": a["duration"] * 1.6}
    for a in ACTIVITIES
]


def main() -> None:
    # Schedule charts from a critical-path result.
    schedule = pm.cpm(ACTIVITIES)
    pm.gantt(schedule)[0].savefig("gantt.png", dpi=150, bbox_inches="tight")
    pm.network_diagram(schedule)[0].savefig(
        "network.png", dpi=150, bbox_inches="tight"
    )

    # Risk charts from a Monte Carlo PERT result (keep_samples for the histogram).
    risk = pm.pert(THREE_POINT, keep_samples=True)
    pm.criticality(risk)[0].savefig(
        "criticality.png", dpi=150, bbox_inches="tight"
    )
    pm.mc_distribution(risk)[0].savefig(
        "completion_distribution.png", dpi=150, bbox_inches="tight"
    )

    # Earned value S-curve from a frozen baseline and a status reading.
    pmb = pm.plan(list(range(11)), [i * 10_000 for i in range(11)])
    evm = pm.evm(pmb, ev=30_000, ac=35_000, at=4)
    pm.evm_curve(pmb, evm)[0].savefig(
        "earned_value.png", dpi=150, bbox_inches="tight"
    )

    print(
        "Saved gantt.png, network.png, criticality.png, "
        "completion_distribution.png, earned_value.png"
    )


if __name__ == "__main__":
    main()

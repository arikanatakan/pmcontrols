"""Quickstart example for pmcontrols.

Runs the General Foundry network end to end: critical path, schedule
risk, crashing, and an earned value status check. Run with:

    python examples/quickstart.py
"""

import pmcontrols as pm

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

CRASH = [
    {"id": "A", "predecessors": [],         "duration": 2, "crash_duration": 1, "crash_cost": 1000},
    {"id": "B", "predecessors": [],         "duration": 3, "crash_duration": 1, "crash_cost": 2000},
    {"id": "C", "predecessors": ["A"],      "duration": 2, "crash_duration": 1, "crash_cost": 1000},
    {"id": "D", "predecessors": ["B"],      "duration": 4, "crash_duration": 3, "crash_cost": 1000},
    {"id": "E", "predecessors": ["C"],      "duration": 4, "crash_duration": 2, "crash_cost": 1000},
    {"id": "F", "predecessors": ["C"],      "duration": 3, "crash_duration": 2, "crash_cost": 500},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5, "crash_duration": 2, "crash_cost": 2000},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2, "crash_duration": 1, "crash_cost": 3000},
]


def main() -> None:
    print("== Critical path ==")
    r = pm.cpm(ACTIVITIES)
    print(r.summary())
    print(r.table.to_string(index=False), "\n")

    print("== Schedule risk (PERT, three-point with +/- 30%) ==")
    three_point = []
    for a in ACTIVITIES:
        d = a["duration"]
        three_point.append(
            {"id": a["id"], "predecessors": a["predecessors"],
             "a": d * 0.8, "m": d, "b": d * 1.4}
        )
    r = pm.pert(three_point, n_sim=20_000, seed=0)
    for k in ("expected_duration", "mc_p50", "mc_p80", "mc_p95"):
        print(f"  {k:<20} {r.stats[k]:.2f}")
    print()

    print("== Cheapest compression to 13 periods ==")
    r = pm.crash(CRASH, target=13)
    print(f"  total crash cost: {r.stats['total_crash_cost']:.0f}")
    cuts = r.table[r.table["crash_amount"] > 1e-9][["activity", "crash_amount"]]
    print(cuts.to_string(index=False), "\n")

    print("== Earned value status at period 4 ==")
    periods = list(range(11))
    pv = [i * 10_000 for i in periods]  # linear $100k over 10 periods
    pmb = pm.plan(periods, pv)
    r = pm.evm(pmb, ev=30_000, ac=35_000, at=4)
    print(r.summary())


if __name__ == "__main__":
    main()

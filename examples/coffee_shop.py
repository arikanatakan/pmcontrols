"""End-to-end example: opening a coffee shop in New York.

Runs the whole toolkit on one project: critical path, schedule risk,
deadline crashing, a frozen budget baseline, and an earned value status
check. Run with:

    python examples/coffee_shop.py
"""

import pmcontrols as pm

# Activities for the build-out, durations in weeks.
ACTIVITIES = [
    {"id": "A", "predecessors": [],              "duration": 1},  # sign the lease
    {"id": "B", "predecessors": ["A"],           "duration": 3},  # permits
    {"id": "C", "predecessors": ["A"],           "duration": 2},  # interior design
    {"id": "D", "predecessors": ["B", "C"],      "duration": 4},  # build-out
    {"id": "E", "predecessors": ["D"],           "duration": 3},  # equipment install
    {"id": "F", "predecessors": ["D"],           "duration": 2},  # hire and train staff
    {"id": "G", "predecessors": ["C"],           "duration": 2},  # marketing
    {"id": "H", "predecessors": ["E", "F", "G"], "duration": 1},  # soft launch
]

# Same activities with crash data: fully-crashed duration and cost per week.
CRASH = [
    {"id": "A", "predecessors": [],              "duration": 1, "crash_duration": 1, "crash_cost": 0},
    {"id": "B", "predecessors": ["A"],           "duration": 3, "crash_duration": 2, "crash_cost": 4000},
    {"id": "C", "predecessors": ["A"],           "duration": 2, "crash_duration": 2, "crash_cost": 0},
    {"id": "D", "predecessors": ["B", "C"],      "duration": 4, "crash_duration": 2, "crash_cost": 5000},
    {"id": "E", "predecessors": ["D"],           "duration": 3, "crash_duration": 2, "crash_cost": 3000},
    {"id": "F", "predecessors": ["D"],           "duration": 2, "crash_duration": 1, "crash_cost": 2000},
    {"id": "G", "predecessors": ["C"],           "duration": 2, "crash_duration": 2, "crash_cost": 0},
    {"id": "H", "predecessors": ["E", "F", "G"], "duration": 1, "crash_duration": 1, "crash_cost": 0},
]


def main() -> None:
    print("== Critical path ==")
    r = pm.cpm(ACTIVITIES)
    print(f"  opens in {r.stats['project_duration']:.0f} weeks")
    print(f"  critical path: {' -> '.join(r.meta['critical_activities'])}")
    print(r.table[["activity", "es", "ef", "slack", "critical"]].to_string(index=False), "\n")

    print("== Schedule risk (PERT three-point, wide downside) ==")
    three_point = [
        {"id": a["id"], "predecessors": a["predecessors"],
         "a": round(a["duration"] * 0.8, 2), "m": a["duration"],
         "b": round(a["duration"] * 1.8, 2)}
        for a in ACTIVITIES
    ]
    rp = pm.pert(three_point, n_sim=20_000, seed=1)
    for k in ("expected_duration", "mc_p50", "mc_p80", "mc_p95"):
        print(f"  {k:<20} {rp.stats[k]:.1f} weeks")
    drivers = rp.table.sort_values("criticality_index", ascending=False)
    print("  top risk drivers (criticality index):")
    print(drivers[["activity", "criticality_index"]].head(4).round(2).to_string(index=False), "\n")

    print("== A landlord deal needs the doors open in 10 weeks ==")
    rc = pm.crash(CRASH, target=10)
    print(f"  achievable in {rc.stats['achieved_duration']:.0f} weeks "
          f"for ${rc.stats['total_crash_cost']:.0f}")
    cuts = rc.table[rc.table["crash_amount"] > 1e-9][["activity", "crash_amount", "crash_cost"]]
    print(cuts.to_string(index=False), "\n")

    print("== Freeze the budget, then check status at week 6 ==")
    periods = list(range(13))
    pv = [x * 1000 for x in (0, 5, 12, 20, 32, 50, 68, 84, 96, 106, 114, 118, 120)]
    pmb = pm.plan(periods, pv)            # commit pmb.json to version control
    r = pm.evm(pmb, ev=50_000, ac=58_000, at=6)
    print(r.summary())


if __name__ == "__main__":
    main()

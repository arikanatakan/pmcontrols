"""End-to-end example: a global automaker's new-vehicle development program.

Runs the whole toolkit on one program - critical path, schedule risk, a
launch-window crash, a frozen budget baseline and an earned-value status
check - on the kind of program every global OEM runs to bring a new model
from concept to start of production (SOP).

The work-breakdown follows the automotive industry's standard new-product
framework, APQP (Advanced Product Quality Planning, AIAG), and its phases:
plan and define, product design and development, process design and
development, product and process validation (PPAP, homologation), and
launch. Tooling is the classic long-lead item and lands on the critical
path, as it does in practice.

Real OEM program schedules are confidential, so the network structure and
gateways here are the public APQP phases, while the durations (months) and
costs (illustrative, in USD thousands per month for crashing and USD
millions for the budget) are representative of a clean-sheet vehicle
program, not any one company's internal plan. Run with:

    python examples/automotive_program.py
"""

import pmcontrols as pm

# New-vehicle program, durations in months. Precedence follows the APQP
# phase flow: define -> design -> (process and tooling in parallel with
# verification and sourcing) -> validation -> launch.
ACTIVITIES = [
    {"id": "A", "predecessors": [],              "duration": 3},   # program definition and business case
    {"id": "B", "predecessors": ["A"],           "duration": 4},   # styling and design theme freeze
    {"id": "C", "predecessors": ["B"],           "duration": 6},   # vehicle engineering and CAD release
    {"id": "D", "predecessors": ["C"],           "duration": 3},   # design-verification (DV) prototype build
    {"id": "E", "predecessors": ["D"],           "duration": 4},   # DV testing: crash, durability, NVH, emissions
    {"id": "F", "predecessors": ["C"],           "duration": 3},   # manufacturing process and plant planning
    {"id": "G", "predecessors": ["F"],           "duration": 8},   # tooling design and fabrication (long-lead)
    {"id": "H", "predecessors": ["C"],           "duration": 6},   # supplier sourcing and component PPAP
    {"id": "I", "predecessors": ["E", "G", "H"], "duration": 3},   # production-validation (PV) pilot build
    {"id": "J", "predecessors": ["I"],           "duration": 4},   # homologation and regulatory certification
    {"id": "K", "predecessors": ["J"],           "duration": 2},   # pre-series / production trial run
    {"id": "L", "predecessors": ["K"],           "duration": 3},   # start of production (SOP) ramp-up
    {"id": "M", "predecessors": ["L"],           "duration": 1},   # market launch
]

# Crash data: fully-expedited duration and the linear cost per month saved
# (USD thousands). Governance gates (A), process planning (F), the trial run
# (K) and launch (M) are treated as fixed; tooling (G) is expensive but
# decisive because it sits on the critical path.
CRASH = [
    {"id": "A", "predecessors": [],              "duration": 3, "crash_duration": 3, "crash_cost": 0},
    {"id": "B", "predecessors": ["A"],           "duration": 4, "crash_duration": 3, "crash_cost": 800},
    {"id": "C", "predecessors": ["B"],           "duration": 6, "crash_duration": 5, "crash_cost": 1500},
    {"id": "D", "predecessors": ["C"],           "duration": 3, "crash_duration": 2, "crash_cost": 600},
    {"id": "E", "predecessors": ["D"],           "duration": 4, "crash_duration": 3, "crash_cost": 1200},
    {"id": "F", "predecessors": ["C"],           "duration": 3, "crash_duration": 3, "crash_cost": 0},
    {"id": "G", "predecessors": ["F"],           "duration": 8, "crash_duration": 6, "crash_cost": 2500},
    {"id": "H", "predecessors": ["C"],           "duration": 6, "crash_duration": 5, "crash_cost": 900},
    {"id": "I", "predecessors": ["E", "G", "H"], "duration": 3, "crash_duration": 2, "crash_cost": 1000},
    {"id": "J", "predecessors": ["I"],           "duration": 4, "crash_duration": 3, "crash_cost": 700},
    {"id": "K", "predecessors": ["J"],           "duration": 2, "crash_duration": 2, "crash_cost": 0},
    {"id": "L", "predecessors": ["K"],           "duration": 3, "crash_duration": 2, "crash_cost": 1500},
    {"id": "M", "predecessors": ["L"],           "duration": 1, "crash_duration": 1, "crash_cost": 0},
]


def main() -> None:
    print("== Critical path (concept to SOP) ==")
    r = pm.cpm(ACTIVITIES)
    print(f"  program runs {r.stats['project_duration']:.0f} months")
    print(f"  critical path: {' -> '.join(r.meta['critical_activities'])}  (tooling drives it)")
    print(r.table[["activity", "es", "ef", "slack", "critical"]].to_string(index=False), "\n")

    print("== Schedule risk (PERT three-point, with the usual launch downside) ==")
    three_point = [
        {"id": a["id"], "predecessors": a["predecessors"],
         "a": round(a["duration"] * 0.9, 2), "m": a["duration"],
         "b": round(a["duration"] * 1.6, 2)}
        for a in ACTIVITIES
    ]
    rp = pm.pert(three_point, n_sim=20_000, seed=1)
    for k in ("expected_duration", "mc_p50", "mc_p80", "mc_p95"):
        print(f"  {k:<20} {rp.stats[k]:.1f} months")
    drivers = rp.table.sort_values("criticality_index", ascending=False)
    print("  top schedule-risk drivers (criticality index):")
    print(drivers[["activity", "criticality_index"]].head(4).round(2).to_string(index=False), "\n")

    print("== Marketing needs the reveal one model year early: hit 33 months ==")
    rc = pm.crash(CRASH, target=33)
    print(f"  achievable in {rc.stats['achieved_duration']:.0f} months "
          f"for ${rc.stats['total_crash_cost']:,.0f}k of expediting")
    cuts = rc.table[rc.table["crash_amount"] > 1e-9][["activity", "crash_amount", "crash_cost"]]
    print(cuts.round(2).to_string(index=False), "\n")

    print("== Freeze the $1B program budget, then check status at month 24 ==")
    periods = list(range(38))                      # months 0..37
    # Illustrative cumulative planned value ($M): a logistic spend S-curve
    # peaking through tooling and validation, ending at the $1,000M budget.
    pv = _s_curve(periods, bac=1000.0, midpoint=20.0, steepness=0.24)
    pmb = pm.plan(periods, pv)                     # commit pmb.json to version control
    pv24 = pv[24]
    ev = round(pv[22])                             # two months of earned work behind plan
    ac = round(ev / 0.94)                          # running about 6% over on cost
    # A flagship program holds tighter 0.95 control limits than the 0.90 default.
    r = pm.evm(pmb, ev=ev, ac=ac, at=24, thresholds={"cpi": 0.95, "spi_t": 0.95})
    print(f"  planned value at month 24: ${pv24:,.0f}M;  earned ${ev:,}M;  actual cost ${ac:,}M")
    print(r.summary())


def _s_curve(periods, bac, midpoint, steepness):
    """A monotonic logistic cost S-curve from 0 to bac over the periods."""
    import math

    def f(t):
        return 1.0 / (1.0 + math.exp(-steepness * (t - midpoint)))

    lo, hi = f(periods[0]), f(periods[-1])
    return [round(bac * (f(t) - lo) / (hi - lo), 1) for t in periods]


if __name__ == "__main__":
    main()

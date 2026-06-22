"""Render the automotive-program example's full chart set as one panel.

Composes every chart pmcontrols produces for the program in
examples/automotive_program.py - the Gantt schedule (full width), the activity
network, the earned-value S-curve, the Monte Carlo criticality bars and the
completion histogram - into a single figure with balanced sizes.
Run:  python docs/assets/example_automotive.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pmcontrols as pm

# Same scenario as examples/automotive_program.py (durations in months).
ACTIVITIES = [
    {"id": "A", "predecessors": [],              "duration": 3},
    {"id": "B", "predecessors": ["A"],           "duration": 4},
    {"id": "C", "predecessors": ["B"],           "duration": 6},
    {"id": "D", "predecessors": ["C"],           "duration": 3},
    {"id": "E", "predecessors": ["D"],           "duration": 4},
    {"id": "F", "predecessors": ["C"],           "duration": 3},
    {"id": "G", "predecessors": ["F"],           "duration": 8},
    {"id": "H", "predecessors": ["C"],           "duration": 6},
    {"id": "I", "predecessors": ["E", "G", "H"], "duration": 3},
    {"id": "J", "predecessors": ["I"],           "duration": 4},
    {"id": "K", "predecessors": ["J"],           "duration": 2},
    {"id": "L", "predecessors": ["K"],           "duration": 3},
    {"id": "M", "predecessors": ["L"],           "duration": 1},
]


def _s_curve(periods, bac, midpoint, steepness):
    import math

    def f(t):
        return 1.0 / (1.0 + math.exp(-steepness * (t - midpoint)))

    lo, hi = f(periods[0]), f(periods[-1])
    return [round(bac * (f(t) - lo) / (hi - lo), 1) for t in periods]


cpm = pm.cpm(ACTIVITIES)
three_point = [
    {"id": a["id"], "predecessors": a["predecessors"],
     "a": round(a["duration"] * 0.9, 2), "m": a["duration"],
     "b": round(a["duration"] * 1.6, 2)}
    for a in ACTIVITIES
]
pert = pm.pert(three_point, n_sim=20_000, seed=1, keep_samples=True)

periods = list(range(38))
pv = _s_curve(periods, bac=1000.0, midpoint=20.0, steepness=0.24)
pmb = pm.plan(periods, pv)
ev = round(pv[22])
ac = round(ev / 0.94)
evm = pm.evm(pmb, ev=ev, ac=ac, at=24, thresholds={"cpi": 0.95, "spi_t": 0.95})

fig = plt.figure(figsize=(15, 17.5))
gs = fig.add_gridspec(3, 2, height_ratios=[1.15, 1.0, 1.0])
ax_gantt = fig.add_subplot(gs[0, :])
ax_net = fig.add_subplot(gs[1, 0])
ax_evm = fig.add_subplot(gs[1, 1])
ax_crit = fig.add_subplot(gs[2, 0])
ax_mc = fig.add_subplot(gs[2, 1])

pm.gantt(cpm, ax=ax_gantt)
pm.network_diagram(cpm, ax=ax_net)
pm.evm_curve(pmb, evm, ax=ax_evm)
pm.criticality(pert, ax=ax_crit)
pm.mc_distribution(pert, ax=ax_mc)

fig.suptitle("Automotive new-vehicle program  -  examples/automotive_program.py",
             fontsize=15, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.975))
fig.savefig("docs/assets/example_automotive.png", dpi=130, bbox_inches="tight",
            facecolor="white")
print("wrote docs/assets/example_automotive.png  | duration",
      cpm.stats["project_duration"], "months")

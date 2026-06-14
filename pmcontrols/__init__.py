"""pmcontrols — project scheduling and earned value control for Python.

Validated, pandas-native, automation-first project controls.

    import pmcontrols as pm

    r = pm.cpm(activities)        # critical path, slack, float
    r = pm.pert(activities)       # three-point + Monte Carlo risk
    r = pm.crash(activities, target=14)   # cheapest compression (LP)

    # plan once, freeze, control forever:
    pm.plan(periods, pv).save("project_pmb.json")
    r = pm.evm("project_pmb.json", ev=30_000, ac=35_000, at=4)
    r.ok          # True iff CPI and SPI(t) clear thresholds
    r.summary()   # plain-language verdict
"""

from ._result import PMB, Alert, Result
from ._version import __version__
from .crash import crash
from .evm import earned_schedule, evm, plan
from .network import cpm, pert
from .plot import gantt

__all__ = [
    "cpm", "pert", "crash", "evm", "plan", "earned_schedule",
    "gantt", "Result", "Alert", "PMB", "__version__",
]

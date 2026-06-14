# pmcontrols

Project scheduling and earned value control for Python. Critical path
analysis, PERT with Monte Carlo schedule risk, minimum-cost crashing,
and earned value with Lipke's earned schedule. Every released number is
checked against published reference values on every CI run.

```
pip install pmcontrols
```

## Sixty seconds

```python
import pmcontrols as pm

activities = [
    {"id": "A", "predecessors": [],         "duration": 2},
    {"id": "B", "predecessors": [],         "duration": 3},
    {"id": "C", "predecessors": ["A"],      "duration": 2},
    {"id": "D", "predecessors": ["B"],      "duration": 4},
    {"id": "E", "predecessors": ["C"],      "duration": 4},
    {"id": "F", "predecessors": ["C"],      "duration": 3},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2},
]

r = pm.cpm(activities)
print(r.summary())
```

```text
pmcontrols cpm - 2026-06-13T00:00:00+00:00
  project_duration              15.0000
  n_activities                   8.0000
  n_critical                     5.0000
Verdict: on track - no indicator breaches thresholds.
```

The critical path is A-C-E-G-H at 15 periods, with B, D and F carrying
slack. This is the standard General Foundry result, reproduced exactly in
the validation suite.

## Plan once, freeze, control forever

```python
pm.plan(periods, pv_curve).save("pmb.json")     # commit to git
r = pm.evm("pmb.json", ev=30_000, ac=35_000, at=4)
r.ok                 # False if CPI or SPI(t) is below threshold
r.stats["ieac_t"]    # earned-schedule duration forecast
```

See the guides for the critical path, schedule risk, crashing, and
earned value, and the reference section for the full API and the
validation methodology.

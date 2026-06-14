# pmcontrols

[![CI](https://github.com/arikanatakan/pmcontrols/actions/workflows/ci.yml/badge.svg)](https://github.com/arikanatakan/pmcontrols/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pmcontrols)](https://pypi.org/project/pmcontrols/)
[![License: MIT](https://img.shields.io/github/license/arikanatakan/pmcontrols)](LICENSE)

Project scheduling and earned value control for Python.

Critical path and PERT scheduling, minimum-cost schedule compression, and
earned value management with earned schedule. Results are computed from the
standard formulations and checked against reference values in the test suite.

## Motivation

Every project office computes CPI and SPI, and almost all of it happens in
spreadsheets. R and commercial tools (Primavera, @RISK) cover schedule risk
and earned value; Python has no maintained library that a cost engineer or a
project-controls researcher can `pip install`. This is an attempt to fix
that, with a few specific goals:

* the critical path from the full forward and backward pass (ES, EF, LS, LF,
  slack), not a longest-chain guess
* PERT with a Monte Carlo completion distribution and per-activity
  criticality indices, which the analytic three-point method cannot give
* schedule crashing as optimization: the cheapest set of compressions that
  meets a deadline, solved as a linear program
* earned value with Lipke's earned schedule (ES, SPI(t), IEAC(t)), which
  plain SPI reports wrong late in a project
* an API that works headless, so a weekly cost and schedule review can run
  as a cron job

```
pip install pmcontrols
```

Documentation: https://arikanatakan.github.io/pmcontrols/

## Status

Version 0.1.0 is on PyPI. Implemented and tested:

* `cpm`: forward and backward pass returning ES, EF, LS, LF, total slack,
  and the zero-float critical path, with clear errors on cycles and unknown
  predecessors
* `pert`: three-point estimates (te = (a + 4m + b) / 6) along the critical
  path, plus a Monte Carlo simulation reporting the completion distribution
  (p50, p80, p95) and a per-activity criticality index
* `crash`: minimum-cost schedule compression to a target date, solved as the
  classical time/cost trade-off linear program (scipy, HiGHS)
* `evm`, `plan`, `earned_schedule`: cost and schedule variance, CPI and SPI,
  the estimate-at-completion family, TCPI and VAC, and Lipke's earned
  schedule (ES, SPI(t), IEAC(t)) evaluated against a frozen baseline
* `Result`: every analysis returns named statistics, a tidy table,
  structured alerts, `r.ok`, `r.summary()`, and a JSON-safe `to_dict()` with
  provenance (version, input hash, timestamp)
* `PMB`: a Performance Measurement Baseline that validates a non-decreasing
  planned-value curve and round-trips through JSON
* a reference-case validation suite (tests/validation_cases.json), with the
  General Foundry network (full schedule, critical path, and optimal crash
  costs) and hand-derived EVM and earned-schedule cases reproduced in CI
  across Python 3.10 to 3.12

## Usage

Critical path, slack, and the full schedule:

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
r.stats["project_duration"]      # 15.0
r.meta["critical_activities"]    # ['A', 'C', 'E', 'G', 'H']
r.table                          # ES/EF/LS/LF/slack per activity
```

Schedule risk from three-point estimates, with the Monte Carlo completion
distribution the analytic method cannot give:

```python
r = pm.pert([
    {"id": "X", "predecessors": [],    "a": 1, "m": 2, "b": 9},
    {"id": "Y", "predecessors": ["X"], "a": 2, "m": 3, "b": 10},
])
r.stats["mc_p80"]                # 80th-percentile completion time
r.table["criticality_index"]     # per activity, from the simulation
```

The cheapest way to hit a deadline, as a linear program rather than by hand:

```python
r = pm.crash(crash_activities, target=13)
r.stats["total_crash_cost"]      # globally optimal, not greedy
r.table["crash_amount"]          # how much to compress each activity
```

Freeze the planned value curve once, then control against it every period:

```python
import sys

pm.plan(periods, pv).save("pmb.json")   # commit this to version control

r = pm.evm("pmb.json", ev=30_000, ac=35_000, at=4)
r.ok                 # False if CPI or SPI(t) is below threshold
r.summary()          # plain text verdict
r.stats["ieac_t"]    # earned-schedule duration forecast
sys.exit(0 if r.ok else 1)
```

Every analysis returns the same `Result` object: named statistics, a tidy
table, a tuple of structured alerts, and provenance metadata (library
version, input hash, timestamp).

If you are wiring this into an AI agent, read
[Project control is not a language task](https://arikanatakan.github.io/pmcontrols/agents/)
first.

## Roadmap

| Version | Scope |
|---------|-------|
| 0.2     | published PMI/Lipke earned-schedule case-study validation; Gantt and OC plotting, kept separate from the statistics |
| 0.3     | resource leveling and constrained scheduling; schedule risk drivers (correlation, risk events); EVM from time-phased ledgers |
| 0.4     | critical chain buffers; probabilistic crashing; earned-schedule forecasting variants; JOSS paper |

Out of scope: Gantt-chart project editors (use dedicated PM tools), process
control, acceptance sampling (see [lotsampling](https://github.com/arikanatakan/lotsampling)),
general linear programming (use scipy or pyomo directly).

## License

MIT. Written and maintained by [Atakan Arikan](https://github.com/arikanatakan),
MSc Student at Tsinghua University and Politecnico di Milano.

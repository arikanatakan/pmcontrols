# pmcontrols

[![CI](https://github.com/arikanatakan/pmcontrols/actions/workflows/ci.yml/badge.svg)](https://github.com/arikanatakan/pmcontrols/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/arikanatakan/pmcontrols)](LICENSE)

Project scheduling and earned value control for Python.

CPM, PERT with Monte Carlo schedule risk, minimum-cost crashing, and
EVM/earned-schedule control — computed from the defining formulations,
never from spreadsheet conventions, and checked against published
reference values in the test suite.

Companion to [lotsampling](https://github.com/arikanatakan/lotsampling) (acceptance
sampling): lotsampling judges the lot, pmcontrols keeps the project honest.

## Motivation

Every project office computes CPI and SPI; almost all of it happens in
Excel. R and commercial tools (Primavera, Deltek, @RISK) cover schedule
risk and earned value; in Python the landscape is a 4 KB CPM toy and an
abandoned ERP add-on. There is no maintained library a cost engineer or
a project-controls researcher can `pip install` to get:

- the **critical path** with full ES/EF/LS/LF/slack accounting
- **PERT** three-point analysis plus what the textbook procedure cannot
  give you: a Monte Carlo completion distribution and per-activity
  **criticality indices**
- **crashing as optimization** — the cheapest set of compressions
  meeting a deadline, solved as the classical time/cost trade-off LP
  rather than by manual marginal-cost inspection
- **EVM with earned schedule** — the full indicator set (CV, SV, CPI,
  SPI, the EAC family, TCPI, VAC) plus Lipke's time-based ES, SPI(t)
  and duration forecast IEAC(t), which plain EVM gets wrong late in
  projects

## Quickstart

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
r.stats["project_duration"]        # 15.0
r.meta["critical_activities"]      # ['A', 'C', 'E', 'G', 'H']
r.table                            # tidy ES/EF/LS/LF/slack DataFrame

# Cheapest way to finish in 13 periods (linear program):
r = pm.crash(crash_activities, target=13)
r.stats["total_crash_cost"]        # optimal, not greedy

# Plan once, freeze, control forever:
pm.plan(periods, pv_curve).save("pmb.json")     # commit this to git
r = pm.evm("pmb.json", ev=30_000, ac=35_000, at=4)
r.ok                 # False — CPI and SPI(t) below threshold
print(r.summary())   # audit text with plain-language verdict
r.stats["ieac_t"]    # earned-schedule duration forecast
```

`r.ok` is the automation primitive: a weekly cron job can evaluate the
latest actuals against the frozen PMB and exit nonzero the moment cost
or schedule efficiency breaches a threshold.

## Validation philosophy

Every release must reproduce, in `tests/validation_cases.json` (each
case ships with its full derivation):

1. the General Foundry reference network — complete ES/EF/LS/LF/slack
   table, 15-period critical path, and optimal crash costs to 14 and 13
   periods,
2. hand-derived EVM/earned-schedule cases covering the full indicator
   set and the ES interpolation formula,
3. identity and property checks (slack = LS−ES = LF−EF; SPI(t) = ES/AT;
   crash cost monotone in target; Monte Carlo means converging to
   analytic values),
4. (before 0.1) published PMI/Lipke earned-schedule case studies,
   verified privately where copyright prevents redistribution.

## Status

0.1.0 — first public release. The API surface is small on purpose; the
`Result`/`PMB` contract is frozen and append-only from this version on.

## Roadmap

| Version | Scope |
| ------- | ----- |
| 0.2 | Published PMI/Lipke earned-schedule case-study validation; Gantt and OC plotting (separate from the statistics) |
| 0.3 | Resource leveling and constrained scheduling; schedule risk drivers (correlation, risk events); EVM from time-phased ledgers (DataFrame in, indicators out) |
| 0.4 | Critical chain buffers; probabilistic crashing (crash under uncertainty); ES forecasting variants (performance factors); JOSS paper |

Out of scope: Gantt-chart project *editors* (use dedicated PM tools),
process control, acceptance sampling (see lotsampling), generic LP modeling
(use scipy/pyomo directly).

## License

MIT. Written and maintained by [Atakan Arikan](https://github.com/arikanatakan),
MSc Student at Tsinghua University and Politecnico di Milano.

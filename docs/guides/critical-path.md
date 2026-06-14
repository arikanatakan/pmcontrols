# Critical path in Python

`pmcontrols.cpm` takes a list of activities — each with an `id`, its
`predecessors`, and a `duration` — runs the forward and backward pass, and
returns earliest/latest start and finish, total slack, and the critical
path (the activities with zero slack).

```python
import pmcontrols as pm

r = pm.cpm([
    {"id": "A", "predecessors": [],         "duration": 2},
    {"id": "B", "predecessors": [],         "duration": 3},
    {"id": "C", "predecessors": ["A"],      "duration": 2},
    {"id": "D", "predecessors": ["B"],      "duration": 4},
    {"id": "E", "predecessors": ["C"],      "duration": 4},
    {"id": "F", "predecessors": ["C"],      "duration": 3},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2},
])

r.stats["project_duration"]      # 15.0
r.meta["critical_activities"]    # ['A', 'C', 'E', 'G', 'H']
print(r.table.to_string(index=False))
```

```text
activity  duration   es   ef   ls   lf  slack  critical
       A       2.0  0.0  2.0  0.0  2.0    0.0      True
       B       3.0  0.0  3.0  1.0  4.0    1.0     False
       C       2.0  2.0  4.0  2.0  4.0    0.0      True
       D       4.0  3.0  7.0  4.0  8.0    1.0     False
       E       4.0  4.0  8.0  4.0  8.0    0.0      True
       F       3.0  4.0  7.0 10.0 13.0    6.0     False
       G       5.0  8.0 13.0  8.0 13.0    0.0      True
       H       2.0 13.0 15.0 13.0 15.0    0.0      True
```

This is the textbook General Foundry network; the critical path is
A-C-E-G-H at 15 periods, with B and D carrying one period of slack and F
carrying six. The whole schedule is reproduced to the digit in the
validation suite.

## Input

- **`predecessors`** may be a list (`["A", "B"]`) or a comma-separated
  string (`"A, B"`). An activity with no predecessors starts at time zero.
- **`duration`** is the field name by default; pass `duration="dur"` to
  read a differently named column.
- Activity ids are stringified, so integer ids work too.

## What you get back

A single `Result`:

- `r.stats` — `project_duration`, `n_activities`, `n_critical`.
- `r.table` — one row per activity with `es`, `ef`, `ls`, `lf`, `slack`,
  `critical`.
- `r.meta["critical_activities"]` — the critical path in topological order.

The identity `slack = LS − ES = LF − EF` holds for every activity and is
asserted in the test suite.

## Errors

A precedence **cycle** raises a `ValueError` that names the cycle; an
activity that lists an **unknown predecessor** raises a `ValueError`
naming both; a **negative duration** is rejected. You get a clear message
instead of a silently wrong schedule.

The forward/backward pass follows the standard activity-on-node
formulation (Render, Stair & Hanna, *Quantitative Analysis for
Management*; PMBOK).

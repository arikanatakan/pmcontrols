# Schedule crashing as a linear program

`pmcontrols.crash` finds the **cheapest** set of activity compressions that
meets a target completion time. Each activity needs a normal duration, a
fully-crashed duration, and a linear crash cost per period.

```python
import pmcontrols as pm

activities = [
    {"id": "A", "predecessors": [],         "duration": 2, "crash_duration": 1, "crash_cost": 1000},
    {"id": "B", "predecessors": [],         "duration": 3, "crash_duration": 1, "crash_cost": 2000},
    {"id": "C", "predecessors": ["A"],      "duration": 2, "crash_duration": 1, "crash_cost": 1000},
    {"id": "D", "predecessors": ["B"],      "duration": 4, "crash_duration": 3, "crash_cost": 1000},
    {"id": "E", "predecessors": ["C"],      "duration": 4, "crash_duration": 2, "crash_cost": 1000},
    {"id": "F", "predecessors": ["C"],      "duration": 3, "crash_duration": 2, "crash_cost":  500},
    {"id": "G", "predecessors": ["D", "E"], "duration": 5, "crash_duration": 2, "crash_cost": 2000},
    {"id": "H", "predecessors": ["F", "G"], "duration": 2, "crash_duration": 1, "crash_cost": 3000},
]

r = pm.crash(activities, target=13)
r.stats["total_crash_cost"]   # 3000.0 — globally optimal, not greedy
cuts = r.table[r.table["crash_amount"] > 1e-9][["activity", "crash_amount"]]
print(cuts.to_string(index=False))
```

```text
activity  crash_amount
       D           1.0
       E           2.0
```

The uncrashed network finishes in 15 periods. To reach 13 the LP compresses
E by two periods and D by one, for $3000 — cheaper than crashing the single
shared activity G, and a result manual marginal-cost crashing reaches only
after carefully tracking which paths have become critical.

## Why a linear program

Manual crashing compresses the cheapest activity on the critical path,
one period at a time, and has to stop and recheck every time a second path
becomes critical. The decision variables here are the activity start times
`s_i`, the crash amounts `y_i`, and the project finish `F`:

    minimize    Σ  c_i · y_i
    subject to  s_j ≥ s_i + (d_i − y_i)   for every precedence i → j
                F   ≥ s_i + (d_i − y_i)   for every terminal activity i
                F   ≤ target
                0 ≤ y_i ≤ d_i − crash_i,  s_i ≥ 0

This is the classical CPM time/cost trade-off (Kelley, 1961), solved with
`scipy.optimize.linprog` (HiGHS). The LP handles the appearance of second
critical paths automatically: when compressing one path makes another
bind, it compresses shared activities optimally.

## Input and output

- Field names default to `duration`, `crash_duration`, `crash_cost`; each
  is overridable.
- `r.stats` carries `normal_duration_total`, `target`, `achieved_duration`,
  `total_crash_cost`.
- `r.table` adds `normal_duration`, `crash_amount`, and `crash_cost` per
  activity to the resulting schedule.

A `target` longer than the uncrashed duration (nothing to do) or a
`crash_duration` longer than the `duration` raises a `ValueError`.

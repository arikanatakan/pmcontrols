# PERT and schedule risk

`pmcontrols.pert` takes three-point estimates — `a` optimistic, `m` most
likely, `b` pessimistic — and returns both the classical analytic result
and a Monte Carlo schedule-risk simulation in one `Result`.

```python
import pmcontrols as pm

r = pm.pert([
    {"id": "X", "predecessors": [],    "a": 1, "m": 2, "b": 9},
    {"id": "Y", "predecessors": ["X"], "a": 2, "m": 3, "b": 10},
], seed=0)

r.stats["expected_duration"]     # 7.0  — sum of te along the te-critical path
r.stats["sigma_critical_path"]   # 1.8856 — analytic standard deviation
r.stats["mc_p80"]                # 80th-percentile completion from simulation
r.table[["activity", "te", "var", "criticality_index"]]
```

## The analytic estimate

Each activity gets the classical beta approximation

    te = (a + 4m + b) / 6,    var = ((b − a) / 6)²

`expected_duration` sums `te` along the critical path of the te-network and
`sigma_critical_path` is the square root of the summed variances on that
path — the procedure in every project-management textbook (Malcolm et al.,
1959).

## Why the simulation

The analytic estimate looks only at one critical path. When a second path
is nearly as long, it can finish later than the nominal critical path on
any given run, and the analytic number **understates the risk**. The Monte
Carlo run samples every activity from a PERT-beta distribution
(α + β = 6, the classic four-sigma range), reschedules the whole network
thousands of times, and reports:

- the empirical completion distribution: `mc_mean`, `mc_p50`, `mc_p80`,
  `mc_p95`;
- the per-activity **criticality index** — the fraction of runs in which
  the activity lands on the critical path. An activity with a high
  criticality index but positive deterministic slack is exactly the risk
  the analytic method hides.

## Options

- `n_sim` (default `20000`) — number of simulation runs.
- `seed` (default `0`) — set for reproducible output; pass `None` for a
  fresh draw each call.
- `optimistic` / `most_likely` / `pessimistic` — field names, default
  `"a"`, `"m"`, `"b"`.

The estimates require `a ≤ m ≤ b` for every activity; otherwise a
`ValueError` is raised.

# API and grammar

Every analysis returns a `Result`. The contract is frozen from 0.1 on:
no public name, signature, default, or field meaning changes within
major version 0/1.

## Result

| Member | Meaning |
| ------ | ------- |
| `method` | analysis alias: `"cpm"`, `"pert"`, `"crash"`, `"evm"` |
| `params` | echo of the user's inputs |
| `stats` | named scalar outputs |
| `table` | tidy per-activity / per-indicator DataFrame |
| `alerts` | tuple of structured threshold events; empty == on track |
| `meta` | provenance: version, input hash, timestamp |
| `ok` | `True` iff no alerts |
| `summary()` | fixed-width audit text |
| `to_dict()` | JSON-safe, integer-versioned schema |

## Functions

- `cpm(activities, duration="duration")`
- `pert(activities, optimistic="a", most_likely="m", pessimistic="b", n_sim=20000, seed=0)`
- `crash(activities, target, duration="duration", crash_duration="crash_duration", cost_per_period="crash_cost")`
- `plan(periods, pv) -> PMB`
- `evm(pmb, ev, ac, at, thresholds=None)`
- `earned_schedule(pmb, ev) -> float`
- `gantt(result, ax=None, show_slack=True, title=None) -> (figure, axes)` (needs the `plot` extra)

## PMB

`plan(...)` returns a `PMB` (Performance Measurement Baseline) with
`.save(path)`, `.load(path)`, `.to_json()` / `.from_json()`, and a
`planned_duration` property. It validates that planned value is
non-decreasing and ends at BAC.

# Charts

pmcontrols turns its results into the standard project-control charts. The
plots are optional: the validated statistics stay dependency-free, and the
plotting code lives behind the `plot` extra.

```
pip install "pmcontrols[plot]"
```

Every chart function returns the matplotlib `(figure, axes)`, so you can
restyle it, drop it onto an existing axis, embed it in a report, or save it
in any format matplotlib supports. The numbers come straight from the
results, so a chart always matches the validated output.

## Gantt chart

```python
import pmcontrols as pm

r = pm.cpm(activities)
fig, ax = pm.gantt(r)
fig.savefig("schedule.png", dpi=150)
```

Each activity is a bar from its earliest start to its earliest finish.
**Critical** activities (zero total float) are red, the rest blue, and the
light grey bar behind a non-critical activity is its **total float**. A
zero-duration activity is drawn as a diamond (a milestone). Works on a `cpm`
or `crash` result.

## Network diagram

```python
fig, ax = pm.network_diagram(pm.cpm(activities))
```

An activity-on-node view: nodes are activities (placed by earliest start),
arrows are precedence, and the critical path is red. It reads the precedence
straight from the result's provenance, so a `cpm` or `crash` result is all it
needs.

## Earned value S-curve

```python
pmb = pm.plan(periods, pv)
r = pm.evm(pmb, ev=30_000, ac=35_000, at=4)
fig, ax = pm.evm_curve(pmb, r)
```

The classic earned-value chart: the planned-value curve, the earned value and
actual cost at the status date, the budget at completion, and the
earned-schedule forecast running from the current earned value to the
forecast completion (IEAC).

## Criticality and the completion distribution

These read a `pert` result. The criticality bars need only the standard
result; the histogram needs the Monte Carlo sample, so run `pert` with
`keep_samples=True`.

```python
r = pm.pert(activities, keep_samples=True)
pm.criticality(r)        # per-activity share of runs on the critical path
pm.mc_distribution(r)    # histogram of completion times with p50/p80/p95
```

`criticality` highlights the activities that drive schedule risk, including
near-critical ones a deterministic critical path hides. `mc_distribution`
shows the spread of completion times with the key percentiles marked.

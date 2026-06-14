# Gantt charts

`pmcontrols.gantt` turns a `cpm` or `crash` result into a Gantt chart. It is
an optional feature: the validated statistics stay dependency-free, and the
plotting code lives behind the `plot` extra.

```
pip install "pmcontrols[plot]"
```

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

fig, ax = pm.gantt(r)
fig.savefig("schedule.png", dpi=150)
```

## How to read it

* Each activity is a bar from its earliest start to its earliest finish, so
  the bar length is the activity's duration.
* **Critical** activities (zero total float) are drawn in red; the rest in
  blue. A delay on a red activity delays the whole project.
* The light grey bar behind a non-critical activity is its **total float**:
  how far it can slip, from its earliest to its latest finish, without moving
  the finish date.
* A zero-duration activity is drawn as a diamond (a milestone).

The chart reads the schedule straight from the result, so it always matches
the validated `cpm`/`crash` numbers.

## Options

* `ax`: draw onto an existing matplotlib Axes instead of a new figure.
* `show_slack`: set to `False` to hide the total-float bars.
* `title`: override the default title.

`gantt` returns the matplotlib `(figure, axes)`, so you can restyle, embed in
a report, or save in any format matplotlib supports.

# Changelog

All notable changes are recorded here. The public API on the
[grammar page](https://arikanatakan.github.io/pmcontrols/reference/api/) is
frozen from 0.1.0 on: no public name, signature, default value, or field
meaning will be removed or change meaning within major version 0/1.

## Unreleased

### Added

- Example `examples/automotive_program.py`: an end-to-end run of the whole
  toolkit (critical path, PERT schedule risk, a launch-window crash, and an
  earned-value status check with custom control limits) on a global automaker's
  new-vehicle development program. The work-breakdown follows the automotive
  APQP phases (durations and costs are illustrative, not a company's internal
  plan).

## 0.2.1

### Added

* Visualization suite (optional `plot` extra, matplotlib): `evm_curve` (earned
  value S-curve), `network_diagram` (activity-on-node graph with the critical
  path), `criticality` (Monte Carlo criticality bars), and `mc_distribution`
  (PERT completion histogram), alongside the existing `gantt`.
* `pert(..., keep_samples=True)` stores a capped Monte Carlo completion sample
  (`meta["mc_finish_sample"]`) for the histogram.
* `cpm` and `crash` results now carry `meta["predecessors"]`, so the network
  diagram can be drawn from the result alone.

## 0.2.0

### Added

* `gantt(result)`: an optional Gantt chart of a `cpm` or `crash` schedule,
  with the critical path highlighted and total float shown. Requires the
  `plot` extra (`pip install "pmcontrols[plot]"`, matplotlib); the validated
  statistics stay dependency-free and headless.

## 0.1.0

First public release.

### Added

* `cpm`: critical path analysis of a deterministic activity-on-node
  network - topological forward/backward pass returning ES/EF/LS/LF, total
  slack, and the zero-float critical path. Precedence cycles and unknown
  predecessors raise clear errors.
* `pert`: three-point analysis with the classical beta approximation
  (te = (a + 4m + b)/6, var = ((b - a)/6)^2) along the te-critical path,
  plus a Monte Carlo schedule-risk simulation reporting the empirical
  completion distribution (p50/p80/p95) and the per-activity **criticality
  index** that the analytic procedure cannot give.
* `crash`: minimum-cost schedule compression solved as the classical CPM
  time/cost trade-off linear program (`scipy.optimize.linprog`, HiGHS),
  returning the globally optimal crash amounts, the resulting schedule, and
  the total crash cost.
* `evm` and `plan`: earned value management against a frozen Performance
  Measurement Baseline - CV, SV, CPI, SPI, the estimate-at-completion
  family (BAC/CPI, AC + (BAC - EV), and the CPI*SPI blend), ETC, TCPI, VAC.
* `earned_schedule` and the EVM earned-schedule block: Lipke's ES by linear
  interpolation on the baseline curve, SV(t), SPI(t) = ES/AT, and the
  duration forecast IEAC(t) = PD/SPI(t).
* `Result`: the single object every analysis returns - `stats`, tidy
  `table`, structured `alerts`, `meta` provenance (version, input hash,
  timestamp), `ok`, `summary()`, and a JSON-safe, integer-versioned
  `to_dict()`.
* `PMB`: a Performance Measurement Baseline that validates a non-decreasing
  planned-value curve ending at BAC, with `save`/`load` and
  `to_json`/`from_json`.
* Validation suite driven by `tests/validation_cases.json`, each case
  shipped with its full derivation: the General Foundry reference network
  (complete schedule, 15-period critical path A-C-E-G-H, optimal crash
  costs to 14 and 13 periods) and hand-derived EVM/earned-schedule cases,
  reproduced in CI across Python 3.10-3.12.

### Compatibility

* From this version on the `Result` and `PMB` schemas are append-only:
  fields may be added, never removed or repurposed within major version
  0/1.

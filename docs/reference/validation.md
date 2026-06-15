# Validation

Every released number is reproduced in `tests/validation_cases.json`,
where each case ships with its full derivation, on every CI run across
Python 3.10-3.12.

## Layers

1. **Reference network.** The General Foundry example - complete
   ES/EF/LS/LF/slack table, the 15-period critical path A-C-E-G-H, and
   optimal crash costs to 14 and 13 periods.
2. **Hand-derived EVM/ES.** The full indicator set and the earned
   schedule interpolation formula, derived from first principles with
   published values.
3. **Identities and properties.** slack = LS-ES = LF-EF; SPI(t) = ES/AT;
   crash cost monotone in target; Monte Carlo means converging to the
   analytic mean.
4. **Roadmap (before 0.1).** Published PMI/Lipke earned-schedule case
   studies, verified privately where copyright prevents redistribution.

## Why compute from formulations, not conventions

Spreadsheet EVM templates bake in shortcuts (linear PV interpolation,
period-end snapshots) that diverge from the underlying definitions.
pmcontrols computes from the definitions - interpolating the PV curve for
PV(t), solving the time/cost trade-off as an LP rather than by marginal
inspection - so results are reproducible and auditable.

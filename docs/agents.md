# Project control is not a language task

*For people building agents that touch schedules and budgets.*

Ask an agent how the project is doing and it will, with great confidence,
write something like this:

```python
spi = ev / pv
forecast_finish = planned_duration / spi
```

It runs. It returns a number. It is wrong in a way that gets worse exactly
when you need it.

Plain SPI = EV/PV is built on cost-denominated value, not time, and it
drifts back to 1.0 as a late project finishes: at completion EV = PV = BAC,
so SPI = 1.0 and the indicator reports "on schedule" for a project that
delivered three months late. Lipke's earned schedule works in the time
dimension instead and keeps reporting the slip. The naive forecast above
inherits the same blindness and quietly heals itself toward the baseline.

No exception. No warning. Just a confident number that happens to be
fiction at the worst moment.

## The failure mode is confidence

When a human computes a backward pass by hand, the work gets written once,
and a colleague has a chance to catch the slip. An agent writes it fresh,
thousands of times a day, and throws it away after answering. Nobody
reviews arithmetic that lives for four seconds.

A crash would be merciful. Generated project metrics fail by being
believed and pasted into a status deck.

## Three classics

**The eyeballed critical path.** Asked for the critical path, a model sums
the longest-looking chain of activities and stops. The critical path is
not the longest chain you can see; it is the set of activities with zero
total float, which only falls out of a full forward *and* backward pass.
Skip the backward pass and parallel near-critical paths vanish from the
report — the ones most likely to actually slip.

**SPI that heals itself.** EV/PV returns to 1.0 at completion no matter how
late the finish. Reported alone, it is an indicator that goes blind right
when the project is ending. Earned schedule — SPI(t) = ES/AT — does not.

**The naked EAC.** "EAC = 1.18M, forecast finish month 11," case closed.
Which EAC? BAC/CPI, AC + (BAC − EV), or the CPI×SPI blend? They disagree by
hundreds of thousands of dollars on the same inputs, and the right one
depends on whether the cost variance is structural or one-off. Quoting a
single number without the method changes the claim, quietly.

## None of this is hard. All of it is exact.

A topological forward and backward pass. Earned schedule by linear
interpolation on the baseline curve, exactly as Lipke published it. The
estimate-at-completion family, each member named. Crashing solved as the
classical time/cost trade-off LP instead of by marginal-cost guesswork.
Twenty freshly generated lines do not reliably contain any of that. And
there is a simple test: the code either reproduces the General Foundry
schedule and the hand-derived earned-value cases, to the digit, or it does
not. There is no third state.

## The division of labor

Keep agents on the project narrative. Keep them off the arithmetic.

> **The agent interprets. Validated code calculates.**

Models are genuinely good at figuring out what was asked, picking the right
analysis, and explaining a verdict in plain words. They are not
calculators. And project control is a field where almost right and right
look identical until the variance report.

## What an accountable number looks like

```json
{
  "schema": 1, "method": "evm",
  "stats": {"cpi": 0.857, "spi_t": 0.75, "ieac_t": 13.33, "...": "..."},
  "alerts": [{"indicator": "spi_t", "value": 0.75, "threshold": 0.9}],
  "meta": {"version": "0.1.0", "input_hash": "sha256:9f2c...",
           "computed_at": "2026-06-15T09:14:02+00:00"}
}
```

Library version, input hash, timestamp, named indicators, structured
alerts. Six months from now, when someone asks where that forecast came
from, this is the difference between an answer and a shrug.

A number you cannot recompute is an opinion.

## The practical part

This is why pmcontrols is built the way it is. `pm.cpm`, `pm.pert`,
`pm.crash` and `pm.evm` each return one structured `Result` with full
provenance, and `r.ok` collapses it to a pass/fail gate the agent can act
on. The agent never touches a formula. Every released number is
re-derived against published reference values on every CI run.

Use it, or use something else that is validated. The principle outranks the
package.

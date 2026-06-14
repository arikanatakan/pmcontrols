# EVM control as a cron job

Every pmcontrols `Result` exposes `r.ok`, which is `True` only when no
indicator breaches its threshold. That one boolean turns earned value
control from a status report into an automatable gate.

```python
import sys
import pmcontrols as pm

r = pm.evm("pmb.json", ev=current_ev, ac=current_ac, at=current_period)
print(r.summary())
sys.exit(0 if r.ok else 1)
```

A weekly job reads the latest actuals, evaluates them against the frozen
PMB, prints a plain-language verdict, and exits nonzero the moment CPI or
SPI(t) drops below the threshold. Anything that watches process exit codes
(cron with `MAILTO`, a CI step, a systemd timer, an agent) now alerts on
schedule and cost the same way a failing test alerts on code.

```text
pmcontrols evm - 2026-06-15T09:14:02+00:00
  cpi                            0.8571
  spi_t                          0.7500
  ieac_t                        13.3333
Alerts:
  ! cpi=0.857 breaches 0.9 - below threshold
  ! spi_t=0.750 breaches 0.9 - below threshold
Verdict: ATTENTION - indicators breach thresholds.
```

## Thresholds

The defaults flag CPI or SPI(t) below 0.90. Override per run:

```python
r = pm.evm("pmb.json", ev=ev, ac=ac, at=at,
           thresholds={"cpi": 0.95, "spi_t": 0.95})
```

Any indicator name in `r.stats` can be a threshold key, and the alert fires
when the value falls below it. `r.alerts` is a tuple of structured `Alert`
records (`indicator`, `value`, `threshold`, `note`), so a downstream system
can route them rather than parse text.

## Why this is safe to automate

The PMB is frozen and committed, so the baseline a job compares against is
the same one signed off at planning time. Limits do not drift because
someone recomputed them on this week's data. And `r.to_dict()` gives a
JSON-safe, versioned payload with the library version, an input hash, and a
timestamp, so every alert is reproducible six months later.

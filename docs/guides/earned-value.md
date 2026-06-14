# Earned value and earned schedule

Freeze the time-phased planned value curve as a Performance Measurement
Baseline (PMB), commit it to version control, and evaluate each reporting
period against it.

```python
import pmcontrols as pm

periods = list(range(11))
pv = [i * 10_000 for i in periods]      # linear $100k over 10 periods

pm.plan(periods, pv).save("pmb.json")   # freeze once; commit to git

r = pm.evm("pmb.json", ev=30_000, ac=35_000, at=4)
print(r.summary())
```

`r.stats` carries the full indicator set.

| Indicator | Meaning |
| --------- | ------- |
| `cv`, `sv` | cost and schedule variance (EV − AC, EV − PV) |
| `cpi`, `spi` | cost and schedule performance index (EV/AC, EV/PV) |
| `eac_cpi` | estimate at completion, BAC / CPI |
| `eac_typical` | AC + (BAC − EV), remaining work at planned efficiency |
| `eac_cpi_spi` | the CPI×SPI blended forecast |
| `etc`, `vac` | estimate to complete, variance at completion |
| `tcpi_bac` | to-complete performance index against BAC |

## The earned-schedule block

Plain SPI = EV/PV is known to drift back to 1.0 as a late project finishes:
at completion EV = PV = BAC, so SPI = 1.0 even on a project that delivered
months late. Lipke's **earned schedule** (Lipke, 2003) fixes this by
working in the time dimension:

- **ES** — the time at which the plan had earned what you have now earned,
  by linear interpolation on the cumulative PV curve.
- **SV(t) = ES − AT**, **SPI(t) = ES / AT** — a schedule index that keeps
  reporting slippage all the way to the finish.
- **IEAC(t) = PD / SPI(t)** — a forecast of the total project *duration*.

```python
r.stats["es"]        # earned schedule, in PMB time units
r.stats["spi_t"]     # ES / AT
r.stats["ieac_t"]    # forecast completion duration
```

## The PMB

`pm.plan(periods, pv)` returns a `PMB` that validates the planned-value
curve is non-decreasing and ends at BAC. It round-trips through JSON
(`save`/`load`, `to_json`/`from_json`) so the baseline is a committed,
auditable artifact rather than a cell in a spreadsheet. `pm.evm` accepts
either a `PMB` object or a path to a saved one.

EV above BAC, or negative EV/AC, raises a `ValueError`. The definitions
follow PMBOK / EIA-748 practice for the cost indicators and Lipke (2003)
for earned schedule.

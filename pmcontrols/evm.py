"""Earned value management and earned schedule.

Cost indicators follow the standard EVM formulation (PMBOK; EIA-748
practice): CV = EV - AC, SV = EV - PV, CPI = EV/AC, SPI = EV/PV, with
the classical estimate-at-completion family and TCPI.

Time indicators follow Lipke's earned schedule: ES(t) is the time at
which the planned value curve equals current EV (linear interpolation
between baseline periods), SV(t) = ES - AT, SPI(t) = ES / AT, and the
duration forecast IEAC(t) = PD / SPI(t).
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from ._result import PMB, Alert, Result, data_hash, utcnow
from ._version import __version__

__all__ = ["evm", "plan", "earned_schedule"]


def plan(periods: Sequence[float], pv: Sequence[float]) -> PMB:
    """Freeze a time-phased planned value curve into a PMB."""
    return PMB(
        periods=tuple(float(x) for x in periods),
        pv=tuple(float(x) for x in pv),
        bac=float(pv[-1]),
        created_at=utcnow(),
        version=__version__,
    )


def earned_schedule(pmb: PMB, ev: float) -> float:
    """Earned schedule ES(t): when the plan earned what we have earned.

    Linear interpolation on the cumulative PV curve (Lipke 2003):
    ES = t_N + (EV - PV_N) / (PV_{N+1} - PV_N) * (t_{N+1} - t_N),
    where N is the last baseline period with PV_N <= EV.
    """
    t = np.asarray(pmb.periods, dtype=float)
    pv = np.asarray(pmb.pv, dtype=float)
    if ev <= pv[0]:
        return float(t[0])
    if ev >= pv[-1]:
        return float(t[-1])
    n = int(np.searchsorted(pv, ev, side="right") - 1)
    if pv[n + 1] == pv[n]:
        return float(t[n + 1])
    return float(t[n] + (ev - pv[n]) / (pv[n + 1] - pv[n]) * (t[n + 1] - t[n]))


def evm(
    pmb: PMB | str,
    ev: float,
    ac: float,
    at: float,
    thresholds: Mapping[str, float] | None = None,
) -> Result:
    """Evaluate project status at actual time ``at`` against a frozen PMB.

    Parameters
    ----------
    pmb : a PMB object or a path to a saved PMB JSON.
    ev : cumulative earned value at ``at``.
    ac : cumulative actual cost at ``at``.
    at : actual time, in the PMB's time units.
    thresholds : alert thresholds; defaults to CPI and SPI(t) below 0.90.

    Returns a Result whose stats include the full indicator set:
    PV, CV, SV, CPI, SPI, the EAC family, ETC, TCPI, VAC, and the
    earned-schedule block ES, SV(t), SPI(t), IEAC(t).
    """
    if isinstance(pmb, str):
        pmb = PMB.load(pmb)
    if ev < 0 or ac < 0:
        raise ValueError("EV and AC must be non-negative")
    if ev > pmb.bac * (1 + 1e-9):
        raise ValueError("EV cannot exceed BAC")
    t = np.asarray(pmb.periods, dtype=float)
    pv_curve = np.asarray(pmb.pv, dtype=float)
    pv = float(np.interp(at, t, pv_curve))
    bac, pd_ = pmb.bac, pmb.planned_duration

    cv, sv = ev - ac, ev - pv
    cpi = ev / ac if ac > 0 else np.nan
    spi = ev / pv if pv > 0 else np.nan
    eac_cpi = bac / cpi if cpi and not np.isnan(cpi) and cpi > 0 else np.nan
    eac_typical = ac + (bac - ev)  # remaining work at planned efficiency
    spi_for_blend = spi if spi and not np.isnan(spi) and spi > 0 else np.nan
    eac_blend = (
        ac + (bac - ev) / (cpi * spi_for_blend)
        if cpi and spi_for_blend and cpi > 0
        else np.nan
    )
    etc = eac_cpi - ac if not np.isnan(eac_cpi) else np.nan
    tcpi_bac = (bac - ev) / (bac - ac) if bac > ac else np.inf
    vac = bac - eac_cpi if not np.isnan(eac_cpi) else np.nan

    es = earned_schedule(pmb, ev)
    sv_t = es - at
    spi_t = es / at if at > 0 else np.nan
    ieac_t = pd_ / spi_t if spi_t and not np.isnan(spi_t) and spi_t > 0 else np.nan

    stats = {
        "bac": bac, "planned_duration": pd_, "at": at,
        "pv": pv, "ev": ev, "ac": ac,
        "cv": cv, "sv": sv, "cpi": cpi, "spi": spi,
        "eac_cpi": eac_cpi, "eac_typical": eac_typical, "eac_cpi_spi": eac_blend,
        "etc": etc, "tcpi_bac": tcpi_bac, "vac": vac,
        "es": es, "sv_t": sv_t, "spi_t": spi_t, "ieac_t": ieac_t,
        "pct_complete": ev / bac, "pct_spent": ac / bac,
    }

    thr = {"cpi": 0.90, "spi_t": 0.90, **(thresholds or {})}
    alerts = tuple(
        Alert(indicator=k, value=float(stats[k]), threshold=float(v),
              note="below threshold")
        for k, v in thr.items()
        if k in stats and not np.isnan(stats[k]) and stats[k] < v
    )

    table = pd.DataFrame(
        {"indicator": list(stats), "value": [stats[k] for k in stats]}
    )
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({"ev": ev, "ac": ac, "at": at, "pv": list(pmb.pv)}),
        "pmb_created_at": pmb.created_at,
    }
    return Result(method="evm", params={"ev": ev, "ac": ac, "at": at},
                  stats=stats, table=table, alerts=alerts, meta=meta)

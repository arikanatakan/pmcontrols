"""Minimum-cost schedule compression (crashing) as a linear program.

Decision variables are activity start times s_i, crash amounts y_i and
the project finish time F:

    minimize    sum_i  c_i * y_i
    subject to  s_j >= s_i + (d_i - y_i)      for every precedence i -> j
                F   >= s_i + (d_i - y_i)      for every terminal activity i
                F   <= T_target
                0 <= y_i <= d_i - crash_i,    s_i >= 0

This is the classical CPM time/cost trade-off LP (Kelley 1961), solved
with scipy.optimize.linprog (HiGHS).
"""

from __future__ import annotations

from typing import Iterable, Mapping

import numpy as np
from scipy.optimize import linprog

from ._result import Result, data_hash, utcnow
from ._version import __version__
from .network import _normalize, _passes

__all__ = ["crash"]


def crash(
    activities: Iterable[Mapping[str, object]],
    target: float,
    duration: str = "duration",
    crash_duration: str = "crash_duration",
    cost_per_period: str = "crash_cost",
) -> Result:
    """Cheapest set of crash decisions meeting a target completion time.

    Each activity mapping must carry: ``id``, ``predecessors``, a normal
    duration, a fully-crashed duration, and a (linear) crash cost per
    period.  Returns the optimal crash amount per activity, the resulting
    schedule, and the total crash cost.
    """
    acts = _normalize(activities)
    names = list(acts)
    idx = {a: i for i, a in enumerate(names)}
    n = len(names)
    d = np.array([float(acts[a][duration]) for a in names])
    dc = np.array([float(acts[a][crash_duration]) for a in names])
    cost = np.array([float(acts[a][cost_per_period]) for a in names])
    if np.any(dc > d):
        raise ValueError("crash duration cannot exceed normal duration")
    if np.any(cost < 0):
        raise ValueError("crash costs must be non-negative")

    normal = _passes(acts, {a: float(acts[a][duration]) for a in names})
    normal_finish = float(normal["ef"].max())
    if target > normal_finish:
        raise ValueError(
            f"target {target} exceeds the uncrashed duration {normal_finish}; "
            "nothing to crash"
        )

    # Variables: [s_0..s_{n-1}, F, y_0..y_{n-1}]
    nv = 2 * n + 1
    c = np.zeros(nv)
    c[n + 1:] = cost

    A_ub, b_ub = [], []
    succs: dict[str, list[str]] = {a: [] for a in acts}
    for a in acts:
        for p in acts[a]["preds"]:
            succs[p].append(a)
    # Precedence: s_i + d_i - y_i - s_j <= 0
    for a in names:
        for s in succs[a]:
            row = np.zeros(nv)
            row[idx[a]] = 1.0
            row[idx[s]] = -1.0
            row[n + 1 + idx[a]] = -1.0
            A_ub.append(row)
            b_ub.append(-d[idx[a]])
    # Terminal: s_i + d_i - y_i - F <= 0
    for a in names:
        if not succs[a]:
            row = np.zeros(nv)
            row[idx[a]] = 1.0
            row[n] = -1.0
            row[n + 1 + idx[a]] = -1.0
            A_ub.append(row)
            b_ub.append(-d[idx[a]])

    bounds = [(0, None)] * n + [(0, target)] + [
        (0, float(d[i] - dc[i])) for i in range(n)
    ]
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds,
                  method="highs")
    if not res.success:
        raise RuntimeError(f"crashing LP infeasible or failed: {res.message}")

    y = res.x[n + 1:]
    new_dur = {a: float(d[idx[a]] - y[idx[a]]) for a in names}
    sched = _passes(acts, new_dur)
    sched["normal_duration"] = sched["activity"].map(
        {a: float(d[idx[a]]) for a in names}
    )
    sched["crash_amount"] = sched["activity"].map(
        {a: float(y[idx[a]]) for a in names}
    )
    sched["crash_cost"] = sched["activity"].map(
        {a: float(y[idx[a]] * cost[idx[a]]) for a in names}
    )

    stats = {
        "normal_duration_total": normal_finish,
        "target": float(target),
        "achieved_duration": float(sched["ef"].max()),
        "total_crash_cost": float(res.fun),
    }
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({a: [float(d[idx[a]]), float(dc[idx[a]]),
                                     float(cost[idx[a]])] for a in names}),
        "solver": "scipy.linprog/highs",
        "predecessors": {a: list(acts[a]["preds"]) for a in names},
    }
    return Result(method="crash", params={"target": target}, stats=stats,
                  table=sched, meta=meta)

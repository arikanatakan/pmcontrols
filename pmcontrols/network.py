"""Project networks: CPM and PERT.

Activity-on-node networks built from plain records
(id, duration, predecessors). The forward/backward pass follows the
standard formulation (e.g. Render, Stair & Hanna; PMBOK):

    EF = ES + t           ES = max EF of immediate predecessors
    LS = LF - t           LF = min LS of immediate successors
    slack = LS - ES = LF - EF
"""

from __future__ import annotations

from graphlib import CycleError, TopologicalSorter
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

from ._result import Result, utcnow, data_hash
from ._version import __version__

__all__ = ["cpm", "pert"]

Activity = Mapping[str, object]


def _normalize(activities: Iterable[Activity]) -> dict[str, dict]:
    acts: dict[str, dict] = {}
    for a in activities:
        aid = str(a["id"])
        if aid in acts:
            raise ValueError(f"duplicate activity id: {aid}")
        preds_raw = a.get("predecessors", a.get("pred", ())) or ()
        if isinstance(preds_raw, str):
            preds: tuple[str, ...] = tuple(
                p.strip() for p in preds_raw.split(",") if p.strip()
            )
        else:
            preds = tuple(str(p) for p in preds_raw)  # type: ignore[attr-defined]
        acts[aid] = {"preds": preds, **{
            k: v for k, v in a.items() if k not in ("id", "predecessors", "pred")
        }}
    for aid, a in acts.items():
        for p in a["preds"]:
            if p not in acts:
                raise ValueError(f"activity {aid} references unknown predecessor {p!r}")
    return acts


def _topo_order(acts: dict[str, dict]) -> list[str]:
    """Topological order, raising a clear error on precedence cycles."""
    try:
        return list(
            TopologicalSorter({k: v["preds"] for k, v in acts.items()}).static_order()
        )
    except CycleError as exc:  # graphlib's message is opaque to end users
        cycle = " -> ".join(map(str, exc.args[1])) if len(exc.args) > 1 else "?"
        raise ValueError(f"precedence cycle in the activity network: {cycle}") from None


def _passes(acts: dict[str, dict], dur: Mapping[str, float]) -> pd.DataFrame:
    order = _topo_order(acts)
    es: dict[str, float] = {}
    ef: dict[str, float] = {}
    for a in order:
        es[a] = max((ef[p] for p in acts[a]["preds"]), default=0.0)
        ef[a] = es[a] + dur[a]
    finish = max(ef.values())
    succs: dict[str, list[str]] = {a: [] for a in acts}
    for a in acts:
        for p in acts[a]["preds"]:
            succs[p].append(a)
    lf: dict[str, float] = {}
    ls: dict[str, float] = {}
    for a in reversed(order):
        lf[a] = min((ls[s] for s in succs[a]), default=finish)
        ls[a] = lf[a] - dur[a]
    rows = []
    for a in order:
        slack = ls[a] - es[a]
        rows.append(
            {
                "activity": a,
                "duration": dur[a],
                "es": es[a],
                "ef": ef[a],
                "ls": ls[a],
                "lf": lf[a],
                "slack": slack,
                "critical": bool(abs(slack) < 1e-9),
            }
        )
    return pd.DataFrame(rows)


def cpm(activities: Iterable[Activity], duration: str = "duration") -> Result:
    """Critical path analysis of a deterministic activity network.

    Parameters
    ----------
    activities : iterable of mappings with keys ``id``, ``predecessors``
        (list or comma-separated string; empty for start activities) and a
        duration field.
    duration : name of the duration field (default ``"duration"``).
    """
    acts = _normalize(activities)
    dur = {a: float(v[duration]) for a, v in acts.items()}
    if any(d < 0 for d in dur.values()):
        raise ValueError("durations must be non-negative")
    table = _passes(acts, dur)
    crit = table.loc[table["critical"], "activity"].tolist()
    stats = {
        "project_duration": float(table["ef"].max()),
        "n_activities": float(len(table)),
        "n_critical": float(len(crit)),
    }
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({a: dur[a] for a in sorted(dur)}),
        "critical_activities": crit,
    }
    return Result(method="cpm", params={"duration": duration},
                  stats=stats, table=table, meta=meta)


def pert(
    activities: Iterable[Activity],
    optimistic: str = "a",
    most_likely: str = "m",
    pessimistic: str = "b",
    n_sim: int = 20_000,
    seed: int | None = 0,
) -> Result:
    """PERT three-point analysis with Monte Carlo schedule risk.

    Expected time and variance per activity follow the classical beta
    approximation te = (a + 4m + b) / 6, var = ((b - a) / 6)^2.  The
    analytic project estimate sums te and var along the te-critical path
    (the textbook procedure); the Monte Carlo simulation samples each
    activity from the PERT-beta distribution and reports the empirical
    completion distribution and per-activity criticality indices, which
    the analytic procedure cannot provide.
    """
    acts = _normalize(activities)
    te, var, lo, hi = {}, {}, {}, {}
    for k, v in acts.items():
        a, m, b = float(v[optimistic]), float(v[most_likely]), float(v[pessimistic])
        if not a <= m <= b:
            raise ValueError(f"activity {k}: require a <= m <= b")
        te[k] = (a + 4 * m + b) / 6.0
        var[k] = ((b - a) / 6.0) ** 2
        lo[k], hi[k] = a, b
    base = _passes(acts, te)
    base["te"] = base["activity"].map(te)
    base["var"] = base["activity"].map(var)
    crit = base.loc[base["critical"], "activity"].tolist()
    mean = float(base["ef"].max())
    sigma = float(np.sqrt(sum(var[c] for c in crit)))

    rng = np.random.default_rng(seed)
    names = list(acts)
    samples = {}
    for k in names:
        a, b = lo[k], hi[k]
        if b - a < 1e-12:
            samples[k] = np.full(n_sim, a)
            continue
        # PERT-beta with alpha + beta = 6 (the classic four-sigma range).
        alpha = 1.0 + 4.0 * (float(acts[k][most_likely]) - a) / (b - a)
        beta = 6.0 - alpha
        samples[k] = a + (b - a) * rng.beta(alpha, beta, n_sim)

    order = _topo_order(acts)
    ef_sim = {k: np.zeros(n_sim) for k in names}
    for k in order:
        preds = acts[k]["preds"]
        es_k = np.maximum.reduce([ef_sim[p] for p in preds]) if preds else np.zeros(n_sim)
        ef_sim[k] = es_k + samples[k]
    finish = np.maximum.reduce([ef_sim[k] for k in names])

    # Per-activity criticality index: share of simulation runs in which the
    # activity lies on the critical path (zero slack) under sampled durations.
    succs: dict[str, list[str]] = {name: [] for name in acts}
    for name in acts:
        for pred in acts[name]["preds"]:
            succs[pred].append(name)
    ls_sim: dict[str, np.ndarray] = {}
    lf_sim: dict[str, np.ndarray] = {}
    crit_idx: dict[str, float] = {}
    for k in reversed(order):
        lf_sim[k] = (
            np.minimum.reduce([ls_sim[s] for s in succs[k]]) if succs[k] else finish
        )
        es_k = (
            np.maximum.reduce([ef_sim[p] for p in acts[k]["preds"]])
            if acts[k]["preds"]
            else np.zeros(n_sim)
        )
        ls_sim[k] = lf_sim[k] - samples[k]
        crit_idx[k] = float(np.mean(np.abs(ls_sim[k] - es_k) < 1e-9))
    base["criticality_index"] = base["activity"].map(crit_idx)

    stats = {
        "expected_duration": mean,
        "sigma_critical_path": sigma,
        "mc_mean": float(np.mean(finish)),
        "mc_p50": float(np.percentile(finish, 50)),
        "mc_p80": float(np.percentile(finish, 80)),
        "mc_p95": float(np.percentile(finish, 95)),
    }
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "n_sim": n_sim,
        "seed": seed,
        "critical_activities": crit,
        "mc_finish_quantiles": {
            str(q): float(np.percentile(finish, q)) for q in (5, 25, 50, 75, 95)
        },
    }
    return Result(method="pert", params={"n_sim": n_sim}, stats=stats,
                  table=base, meta=meta)

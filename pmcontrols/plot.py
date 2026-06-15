"""Gantt plotting, kept separate from the validated statistics.

This module is optional: it needs matplotlib, installed with the ``plot``
extra (``pip install "pmcontrols[plot]"``). The numbers it draws come
straight from a ``cpm`` or ``crash`` result; nothing here computes a
schedule.
"""

from __future__ import annotations

from ._result import Result

_CRITICAL = "#c0392b"
_NORMAL = "#4a86c5"
_SLACK = "#d7dde3"


def gantt(result: Result, ax=None, show_slack: bool = True, title: str | None = None):
    """Draw a Gantt chart of a ``cpm`` or ``crash`` schedule.

    Each activity is a bar from its earliest start to its earliest finish.
    Critical activities (zero total float) are drawn in red, the rest in
    blue, and the available total float is shown as a light bar from the
    earliest to the latest finish. Zero-duration activities render as
    diamonds (milestones).

    Parameters
    ----------
    result : a ``cpm`` or ``crash`` Result (carries es/ef/lf/slack/critical).
    ax : an existing matplotlib Axes to draw on; a new figure is created
        if omitted.
    show_slack : draw the total-float bar behind each non-critical activity.
    title : plot title; a sensible default is used if omitted.

    Returns
    -------
    (figure, axes) : the matplotlib Figure and Axes, for further styling
        or saving.
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch
    except ModuleNotFoundError as exc:  # pragma: no cover - import guard
        raise ModuleNotFoundError(
            "gantt() requires matplotlib; install it with: "
            "pip install 'pmcontrols[plot]'"
        ) from exc

    if getattr(result, "method", None) not in ("cpm", "crash"):
        raise ValueError(
            f"gantt() expects a cpm or crash result, got {result.method!r}"
        )

    df = result.table.sort_values(["es", "ef"]).reset_index(drop=True)
    n = len(df)

    if ax is None:
        fig, ax = plt.subplots(figsize=(9.0, 0.5 * n + 1.2))
    else:
        fig = ax.figure

    for i, row in df.iterrows():
        y = n - 1 - i  # earliest activity at the top
        es, ef, lf = float(row["es"]), float(row["ef"]), float(row["lf"])
        duration = ef - es
        critical = bool(row["critical"])
        color = _CRITICAL if critical else _NORMAL

        if show_slack and lf - ef > 1e-9:
            ax.broken_barh([(ef, lf - ef)], (y - 0.3, 0.6), facecolors=_SLACK)
        if duration <= 1e-9:
            ax.plot([es], [y], marker="D", markersize=9, color=color)
        else:
            ax.broken_barh([(es, duration)], (y - 0.4, 0.8), facecolors=color)

    ax.set_yticks(range(n))
    ax.set_yticklabels(list(df["activity"])[::-1])
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlabel("Time")
    ax.set_title(title or "Project schedule (critical path in red)")
    ax.grid(axis="x", linestyle=":", alpha=0.5)

    handles = [
        Patch(facecolor=_CRITICAL, label="critical"),
        Patch(facecolor=_NORMAL, label="non-critical"),
    ]
    if show_slack:
        handles.append(Patch(facecolor=_SLACK, label="total float"))
    ax.legend(handles=handles, loc="lower right", fontsize=8)

    fig.tight_layout()
    return fig, ax


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt

        return plt
    except ModuleNotFoundError as exc:  # pragma: no cover - import guard
        raise ModuleNotFoundError(
            "this plot requires matplotlib; install it with: "
            "pip install 'pmcontrols[plot]'"
        ) from exc


def evm_curve(pmb, result: Result, ax=None, title: str | None = None):
    """Earned value S-curve: the planned-value baseline with EV, AC, BAC and
    the earned-schedule forecast at the status date.

    Parameters
    ----------
    pmb : the Performance Measurement Baseline (the planned-value curve).
    result : the matching ``evm`` Result.
    """
    plt = _require_matplotlib()
    if getattr(result, "method", None) != "evm":
        raise ValueError(f"evm_curve() expects an evm result, got {result.method!r}")
    s = result.stats
    at, ev, ac = float(s["at"]), float(s["ev"]), float(s["ac"])
    bac = float(pmb.bac)
    ieac = s.get("ieac_t")

    if ax is None:
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
    else:
        fig = ax.figure

    ax.plot(list(pmb.periods), list(pmb.pv), color="#4a86c5", marker="o",
            markersize=3, label="PV (planned value)")
    ax.axhline(bac, color="#7f8c8d", linestyle="--", linewidth=1, label="BAC")
    ax.axvline(at, color="#bdc3c7", linestyle=":", linewidth=1)
    ax.plot([at], [ev], marker="o", markersize=10, color="#2e8b57",
            label="EV (earned value)")
    ax.plot([at], [ac], marker="s", markersize=10, color="#c0392b",
            label="AC (actual cost)")
    if ieac is not None and ieac == ieac:  # ieac == ieac excludes NaN
        ax.plot([at, float(ieac)], [ev, bac], color="#2e8b57", linestyle="--",
                linewidth=1, label="EV forecast (to IEAC)")

    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative value / cost")
    ax.set_title(title or "Earned value (S-curve)")
    ax.grid(linestyle=":", alpha=0.5)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    return fig, ax


def criticality(result: Result, ax=None, title: str | None = None):
    """Bar chart of each activity's criticality index from a ``pert`` result."""
    plt = _require_matplotlib()
    if getattr(result, "method", None) != "pert":
        raise ValueError(
            f"criticality() expects a pert result, got {result.method!r}"
        )
    df = result.table.sort_values("criticality_index", ascending=True)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8.0, 0.45 * len(df) + 1.2))
    else:
        fig = ax.figure
    colors = [_CRITICAL if v >= 0.5 else _NORMAL for v in df["criticality_index"]]
    ax.barh(df["activity"].astype(str), df["criticality_index"], color=colors)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Criticality index (share of simulations on the critical path)")
    ax.set_title(title or "Activity criticality")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig, ax


def mc_distribution(result: Result, ax=None, bins: int = 40, title: str | None = None):
    """Histogram of Monte Carlo completion times from a ``pert`` result.

    The result must come from ``pert(..., keep_samples=True)``.
    """
    plt = _require_matplotlib()
    if getattr(result, "method", None) != "pert":
        raise ValueError(
            f"mc_distribution() expects a pert result, got {result.method!r}"
        )
    sample = result.meta.get("mc_finish_sample")
    if not sample:
        raise ValueError(
            "no Monte Carlo sample on this result; "
            "re-run pert(..., keep_samples=True)"
        )
    if ax is None:
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
    else:
        fig = ax.figure
    ax.hist(sample, bins=bins, color="#4a86c5", edgecolor="white")
    for key, color in (("mc_p50", "#2e8b57"), ("mc_p80", "#e67e22"),
                       ("mc_p95", "#c0392b")):
        value = result.stats.get(key)
        if value is not None:
            ax.axvline(float(value), color=color, linestyle="--", linewidth=1.2,
                       label=f"{key[3:].upper()} = {float(value):.1f}")
    ax.set_xlabel("Completion time")
    ax.set_ylabel("Simulations")
    ax.set_title(title or "Monte Carlo completion distribution")
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig, ax


def network_diagram(result: Result, ax=None, title: str | None = None):
    """Activity-on-node network diagram with the critical path highlighted.

    Works on a ``cpm`` or ``crash`` result, reading precedence from the
    result's provenance. Activities are placed by earliest start.
    """
    plt = _require_matplotlib()
    if getattr(result, "method", None) not in ("cpm", "crash"):
        raise ValueError(
            f"network_diagram() expects a cpm or crash result, "
            f"got {result.method!r}"
        )
    preds = result.meta.get("predecessors")
    if preds is None:
        raise ValueError("result carries no precedence information")
    df = result.table.set_index("activity")

    by_es: dict[float, list] = {}
    for activity in df.index:
        by_es.setdefault(float(df.loc[activity, "es"]), []).append(activity)
    pos = {}
    for es in sorted(by_es):
        column = by_es[es]
        for i, activity in enumerate(column):
            pos[activity] = (es, i - (len(column) - 1) / 2.0)

    if ax is None:
        width = 1.7 * max(1, len(by_es)) + 2.0
        height = 0.95 * max(len(v) for v in by_es.values()) + 2.0
        fig, ax = plt.subplots(figsize=(width, height))
    else:
        fig = ax.figure

    for activity in df.index:
        for p in preds.get(activity, []):
            if p in pos:
                x0, y0 = pos[p]
                x1, y1 = pos[activity]
                critical_edge = bool(df.loc[p, "critical"]) and bool(
                    df.loc[activity, "critical"]
                )
                ax.annotate(
                    "", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(
                        arrowstyle="->",
                        color=_CRITICAL if critical_edge else "#95a5a6",
                        lw=1.8 if critical_edge else 1.0,
                        shrinkA=16, shrinkB=16,
                    ),
                )

    for activity in df.index:
        x, y = pos[activity]
        critical = bool(df.loc[activity, "critical"])
        ax.scatter(
            [x], [y], s=1100, marker="o", zorder=3,
            color="#f9d6d1" if critical else "#dfe9f3",
            edgecolors=_CRITICAL if critical else _NORMAL, linewidths=1.8,
        )
        ax.text(x, y, f"{activity}\n{df.loc[activity, 'duration']:g}",
                ha="center", va="center", fontsize=8, zorder=4)

    ax.set_title(title or "Activity network (critical path in red)")
    ax.set_xlabel("Earliest start")
    ax.set_yticks([])
    ax.margins(0.15)
    fig.tight_layout()
    return fig, ax

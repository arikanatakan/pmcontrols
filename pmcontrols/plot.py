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

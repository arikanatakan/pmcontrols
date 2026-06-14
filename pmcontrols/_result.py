"""The Result protocol: the one object every pmcontrols analysis returns.

Design contract (append-only from v0.1 on):

    Result.method    stable analysis alias ("cpm", "pert", "evm", "crash")
    Result.params    echo of the user's inputs
    Result.stats     named scalars (durations, indices, forecasts, costs)
    Result.alerts    tuple of structured threshold events; empty == on track
    Result.meta      provenance: n, version, input hash, timestamp
    Result.table     tidy per-activity / per-period DataFrame

    r.ok             True iff no alerts  ->  sys.exit(0 if r.ok else 1)
    r.summary()      fixed-width audit text with a plain-language verdict
    r.to_dict()      JSON-safe, integer-versioned schema
"""

from __future__ import annotations

import dataclasses
import datetime
import hashlib
import json
import pathlib
from typing import Any, Mapping

import numpy as np
import pandas as pd

_SCHEMA = 1


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def data_hash(values: Any) -> str:
    payload = json.dumps(values, sort_keys=True, default=str).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()[:16]


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, Mapping):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    return str(obj)


@dataclasses.dataclass(frozen=True)
class Alert:
    """One threshold event: which indicator, where, how bad."""

    indicator: str
    value: float
    threshold: float
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "indicator": self.indicator,
            "value": self.value,
            "threshold": self.threshold,
            "note": self.note,
        }

    def __str__(self) -> str:
        base = f"{self.indicator}={self.value:.3f} breaches {self.threshold:g}"
        return base + (f" - {self.note}" if self.note else "")


@dataclasses.dataclass(frozen=True)
class Result:
    method: str
    params: Mapping[str, Any]
    stats: Mapping[str, float]
    table: pd.DataFrame
    alerts: tuple[Alert, ...] = ()
    meta: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.alerts) == 0

    def to_dict(self) -> dict:
        return {
            "schema": _SCHEMA,
            "method": self.method,
            "params": _jsonable(self.params),
            "stats": _jsonable(self.stats),
            "alerts": [a.to_dict() for a in self.alerts],
            "meta": _jsonable(self.meta),
            "table": _jsonable(self.table.to_dict(orient="list")),
        }

    def summary(self) -> str:
        lines = [f"pmcontrols {self.method} - {self.meta.get('computed_at', '')}"]
        for k, v in self.stats.items():
            lines.append(f"  {k:<24} {v:>12.4f}" if isinstance(v, float) else f"  {k:<24} {v}")
        if self.alerts:
            lines.append("Alerts:")
            lines += [f"  ! {a}" for a in self.alerts]
            lines.append("Verdict: ATTENTION - indicators breach thresholds.")
        else:
            lines.append("Verdict: on track - no indicator breaches thresholds.")
        return "\n".join(lines)


@dataclasses.dataclass(frozen=True)
class PMB:
    """Performance Measurement Baseline: plan once, freeze, control forever.

    The EVM sibling of a control-chart baseline: the time-phased planned
    value curve and budget at completion are fixed at planning time,
    committed to version control, and every reporting period is evaluated
    against them.
    """

    periods: tuple[float, ...]
    pv: tuple[float, ...]
    bac: float
    created_at: str
    version: str

    def __post_init__(self) -> None:
        if len(self.periods) != len(self.pv):
            raise ValueError("periods and pv must have the same length")
        if len(self.periods) < 2:
            raise ValueError("a PMB needs at least two points")
        if any(b > a for a, b in zip(self.pv[1:], self.pv[:-1])):
            raise ValueError("planned value must be non-decreasing")
        if abs(self.pv[-1] - self.bac) > 1e-9 * max(1.0, self.bac):
            raise ValueError("planned value must end at BAC")

    @property
    def planned_duration(self) -> float:
        return float(self.periods[-1] - self.periods[0])

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema": _SCHEMA,
                "periods": list(self.periods),
                "pv": list(self.pv),
                "bac": self.bac,
                "created_at": self.created_at,
                "pmcontrols_version": self.version,
            },
            indent=2,
        )

    def save(self, path: str | pathlib.Path) -> pathlib.Path:
        path = pathlib.Path(path)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
        return path

    @classmethod
    def from_json(cls, text: str) -> "PMB":
        raw = json.loads(text)
        return cls(
            periods=tuple(float(x) for x in raw["periods"]),
            pv=tuple(float(x) for x in raw["pv"]),
            bac=float(raw["bac"]),
            created_at=raw["created_at"],
            version=raw["pmcontrols_version"],
        )

    @classmethod
    def load(cls, path: str | pathlib.Path) -> "PMB":
        return cls.from_json(pathlib.Path(path).read_text(encoding="utf-8"))

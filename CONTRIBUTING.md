# Contributing to pmcontrols

Thanks for your interest. pmcontrols aims to be small, correct, and
validated. The bar for merging is not "the tests pass" - it is "the number
is reproduced from a published or hand-derivable reference."

## Ground rules

- **Every new computation ships with a validation case.** Add an entry to
  `tests/validation_cases.json` with a full derivation and a published or
  hand-derivable reference value, and a test that consumes it. Code without
  a reference value is not merged.
- **Compute from the defining formulation, not from tables or spreadsheet
  conventions.** Use the forward/backward pass, the LP, the interpolation
  formula - not period-end snapshots or marginal-cost shortcuts.
- **The `Result`/`PMB` contract is append-only.** Within major version 0/1,
  no public name, signature, default, or field meaning is removed or
  changed. New fields may be added.

## Development

```
pip install -e ".[dev]"
python -m pytest tests/ -q
ruff check .
```

CI runs the same three steps on Python 3.10, 3.11 and 3.12.

## Architecture

- `network.py` - `cpm`, `pert`; the shared `_normalize` / `_passes`
  forward-backward engine.
- `crash.py` - `crash`, the time/cost trade-off linear program.
- `evm.py` - `plan`, `evm`, `earned_schedule`.
- `_result.py` - the `Result` and `PMB` dataclasses and the JSON-safe
  serialization. Every public function returns a `Result`.

Each public function returns one `Result` so that downstream code (and
agents) can rely on a single shape: `stats`, `table`, `alerts`, `meta`,
`ok`, `summary()`, `to_dict()`.

## Adding a validation case

A case is a self-contained record with its derivation, so a reader can
check the number by hand:

```json
{
  "id": "evm-on-plan-001",
  "method": "evm",
  "source": "Hand derivation; PMBOK definitions",
  "derivation": "Linear PMB BAC=100000 over PD=10; at AT=4, EV=AC=40000 ...",
  "inputs": { "...": "..." },
  "expected": { "cpi": 1.0, "spi_t": 1.0 },
  "tol": 1e-9
}
```

Then add a test that loads the case and asserts each expected value.

## Reporting issues

Open an issue with a minimal reproducible example and the expected value,
ideally with a citation to the textbook or standard you are checking
against.

# pmcontrols for AI agents

Project control is not a language task. An LLM asked to "compute the
critical path" or "forecast the completion date" will often produce
plausible-looking arithmetic that is wrong — a misplaced backward pass,
an EVM index inverted, an earned schedule confused with schedule
variance. pmcontrols exists so an agent can call a validated function
instead of doing the math in tokens.

## Use the tool, don't recompute

- Critical path / slack → `pmcontrols.cpm(activities)`
- Three-point schedule risk → `pmcontrols.pert(activities)`
- Cheapest deadline compression → `pmcontrols.crash(activities, target=...)`
- Earned value status → `pmcontrols.evm(pmb, ev, ac, at)`

Each returns a `Result` with `.stats` (named scalars), `.table` (tidy
DataFrame), `.alerts`, and `.to_dict()` for a JSON-safe, versioned
payload. Use `r.ok` for a pass/fail gate and `r.summary()` for a
human-readable verdict.

## Contract

The public API and the `Result`/`PMB` schema are frozen from 0.1 on, so
generated code keeps working. Inputs are plain dict records, so an agent
can build them directly from a table or a user description.

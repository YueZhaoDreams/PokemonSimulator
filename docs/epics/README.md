# Epics

This directory contains outcome contracts for multi-slice work. Draft from `_template/spec.md`. After a human accepts the outcome, run `create-features-for-epic` to produce `breakdown.json` and child slices under `docs/features/`.

Human approval before delivery:

1. Set `docs/epics/<slug>/breakdown.json` `plan_status` to `approved`.
2. Set the epic spec status to `approved`.
3. Set each child slice spec `Status: ready`.
4. Then run `/implement-epic-features <slug>` (or `/fix-feature` for a single slice).

Gate passes are recorded in `.harmonia/epics/<slug>.json` under `passed_gates` (append the gate id after verification). Copy `.harmonia/epics/_template.json` when creating a new epic tracker file.

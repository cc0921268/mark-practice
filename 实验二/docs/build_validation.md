# Build validation — 实验二

GitHub Skill sources: funewa/amazon-consumer-insight

Self-authored business Skill definitions were removed. Each retained Skill has an ADAPTATION.md source record. skill-creator is validation-only.

Validation status: All project tests passed after cleanup.
Packaging excludes vendor, virtual environments, caches, bytecode, logs, and obsolete archives.

## Adapter verification (2026-11-12)

The published `funewa/amazon-consumer-insight` Skill remains unchanged. `src/consumer_insight_adapter.py` maps the course CSV to its evidence-first contract. Five experiment-two tests pass, including missing fields, duplicate IDs, unknown values, evidence and path boundaries.

## Archive policy (2026-11-12)
ZIP packaging is disabled for this project. No v1.0 ZIP or aggregate archive is generated or retained. Final delivery is the clean project directory.


# Legacy schema v1

Schema v1 was the former Chat/Codex coordination format. It used `REVIEW.yaml`
and legacy `decision_author` values such as `chat` and `codex`.

No v1 task records are retained in the current facts repository. The validator
keeps a read-only compatibility branch so imported historical facts can be
diagnosed without being mistaken for current work. New tasks must use schema
version 2, `agent:luna`, `agent:terra`, or `agent:sol`, and `DECISION.yaml`.

This file is the only compatibility reference. It does not define the current
workflow, permissions, lifecycle, or approval rules.

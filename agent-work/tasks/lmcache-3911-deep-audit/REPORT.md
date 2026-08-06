# Executive Summary

LMCache/LMCache#3911 is a concrete report of excessive startup CPU RAM under a
Qwen3.5, mamba-align, and LMCache MP transfer configuration. The relevant source
paths exist, but the reported memory magnitude and causal interaction were not
runtime-confirmed. Recommendation: `needs-more-investigation`.

# Evidence Reviewed

- `agent-work/tasks/lmcache-3911-screening/RESULT.yaml`
- `agent-work/bindings/LMCache-LMCache.yaml`
- Issue #3911 body and two public comments
- Current local target baseline `dev` at `f625b9733ad38c6b1bb3ba3d5083998ab5307ffb`
- Targeted source and test searches in the LMCache checkout

# Existing Work

The explicit PR search for #3911 and the inspected title/configuration queries
returned an empty observation. This is not proof that no related work exists.
Commit `65c2ae81` (`#3613`) provides mamba/GDN hybrid MP support and an
align-mode scheduler validation helper; it is foundational and not evidence of
an issue-specific memory fix. Other inspected hits were documentation, CI,
general engine-driven, or refactoring work without established semantic linkage.

# Technical Analysis

The relevant path is:

`LMCacheMPConnector.__init__`
→ `validate_mamba_step_alignment`
→ KV group/layout registration
→ `start_load_kv`
→ worker `submit_retrieve`
→ `EngineDrivenContext.prepare_retrieve`
→ SHM slot views or pickle payload
→ scatter into paged KV
→ `commit_retrieve`.

`CPUCacheContext` also constructs a fixed-capacity block-id buffer and a
geometry-derived temporary CPU buffer. `KVLayerGroupsManager` supplies the
hybrid/window group geometry consumed by that allocation. These facts identify
the measurement points; they do not establish a root cause.

The three evidence levels are:

- Reported: >100 GB at startup, and later 80 GB to 250 GB in lmcache-driven mode.
- Source-confirmed: align validation, CPU temporary-buffer construction, SHM
  context selection, slot mapping, retrieve/scatter/commit lifecycle.
- Runtime-confirmed: none.

# Feasibility

Source-only analysis is complete enough to identify a bounded next measurement,
but implementation is not feasible responsibly from this environment. A focused
reproduction needs the reporter's vLLM/container/model setup, torch, and GPU;
local pytest and torch are unavailable.

# Risks

- The allocation may belong to vLLM startup or server-side SHM pool sizing rather
  than the connector itself.
- Hybrid/mamba KV group geometry may make simple block-size reasoning invalid.
- SHM slot lifetime and per-process mapping must be measured, not inferred from
  source alone.
- No maintainer direction or acceptance signal is visible in the reviewed issue.

# Recommendation

`needs-more-investigation`, confidence `medium`. Do not enter Candidate
Admission or implementation. Obtain a runnable environment or maintainer
measurements identifying the oversized allocation, then perform a narrow source
verification and regression-test design.

The user has decided to abandon this Issue task. It is closed for the current
workflow and will not proceed to Candidate Admission, implementation, or
upstream contribution.

# Boundary

This record is a Deep Audit result only. It does not authorize implementation,
Candidate Admission, or upstream contribution.

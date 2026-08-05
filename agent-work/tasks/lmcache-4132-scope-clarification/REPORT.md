# Scope

Repository: LMCache/LMCache

Issue: LMCache/LMCache#4132

Investigation type: bounded Scope Clarification

Collection date: 2026-08-05

The investigation was limited to current upstream support/deprecation signals, the exact upstream baseline, current layerwise/CacheBlend paths, recent related work, and maintainer-authored or contributor-role discussion. It did not perform Candidate Admission or implementation.

# Upstream Baseline

The configured official remote was fetched with prune without changing the LMCache worktree. The baseline used for this investigation is:

- Upstream branch: `dev`
- Upstream commit: `a7afadebb9248b62b5c533ce2c12297e9d94fc4a`
- Local branch: `dev`
- Local commit: `f625b9733ad38c6b1bb3ba3d5083998ab5307ffb`
- Local relation: 0 commits ahead, 12 commits behind upstream
- Local worktree: clean

# Current Path Status

The legacy path involved by #4132 remains present in the upstream source:

- `lmcache/v1/compute/blend/utils.py`: `LMCBlenderBuilder` retains a class-level `_blenders` mapping and `get_or_create()`.
- `lmcache/v1/compute/blend/blender.py`: `LMCBlender`, `process_qkv`, `blend_layer`, `blend`, and mutable `LMCBlendMetadata` flow remain present.
- `lmcache/v1/compute/blend/metadata.py`: `LMCBlendMetadata.clean()` remains the cleanup method.
- `lmcache/integration/vllm/vllm_v1_adapter.py`: the vLLM V1 connector still obtains the blender and exposes `start_load_kv`.

Source presence is confirmed. It does not establish that this path is an accepted contribution target.

The upstream tree also contains the newer MP path:

- `lmcache/v1/multiprocess/modules/blend_v3.py`: `BlendV3Module`.
- MP configuration exposes `--engine-type blend` for the current CacheBlend V3 implementation and `--engine-type blend_legacy` for the original CacheBlend.
- `docs/source/kv_cache_optimizations/cacheblend.rst` presents MP CacheBlend as the current enablement path.

# Deprecation and Maintainer Signals

The legacy in-process documentation pages for blending and layerwise operation contain warnings that in-process mode is deprecated and recommend MP mode. The current CacheBlend documentation preserves the in-process material under a Legacy section and documents MP CacheBlend separately.

Issue #4131 is the startup companion issue for the same old vLLM V1 blending path. Its visible discussion contains a comment from ApostaC stating that the code path is deprecated. PR #4157 contains the same signal and remains open; its patch addresses model registration and startup configuration, not the three #4132 failure modes.

This is strong evidence that the reported legacy path is not the preferred contribution surface. It is not a direct maintainer confirmation on #4132, so acceptance of a new fix for #4132 remains unconfirmed.

# Related Work

- PR #3217 remains open and targets a `process_qkv` tensor-alignment failure with CPU regression tests and reported GPU validation. It is technically adjacent to one reported #4132 symptom, but it does not establish ownership or solve singleton state, request reentrancy, or all staging-buffer behavior.
- PR #3228 remains open and targets CacheBlend separator-token matching; its discussion says a cleaner CacheBlend implementation was being developed.
- PR #4162 remains open and targets packed KV layout support in CacheBlend V3.
- PR #4172 is merged and concerns global CacheBlend coordinator matching.

These items show continued CacheBlend development, but the current active direction is the MP/CacheBlend V3 ecosystem rather than acceptance of new changes to the deprecated in-process V1 path.

# Scope Boundary

The clarified boundary is:

`LMCache/LMCache#4132` describes a real source-level interaction surface in a legacy path, but the contribution target is not yet confirmed. Any future work must first decide whether to redirect the investigation to MP CacheBlend V3, address a supported replacement path, or stop because the legacy path is out of scope.

This result does not approve Candidate Admission and does not authorize implementation, branch creation, commits, pushes, Issue interaction, or Pull Request creation.

# Recommendation

Keep the candidate at `needs-more-investigation`. Ask Chat to review whether the evidence is sufficient to close the legacy path as out of scope or to define a new supported-path question. Do not enter Candidate Admission until that scope decision is explicit.

# Limitations

- No GPU runtime reproduction was performed.
- No maintainer response directly on Issue #4132 was found.
- The deprecation signal is from current documentation and a contributor-role comment on the companion path; role and scope do not prove a formal maintainer decision for #4132.
- No LMCache source, branch, commit, merge, rebase, reset, or upstream write was performed.

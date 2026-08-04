# Executive Summary

Issue #4132 has a source-supported failure surface but not an independently runtime-confirmed failure. The source contains the reported shared blender/metadata state, request-sized layerwise staging buffers, QKV comparison/scatter logic, and a normal-completion cleanup point. The reporter's variable-length CUDA replay and three crashes remain reported behavior only.

PR #4157 is not a direct implementation of #4132. It targets startup model registration and explicitly says `Fixes #4131`; its patch does not touch the three #4132 failure mechanisms. A maintainer comment on #4157 says the related code path is deprecated and the edits will not be accepted. Issue #4132 itself has no comments, Timeline events, linked PR, or maintainer confirmation.

Recommendation: `needs-more-investigation`, confidence `medium`.

# Evidence Reviewed

- Completed Evidence Collection in `agent-work/tasks/lmcache-4132-evidence/`.
- Live Issue #4132: open, no labels, no assignee, zero comments, empty Timeline, and no Development branches or pull requests.
- Live PR #4157 metadata, body, changed files, review, and comments.
- Public source clone `/home/sun/py/LMCache`, branch `dev`, baseline `f625b9733ad38c6b1bb3ba3d5083998ab5307ffb`.
- Issue-reported runtime baseline `668a1fd` and environment from the completed evidence.

# Existing Work

PR #4157 is an adjacent CacheBlend startup/model-registration change. Its body lists deferred blender creation, `register_model`, configuration validation, a `blend_special_str` default correction, and a None check before `blend()`, and says `Fixes #4131`. The changed files are the vLLM adapter, blender builder, blender configuration validation, example documentation, and configuration default.

The PR does not change `process_qkv`, `LMCBlendMetadata.clean`, old-KV slicing, staging-buffer length handling, `blend_layer` reentrancy, or exception handling for #4132. It is therefore adjudicated as `unrelated-to-4132-core` / subsystem-adjacent, not `direct implementation` or a complete/partial fix for the three reported modes.

Other Evidence PR hits were keyword-only: MP observability (#3150), disk staging allocation/cleanup (#4036, #3620), token database crash handling (#3819), cache-salt/request identity (#2880, #2962), and DeviceOps singleton refactoring (#4077). They do not implement the #4132 behavior. Historical Issues #1875 and #1064 are adjacent raw candidates, not implementation evidence. Companion Issue #4131 concerns startup model registration.

The only maintainer-authored position found was PR #4157 comment `https://github.com/LMCache/LMCache/pull/4157#issuecomment-5027460658`, stating that the code path is deprecated and the edits will not be accepted. This is not a direct response to #4132, so its scope impact remains an open question.

# Technical Analysis

## Code path map

1. `lmcache/v1/compute/blend/utils.py`: `LMCBlenderBuilder.get_or_create` stores one `LMCBlender` per `instance_id`; `get` returns that cached object.
2. `lmcache/v1/compute/blend/blender.py`: `LMCBlender.__init__` creates one `LMCBlendMetadata`; `blend` drives the `blend_layer` generator; `blend_layer` drives the layerwise retrieval/model generators and cleans metadata at normal completion.
3. `lmcache/v1/compute/blend/metadata.py`: `LMCBlendMetadata` contains mutable `imp_indices`, `attn_mask`, and `positions`; `clean` sets them to `None`.
4. `lmcache/v1/compute/blend/blender.py`: `process_qkv` calls connector `get_kv`, performs check-layer tensor comparison, records top indices, and writes selected K/V rows into the returned old buffers.
5. `lmcache/v1/gpu_connector/gpu_connectors.py`: `VLLMBufferLayerwiseGPUConnector.batched_to_gpu` allocates compute/load buffers from `num_all_tokens`, maps them per layer, transfers layers, deletes old mappings, and releases the final buffers; `get_kv` returns the mapped tensor pair.
6. `lmcache/integration/vllm/vllm_v1_adapter.py`: connector initialization obtains the blender; `start_load_kv` iterates eligible requests and calls `self.blender.blend` with token, mask, cache, slot mapping, and cached-token arguments.

## Validity distinction

- Reported behavior: the reporter claims variable-length requests produce stale-row shape mismatch, stale metadata shape mismatch after an exception, and interleaving failures under async scheduling; the reporter also claims a 900-request replay completed with local defensive changes.
- Source-confirmed behavior: the shared cached blender, mutable metadata, whole mapped KV tensors, request-sized staging allocation, normal-end cleanup, generator lifecycle, and vLLM invocation path are present at the inspected baseline.
- Runtime-confirmed behavior: none independently confirmed in this audit; no GPU reproduction or test run exercised the reported workload.

The static facts make the three reported modes technically plausible, but they do not alone prove that each mode occurs in production or that the proposed defensive changes are sufficient.

# Feasibility

Feasibility is `medium`.

The likely source surface is compact and identifiable, and the existing code has seams around `process_qkv`, metadata cleanup, staging-buffer access, and `start_load_kv`. However, the repository search found no direct unit-test file for `LMCBlender`, `LMCBlendMetadata`, or `blend_layer`. Reproduction requires a CUDA environment, vLLM 0.19.1-compatible integration, CacheBlend configuration, and variable-length load. The exact accepted boundary is also unclear because the maintainer response on the adjacent PR calls the path deprecated.

Expected change areas, if later authorized, would be the blender/metadata lifecycle and possibly GPU connector buffer access, with vLLM adapter error/reentrancy behavior requiring explicit scope confirmation. No patch or implementation plan is produced here.

# Risks

- Slicing or resizing old K/V tensors can invalidate the later `imp_indices` scatter if the original token length is not preserved.
- Cleanup at blend entry may address exception residue but not concurrent interleaving on shared mutable state.
- Buffer lifetime and ping-pong release order are CUDA-sensitive.
- Converting blend failures into per-request failures changes error containment and needs integration validation.
- The path may be deprecated, and no maintainer has confirmed that #4132 remains an accepted contribution target.

# Recommendation

`needs-more-investigation` with `medium` confidence. The evidence is sufficient to justify a focused scope clarification and, if the path remains supported, a dedicated GPU reproduction/test design. It is not sufficient to classify #4157 as an implementation PR, to claim runtime confirmation, or to advance to Candidate Admission.

# Boundary

This record is a Deep Audit result only.
It does not authorize implementation or upstream contribution.

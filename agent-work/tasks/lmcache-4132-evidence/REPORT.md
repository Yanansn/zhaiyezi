# Scope

Repository: LMCache/LMCache  
Issue: #4132  
Collection time: 2026-08-04T08:51:04Z

# Collected Evidence

Issue, comments, Timeline, Development observations, explicit-number/title/symptom/semantic PR queries, issue queries, raw related candidates, and public source references are recorded in `evidence/4132.yaml`.

Issue comments count: 0. Timeline event count: 0. The Issue page Development section displayed “No branches or pull requests”. These are recorded as empty observations.

# Source Facts

At source baseline `dev@f625b9733ad38c6b1bb3ba3d5083998ab5307ffb`, `LMCBlenderBuilder` stores blenders in a class-level mapping keyed by `instance_id`; `LMCBlender` stores runtime metadata in `self.metadata`; `process_qkv` reads connector KV tensors and updates selected rows; `blend_layer` advances retrieval/model generators and calls `metadata.clean()` near the end of its generator; and the layerwise GPU connector allocates, maps, deletes, and releases per-layer staging buffers. The vLLM adapter creates or obtains the blender during connector initialization and calls `self.blender.blend` from `start_load_kv` for eligible requests. The source-reference paths and line locations are in the evidence file.

# Limitations

- no runtime reproduction
- no GPU validation
- no maintainer confirmation
- no upstream LMCache worktree was modified
- GitHub search results are raw query observations and were not adjudicated
- the local source clone is a user Fork remote at `dev@f625b973`; the Issue body reports `668a1fd` as its runtime source build

# Boundary

This record contains evidence only.

# Suggested Next Step

Await Chat Deep Audit.

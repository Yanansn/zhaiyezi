# GitHub Issue Candidate Discovery

- Repository: `ai-dynamo/dynamo`
- Generated: `2026-08-06T06:52:49.418417Z`
- Scope: open, unassigned, latest 50; include labels: none; exclude labels: none
- Query matches: 155; inspected: 50
- Results: 21 candidates without known PR evidence; 29 with PR evidence; 0 insufficient-evidence
- Local known-Issue exclusions: 1

## Candidate Issues (21)

- [ai-dynamo/dynamo#12742](https://github.com/ai-dynamo/dynamo/issues/12742) — [BUG]: prometheus_names.py is out of sync with Rust source — labels: bug, language::rust, python, metrics, observability
- [ai-dynamo/dynamo#12636](https://github.com/ai-dynamo/dynamo/issues/12636) — [CONTRIBUTION]: Centralize worker component names in prometheus_names::component_names (PREFILL/BACKEND/ENCODE/DIFFUSION) & migrate hardcoded registration sites — labels: language::rust, backend::vllm, metrics, observability, backend::sglang, backend::trtllm, contribution-request
- [ai-dynamo/dynamo#12475](https://github.com/ai-dynamo/dynamo/issues/12475) — [Dynamo MultiNode Kimi-K3] [H200 Recipe Please!] Kimi-K3 deployment on H200 (Hopper/SM90) hits FP8 MLA prefill kernel assertion — labels: bug, platform support, dynamo-runtime, backend::vllm, dep:draft
- [ai-dynamo/dynamo#12463](https://github.com/ai-dynamo/dynamo/issues/12463) — [BUG]: vLLM disaggregated serving over InfiniBand returns garbage tokens when UCX_NET_DEVICES is unset on passthrough VMs — labels: bug, language::python, dynamo-runtime, nixl, backend::vllm, deployment::k8s, kvbm, Dynamo 1.3.0, runtime
- [ai-dynamo/dynamo#12360](https://github.com/ai-dynamo/dynamo/issues/12360) — [CONTRIBUTION]: Make OnceLock Env var a !marco pattern — labels: language::rust, refactor, contribution-request, runtime
- [ai-dynamo/dynamo#12355](https://github.com/ai-dynamo/dynamo/issues/12355) — [BUG] vllm-runtime 1.3.0-dev.1-cuda13: baked flashinfer-jit-cache pin breaks any in-container vLLM upgrade (serve-time registry failure) — labels: dynamo-runtime, backend::vllm, runtime
- [ai-dynamo/dynamo#12317](https://github.com/ai-dynamo/dynamo/issues/12317) — Log effective runtime defaults at startup for key serving knobs — labels: enhancement, dynamo-runtime, observability
- [ai-dynamo/dynamo#12312](https://github.com/ai-dynamo/dynamo/issues/12312) — Make etcd lease TTL configurable for runtime discovery liveness — labels: enhancement, dynamo-runtime, discovery, fault-tolerance
- [ai-dynamo/dynamo#12307](https://github.com/ai-dynamo/dynamo/issues/12307) — Let router selectors request strict DP-rank admission — labels: enhancement, language::rust, dynamo-runtime, router
- [ai-dynamo/dynamo#12306](https://github.com/ai-dynamo/dynamo/issues/12306) — Track active-request ISL pressure by worker and DP rank for router selection — labels: enhancement, language::rust, dynamo-runtime, router
- [ai-dynamo/dynamo#12303](https://github.com/ai-dynamo/dynamo/issues/12303) — Expose best device-tier overlap on router admission responses — labels: enhancement, language::rust, dynamo-runtime, metrics, observability, router
- [ai-dynamo/dynamo#12301](https://github.com/ai-dynamo/dynamo/issues/12301) — Expose router queue and KV indexer operation metrics — labels: enhancement, language::rust, dynamo-runtime, metrics, observability, router
- [ai-dynamo/dynamo#12300](https://github.com/ai-dynamo/dynamo/issues/12300) — Account for active request load in router worker selection — labels: enhancement, language::rust, dynamo-runtime, router
- [ai-dynamo/dynamo#12299](https://github.com/ai-dynamo/dynamo/issues/12299) — Expose endpoint taint snapshots in Python bindings — labels: enhancement, language::python, dynamo-runtime, python, router, runtime
- [ai-dynamo/dynamo#12296](https://github.com/ai-dynamo/dynamo/issues/12296) — Add opt-in graceful shutdown hooks for Python worker decorators — labels: enhancement, language::python, dynamo-runtime, runtime
- [ai-dynamo/dynamo#12293](https://github.com/ai-dynamo/dynamo/issues/12293) — Support first-yield gating for Python-backed HTTP streams — labels: enhancement, dynamo-runtime, python, frontend
- [ai-dynamo/dynamo#12292](https://github.com/ai-dynamo/dynamo/issues/12292) — Support graceful stop behavior on HTTP client disconnect — labels: language::rust, dynamo-runtime, dynamo-llm, frontend, fault-tolerance
- [ai-dynamo/dynamo#12290](https://github.com/ai-dynamo/dynamo/issues/12290) — low-prio: Expose detached Python Context while preserving trace metadata — labels: enhancement, language::python, observability
- [ai-dynamo/dynamo#12200](https://github.com/ai-dynamo/dynamo/issues/12200) — DEP: Extend PD-connector compatibility validation beyond the PdConnector/HMA case — labels: bug, language::python, dynamo-runtime, nixl, backend::vllm, kvbm, dep:draft
- [ai-dynamo/dynamo#12198](https://github.com/ai-dynamo/dynamo/issues/12198) — [BUG]: MTP speculative decoding crashes on NIXL-transferred requests for Mamba-hybrid models — labels: bug, nixl, backend::vllm, kvbm
- [ai-dynamo/dynamo#12197](https://github.com/ai-dynamo/dynamo/issues/12197) — [BUG]: --enable-prefix-caching crashes decode for Mamba-hybrid models in disaggregated (NixlConnector) serving — labels: bug, nixl, backend::vllm, kvbm

## Interpretation

This is Candidate Discovery evidence only. `no_known_related_pr` does not mean `available`; the assigned Agent must continue Deep Audit, ownership, semantic PR, design, and feasibility checks.

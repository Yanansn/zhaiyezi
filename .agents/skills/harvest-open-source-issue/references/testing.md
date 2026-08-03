# Testing strategy

Use a testing ladder:

1. Format and generated-file consistency
2. Static analysis and linting relevant to changed files
3. Targeted unit or package tests
4. Focused integration tests
5. End-to-end, conformance, hardware, or cloud tests when justified
6. Project CI verification

Represent the planned and actual layers in `PROJECT.yaml` using `not-planned`, `not-applicable`, `pending`, `passed`, `failed`, `blocked`, `not-run`, or `ci-only`. A passed layer requires evidence; failed, blocked, not-run, and CI-only layers require a reason.

For accelerator and inference projects, distinguish static, CPU unit, CPU integration, single-GPU, multi-GPU, model E2E, benchmark, and upstream-CI evidence. Passing CPU tests never implies GPU, model, distributed, or performance correctness.

For every command, record working directory, prerequisites, purpose, expected success signal, actual result, and any limitation. Distinguish unrelated flakes from regressions only with evidence.

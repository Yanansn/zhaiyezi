# Testing strategy

Use a testing ladder:

1. Format and generated-file consistency
2. Static analysis and linting relevant to changed files
3. Targeted unit or package tests
4. Focused integration tests
5. End-to-end, conformance, hardware, or cloud tests when justified
6. Project CI verification

For every command, record working directory, prerequisites, purpose, expected success signal, actual result, and any limitation. Distinguish unrelated flakes from regressions only with evidence.

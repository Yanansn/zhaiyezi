# Validation: ai-dynamo/dynamo#12694

## Passed

```bash
python3 - <<'PY'
# Parse both workflows and assert all six setup jobs use a 30-minute job
# deadline, their install steps use 20 minutes, Helm remains at 15 minutes,
# and both deploy gates reject cancelled.
PY
git -C /home/sun/py/dynamo diff --check
/tmp/dynamo-precommit.ayWWVO/bin/pre-commit run --files \
  .github/workflows/pr.yaml .github/workflows/post-merge-ci.yml
```

The YAML and timeout/gate assertions passed. All applicable targeted pre-commit
hooks passed, including YAML, codespell, merge-conflict, line-ending,
trailing-whitespace, and pytest marker checks. The target diff has no
whitespace errors.

## Not run

- `actionlint` is not installed; repository pre-commit YAML checks passed.
- No Kubernetes/vCluster/Helm deployment or GitHub Actions run was available.
- No checkpoint end-to-end test was run; it depends on the unavailable CI
  deployment environment.

## Harness note

An initial local regex-based assertion did not recognize the YAML job block
boundary. It made no repository change and was replaced by the passing YAML
structure assertion above.

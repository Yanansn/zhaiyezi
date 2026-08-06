# Pull Request Draft

Title:

`fix(ci): fail checkpoint gate on cancelled setup`

Body:

```markdown
## Overview:

Prevent cancelled DynamoCheckpoint setup jobs from being treated as a passing deploy result.

## Details:

- give snapshot-agent installation three distinct deadlines: 15 minutes for Helm readiness, 20 minutes for the install step, and 30 minutes for the setup job
- remove `cancelled` from the accepted results in the PR and post-merge deploy status checks
- keep conditional `skipped` jobs valid so unrelated framework lanes do not block the gate

This lets Helm report an unhealthy DaemonSet as a normal job failure while keeping the outer job timeout as a safety limit. If the job is still cancelled for another reason, the deploy gate now fails instead of going green with the checkpoint tests skipped.

## Where should the reviewer start?

Start with `deploy-status-check` and the three `deploy-snapshot-agent-checkpoint-*` jobs in `.github/workflows/pr.yaml`. The matching post-merge jobs use the same timeout ordering and gate behavior.

## Related Issues

- Closes #12694

## Validation

- `pre-commit run --files .github/workflows/pr.yaml .github/workflows/post-merge-ci.yml`
- YAML structure assertions for the 15/20/30-minute timeout ordering and accepted gate results
- `git diff --check`

The Kubernetes/vCluster failure path requires repository CI and was not run locally.
```

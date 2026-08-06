# Implementation: ai-dynamo/dynamo#12694

## Boundary

Only `.github/workflows/pr.yaml` and `.github/workflows/post-merge-ci.yml` are
changed. No application, Helm chart, test, or registry code is modified.

## Local branch and base

- Branch: `fix/ci-checkpoint-gate-12694`
- Base: `upstream/main` at `3de5663e9efdb60bedcb042e3b6c1d8427b148a2`
- Fork remote: `origin` (`bzsuni/dynamo`)
- Upstream remote: `upstream` (`ai-dynamo/dynamo`)

## Change

1. Keep Helm readiness at 15 minutes, bound each snapshot-agent install step at
   20 minutes, and bound the containing setup job at 30 minutes.
2. Restrict `deploy-status-check` to `success` and `skipped`; `cancelled` is no
   longer treated as a passing aggregate result.
3. Apply the same behavior to PR and post-merge checkpoint workflows.

## Prepared publication metadata

- Commit: `fix(ci): fail checkpoint gate on cancelled setup`
- PR title: `fix(ci): fail checkpoint gate on cancelled setup`
- PR body summary: explain the distinct GitHub/Helm deadlines, the narrowed
  gate policy, and that static checks passed while Kubernetes/GitHub Actions
  validation remains required.

The commit includes the required DCO sign-off. No Pull Request has been created.

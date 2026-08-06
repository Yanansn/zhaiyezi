# Implementation Summary

Implemented the smallest scoped change for `llm-d/llm-d#2157`: a reusable
Google Managed Prometheus `PodMonitoring` resource for the existing GKE TPU
device-plugin metrics exporter.

# Changes

Added:

- `guides/recipes/observability/tpu/kustomization.yaml`
- `guides/recipes/observability/tpu/tpu-metrics-exporter-podmonitoring.yaml`

The resource uses:

- API: `monitoring.googleapis.com/v1`
- Kind: `PodMonitoring`
- Namespace: `kube-system`
- Selector: `k8s-app: tpu-device-plugin`
- Metrics port: `2112`
- Scrape interval: `15s`

The exporter itself is external to llm-d and was not modified.

# Validation

- YAML structural assertions passed.
- `git diff --check` passed.
- `kustomize` rendering was not run because the command is unavailable in the
  local environment.
- No TPU/GKE runtime validation was performed.

# Boundary

This is a local implementation result only. No commit, target-fork Push, Pull
Request, Issue comment, or other public GitHub action was performed.

# Next Action

Await User confirmation before committing the target-repository change.

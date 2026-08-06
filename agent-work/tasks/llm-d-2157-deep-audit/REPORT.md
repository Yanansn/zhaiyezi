# Executive Summary

`llm-d/llm-d#2157` is a concrete observability feature request with a defined
TPU telemetry gap. The Issue has no related PR or assignee. Public evidence and
source inspection support a bounded contribution, but the result is not runtime
confirmed because TPU/GKE and the exporter are unavailable locally.

Recommendation: `candidate-for-admission`, confidence `medium`. This is a
recommendation only; Candidate Admission was not performed.

# Evidence Reviewed

- Issue body, comments, labels, author, and Development state for #2157.
- `candidates-llm-d.md` and `discovery/llm-d-llm-d/INDEX.yaml`.
- Local repository `/home/sun/py/llm-d` at `1758aee`.
- Existing model-server monitoring Kustomize components.
- Prometheus/Grafana installation and dashboard-loading scripts.
- TPU deployment guides and TPU nightly workflow names.

# Existing Work

The Issue has no linked or searched PR result. Existing generic monitoring
assets are related infrastructure, not an implementation of TPU hardware
telemetry. The maintainer stated that contributors without TPU access may use
mock data for tests and that this is acceptable for a PR. The author stated
that they do not have short-term bandwidth and invited others to take the work.

# Technical Analysis

The current monitoring path is:

```text
model-server /metrics
  -> generic PodMonitor
  -> Prometheus Operator selection
  -> Grafana dashboard ConfigMap loading
```

The relevant source facts are:

- `guides/recipes/modelserver/components/monitoring/kustomization.yaml` includes
  only the generic decode PodMonitor.
- `decode-podmonitor.yaml` selects decode pods and scrapes the model-server
  `modelserver` port at `/metrics`.
- `install-prometheus-grafana.sh` configures Prometheus and PodMonitor selectors.
- The dashboard directory contains general inference, KV-cache, failure,
  gateway, P/D, vLLM, and SGLang dashboards; no TPU-specific dashboard was found.
- TPU deployment guides and nightly workflows exist, but the inspected paths do
  not define the Issue's TPU exporter metric names or TPU recording rules.

The Issue's proposed work therefore overlaps the existing monitoring framework,
but requires new TPU-specific scrape, query, dashboard, and documentation
artifacts. The issue report's performance and metric availability claims remain
reported behavior until checked against a TPU exporter deployment.

# Feasibility

Feasibility is `medium` for a bounded configuration/documentation contribution
and `low` for complete runtime validation. A first implementation could be
tested with mock Prometheus samples, manifest rendering, dashboard JSON checks,
and CI. Real metric labels, exporter compatibility, and dashboard correctness
still require TPU/GKE validation.

# Risks

- TPU exporter schemas may differ across TPU generations.
- Recording rules may introduce incorrect joins or excessive cardinality.
- A dashboard can parse successfully while its queries return no real data.
- CI-only validation cannot establish hardware telemetry correctness.

# Recommendation

`candidate-for-admission` is recommended with medium confidence, subject to a
separate User decision. If admitted, keep the first task bounded to the exporter
scrape configuration, mock-tested recording rules, one dashboard, and docs. Do
not include unrelated goodput, cost, error taxonomy, or cluster-fragmentation
work in the first contribution.

# Boundary

This record is a Deep Audit result only. It does not authorize implementation or
upstream contribution.

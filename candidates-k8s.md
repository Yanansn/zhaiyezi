# GitHub Issue Candidate Discovery

- Repository: `kubernetes/kubernetes`
- Generated: `2026-08-06T08:19:43.752230Z`
- Scope: open, unassigned, latest 40; include labels: none; exclude labels: none
- Query matches: 862; inspected: 40
- Results: 14 candidates without known PR evidence; 26 with PR evidence; 0 insufficient-evidence
- Local known-Issue exclusions: 4

## Candidate Issues (14)

- [kubernetes/kubernetes#141200](https://github.com/kubernetes/kubernetes/issues/141200) — [Flaking Test] [sig-node] [Feature:GPUDevicePlugin] Sanity test using nvidia-smi [Provider:aws,gce] should run nvidia-smi and cuda-demo-suite [Serial] — labels: sig/node, kind/flake, needs-triage
- [kubernetes/kubernetes#141198](https://github.com/kubernetes/kubernetes/issues/141198) — [Flaking Test] [sig-apps] Deployment should not disrupt a cloud load-balancer's connectivity during rollout [Provider:aws,azure,gce] — labels: kind/flake, sig/apps, needs-triage
- [kubernetes/kubernetes#141193](https://github.com/kubernetes/kubernetes/issues/141193) — Security implications of named ports in NetworkPolicy — labels: sig/network, needs-triage
- [kubernetes/kubernetes#141186](https://github.com/kubernetes/kubernetes/issues/141186) — [Flaking Test] [sig-k8s-infra] ci-kubernetes-e2e-gci-gce-alpha-features kubetest.Timeout / TearDown / Test / Up [ci-kubernetes-e2e-gci-gce-alpha-features] — labels: kind/flake, sig/testing, needs-triage, sig/k8s-infra
- [kubernetes/kubernetes#141178](https://github.com/kubernetes/kubernetes/issues/141178) — [Flake][sig-api-machinery]k8s.io/apiextensions-apiserver/test/integration.conversion — labels: sig/api-machinery, kind/flake, needs-triage
- [kubernetes/kubernetes#141162](https://github.com/kubernetes/kubernetes/issues/141162) — [Feature request] Single API endpoint for feature gates values — labels: sig/api-machinery, kind/feature, sig/architecture, needs-triage
- [kubernetes/kubernetes#141152](https://github.com/kubernetes/kubernetes/issues/141152) — sig/network: API Server validation error message leaks full ClusterIP CIDR range to low-privileged users — labels: kind/bug, sig/network, needs-triage
- [kubernetes/kubernetes#141138](https://github.com/kubernetes/kubernetes/issues/141138) — [Flaking Test] [sig-network] LoadBalancers ExternalTrafficPolicy: Local [Feature:LoadBalancer] should work for type=LoadBalancer [Slow] — labels: sig/network, kind/flake, needs-triage
- [kubernetes/kubernetes#141136](https://github.com/kubernetes/kubernetes/issues/141136) — [Flaking Test] [sig-network] LoadBalancers ExternalTrafficPolicy: Local [Feature:LoadBalancer] should only target nodes with endpoints [Slow] — labels: sig/network, kind/flake, needs-triage
- [kubernetes/kubernetes#141133](https://github.com/kubernetes/kubernetes/issues/141133) — [Flaking Test] [sig-network] LoadBalancers [Feature:LoadBalancer] should be able to change the type and ports of a UDP service [Slow] — labels: sig/network, kind/flake, needs-triage
- [kubernetes/kubernetes#141085](https://github.com/kubernetes/kubernetes/issues/141085) — sig-windows-gce Security Context test are failing — labels: sig/windows, kind/failing-test, needs-triage
- [kubernetes/kubernetes#141036](https://github.com/kubernetes/kubernetes/issues/141036) — ci-kubernetes-node-arm64-ubuntu-serial periodically doesn't come up — labels: sig/node, kind/flake, priority/important-longterm, triage/accepted
- [kubernetes/kubernetes#140984](https://github.com/kubernetes/kubernetes/issues/140984) — DaemonSet pod can be permanently stuck Pending when its target node is saturated by equal-priority pods during mass rescheduling — labels: kind/bug, sig/scheduling, needs-triage
- [kubernetes/kubernetes#140937](https://github.com/kubernetes/kubernetes/issues/140937) — kubelet: support version emulation for CPU and Topology Manager policy options — labels: sig/node, kind/feature, needs-triage

## Interpretation

This is Candidate Discovery evidence only. `no_known_related_pr` does not mean `available`; the assigned Agent must continue Deep Audit, ownership, semantic PR, design, and feasibility checks.

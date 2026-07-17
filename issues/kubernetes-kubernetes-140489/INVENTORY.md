# Test and CI inventory

## Scope and method

Inventory boundary:

- Kubernetes `master@6d5610685c55faf1eab630ed7f6cd9f6d4accd13` for current test definitions. The five relevant local file blobs exactly matched GitHub `master`; full test names came from Ginkgo `--list-tests` output.
- test-infra `master@04ddafd2e719aead330efeae0290a57906cd732b` for Prow job definitions, presets, and OWNERS.
- GitHub Issue/PR discussion and official AKS/EKS/Kubernetes documentation for capabilities not encoded in YAML.

The test set is complete for the two requested Feature labels in the current `e2e` and `e2e_node` suites. The job set is a relevant, bounded inventory of Kubernetes periodics/presubmits that supply AKS/EKS execution, IPv6/dual-stack, NetworkPolicy, non-COS Linux/EC2, or SIG Network coverage; it is not a list of every unrelated job scheduled on either Prow cluster.

## Test inventory

`yes` means the test definition itself requires that capability. `runtime skip` means the body currently calls `ginkgo.Skip`, even if a job selects its labels.

| Suite | Full test name | Source | Protocol | External IPv6 | Dual-stack | NetworkPolicy | SCTP kernel | Effective today |
|---|---|---|---|---:|---:|---:|---:|---|
| e2e | `[sig-network] Networking should provide Internet connection for containers [Feature:Networking-IPv6] [Experimental][LinuxOnly]` | `test/e2e/network/networking.go:94` | TCP/53 (`nc -vz`) to IPv6 | yes | no | no | no | runnable |
| e2e | `[sig-network] Networking Granular Checks: Pods should function for intra-pod communication: sctp [LinuxOnly] [Feature:SCTPConnectivity]` | `test/e2e/common/network/networking.go:135` | SCTP | no | no | no | yes | runnable |
| e2e_node | same `intra-pod communication: sctp` shared spec | `test/e2e/common/network/networking.go:135` | SCTP | no | no | no | yes | runnable |
| e2e | `[sig-network] Networking Granular Checks: Pods should function for node-pod communication: sctp [LinuxOnly] [Feature:SCTPConnectivity]` | `test/e2e/common/network/networking.go:140` | SCTP | no | no | no | yes | runtime skip (#96482) |
| e2e_node | same `node-pod communication: sctp` shared spec | `test/e2e/common/network/networking.go:140` | SCTP | no | no | no | yes | runtime skip (#96482) |
| e2e | `[sig-network] Networking Granular Checks: Services should function for pod-Service: sctp [Feature:SCTPConnectivity]` | `test/e2e/network/networking.go:177` | SCTP | no | no | no | yes | runnable |
| e2e | `[sig-network] Networking Granular Checks: Services should function for node-Service: sctp [Feature:SCTPConnectivity]` | `test/e2e/network/networking.go:219` | SCTP | no | no | no | yes | runtime skip (#96482) |
| e2e | `[sig-network] Networking Granular Checks: Services should function for endpoint-Service: sctp [Feature:SCTPConnectivity]` | `test/e2e/network/networking.go:263` | SCTP | no | no | no | yes | runnable |
| e2e | `[sig-network] [Feature:IPv6DualStack] Granular Checks: Services Secondary IP Family [LinuxOnly] should function for pod-Service: sctp [Feature:SCTPConnectivity]` | `test/e2e/network/dual_stack.go:469` | SCTP | no | yes | no | yes | runnable |
| e2e | `[sig-network] Netpol [Feature:SCTPConnectivity] [LinuxOnly] NetworkPolicy between server and client using SCTP should support a 'default-deny-ingress' policy [Feature:NetworkPolicy]` | `test/e2e/network/netpol/network_policy.go:1429` | SCTP | no | no | yes | yes | runnable |
| e2e | `[sig-network] Netpol [Feature:SCTPConnectivity] [LinuxOnly] NetworkPolicy between server and client using SCTP should enforce policy based on Ports [Feature:NetworkPolicy]` | `test/e2e/network/netpol/network_policy.go:1447` | SCTP | no | no | yes | yes | runnable |
| e2e | `[sig-network] Netpol [Feature:SCTPConnectivity] [LinuxOnly] NetworkPolicy between server and client using SCTP should enforce policy to allow traffic only from a pod in a different namespace based on PodSelector and NamespaceSelector [Feature:NetworkPolicy]` | `test/e2e/network/netpol/network_policy.go:1476` | SCTP | no | no | yes | yes | runnable |

Counting results:

- `e2e`: ten Feature-labeled specs—one external-IPv6 and nine SCTP; two of the SCTP specs self-skip.
- `e2e_node`: two shared SCTP specs—one runnable and one self-skipping.
- three runnable SCTP specs also carry `Feature:NetworkPolicy`.
- one runnable SCTP spec also carries `Feature:IPv6DualStack`.

## AKS periodic inventory

All four Kubernetes periodics explicitly scheduled on `k8s-infra-aks-prow-build` are in `config/jobs/kubernetes/sig-k8s-infra/periodics.yaml`.

| Job | Purpose | Test target | Node image / OS evidence | IP family | CNI / NetworkPolicy | External IPv6 | SCTP | Selection | Template value |
|---|---|---|---|---|---|---|---|---|---|
| `ci-k8s-infra-aks-build-cluster` | heartbeat | none | not exposed | AKS cluster not described in job | n/a | not tested | not tested | `echo` | cluster selector only |
| `ci-kubernetes-cross-canary` | Kubernetes build | none | Prow node not exposed | not tested | n/a | not tested | not tested | `make release` | resource/DinD pattern only |
| `ci-kubernetes-verify-master-canary` | repository verify | none | Prow node not exposed | not tested | n/a | not tested | not tested | `verify-dockerized.sh` | verify pattern only |
| `ci-kubernetes-e2e-kind-ipv6-canary` | Kind e2e | nested Kind | host OS/kernel absent from YAML; current kubekins image shown | Kind IPv6-only; Prow AKS cluster reported dual-stack | CNI not explicit; no policy installation | `upodroid` reports AKS capability; the selected tests do not prove it | unknown | `Feature: isEmpty && !Slow && !Disruptive && !Flaky` | **closest host/runtime template** |

The AKS canary is the best structural reference, but its current filter excludes both target labels and it does not configure a NetworkPolicy provider.

## EKS/AWS periodic inventory

Relevant Kubernetes periodics in `config/jobs/kubernetes/sig-cloud-provider/aws/ec2-e2e.yaml` run their Prow Pods on `eks-prow-build-cluster`. Their test target is Kubernetes provisioned directly on EC2 by `kubetest2 ec2`, not a managed EKS cluster.

| Job | Target provider / OS | IP family | CNI / NetworkPolicy | External IPv6 | SCTP evidence | Selection | Template value |
|---|---|---|---|---|---|---|---|
| `ci-kubernetes-ec2-conformance-latest` | EC2, default worker image | default/not stated | not configured | unknown | unknown | Conformance only | provisioning reference |
| `ci-kubernetes-ec2-arm64-conformance-latest` | EC2 arm64 | default/not stated | not configured | unknown | unknown | Conformance only | arm64 only |
| `ci-kubernetes-e2e-ubuntu-ec2-containerd` | EC2 Ubuntu/containerd | default/not stated | not configured | unknown | Ubuntu is not proof; no run evidence | skips every `[Feature:.+]` | non-COS Linux reference |
| `ci-kubernetes-e2e-ubuntu-ec2-arm64-containerd` | EC2 Ubuntu arm64/containerd | default/not stated | not configured | unknown | unknown | skips every `[Feature:.+]` | non-COS arm64 reference |
| `ci-aws-ec2-janitor` | resource cleanup | n/a | n/a | n/a | n/a | no tests | not a test template |

Related presubmit `pull-kubernetes-e2e-ec2-cloud-provider-dual-stack-quick` proves that `kubetest2 ec2 --ip-family=dual` is wired into test-infra, but it focuses only `Pods should be submitted and removed` and provides no external-IPv6, NetworkPolicy, or SCTP evidence. `pull-kubernetes-e2e-ec2-eks-conformance-canary` uses an EKS-optimized Amazon Linux 2023 worker image but still provisions through `kubetest2 ec2`; it is not a managed EKS test cluster and runs Conformance only.

## IPv6, dual-stack, NetworkPolicy, and SIG Network references

| Job | File | Provider / OS | IP family | CNI / policy | External IPv6 evidence | SCTP evidence | Focus / skip | Reference value |
|---|---|---|---|---|---|---|---|---|
| `ci-kubernetes-e2e-kind-ipv6` | `config/jobs/kubernetes/sig-testing/kubernetes-kind-ci.yaml` | Kind on default Prow cluster | IPv6-only | not explicit | no target Feature selected | none | `Feature: isEmpty` | generic Kind IPv6 |
| `ci-kubernetes-kind-network-ipv6` | `config/jobs/kubernetes/sig-network/sig-network-kind.yaml` | Kind on default Prow cluster | IPv6-only | not explicit | `Internet.connection` is skipped | explicitly skips SCTP | SIG Network focus | SIG Network selection pattern |
| `ci-kubernetes-kind-network-dual` | same | Kind on default Prow cluster | dual | not explicit | explicitly skips Networking-IPv6 | explicitly skips SCTP | SIG Network focus | dual-stack Kind pattern |
| `ci-kubernetes-e2e-gce-network-policies` | `config/jobs/kubernetes/sig-network/sig-network-gce.yaml` | GCE Ubuntu/containerd per annotation | default IPv4 | `NETWORK_POLICY_PROVIDER=kube-network-policies` | explicitly skipped | explicitly skipped; reporter questions GCE underlay | SIG Network/Conformance/NetworkPolicy | upstream policy-provider pattern |
| `ci-kubernetes-kube-network-policies-conformance-parallel` | `config/jobs/kubernetes-sigs/kube-network-policies/kube-network-policies-periodic.yaml` | Kind on default Prow cluster | IPv4 | kube-network-policies | no | explicitly skipped after COS failure | NetworkPolicy or Conformance | policy install/test script |
| `ci-kubernetes-kube-network-policies-conformance-parallel-ipv6` | same | Kind on default Prow cluster | IPv6-only | kube-network-policies | not selected as a target | explicitly skipped | NetworkPolicy or Conformance | IPv6 policy pattern |

No checked job is a complete reference. A prospective configuration would have to combine pieces from at least the AKS canary, SIG Network Kind dual-stack job, and a NetworkPolicy-provider job, then prove the SCTP runtime.

## Facts, inferences, and unknowns

### Facts

- The AKS Prow cluster selector and privileged IPv6 Kind canary exist.
- A repository member stated that the AKS build cluster has external IPv6 and dual-stack networking.
- Current AKS YAML does not state the worker OS/kernel or install a policy provider.
- Existing relevant jobs exclude the target labels through label filters or skip regexes.
- COS caused SCTP failures in kube-network-policies CI; merged PR #35032 added the skip.
- Official AKS documentation supports dual-stack with Azure CNI Overlay and documents Cilium policy support for supported dual-stack configurations.
- Official EKS documentation says EKS IPv6 clusters do not provide dual-stacked Pods or Services.
- Kubernetes requires a supporting network plugin for SCTP Service and NetworkPolicy behavior.

### Inferences that require validation

- A privileged Kind job on AKS may inherit a kernel capable of SCTP.
- A particular AKS node OS may ship `sctp.ko`.
- Cilium or kube-network-policies may provide the required SCTP enforcement in the proposed nested dual-stack topology.
- The AKS build cluster's external IPv6 route may be reachable from a Pod inside nested Kind/Docker.

These are plausible hypotheses, not facts established by the checked configuration.

### Unknowns

- Exact AKS Prow worker OS, kernel config, module loading policy, and node-image lifecycle.
- Exact CNI and policy behavior of a new nested Kind test cluster.
- Whether all target tests must share one job.
- Current TestGrid success/run evidence; public GCS object reads returned 403 during screening.
- Whether maintainers can offer an on-demand AKS rehearsal before the periodic is merged.
- Whether project trust permits any existing generic rehearsal mechanism; the candidate periodic itself has no PR trigger or rerun command.
- Whether additional cluster quota, secrets, or a dedicated resource pool are required. The existing AKS Kind canary references no Azure credential preset or Boskos resource in its job YAML.

## Ownership

- `config/jobs/kubernetes/sig-k8s-infra/OWNERS`: reviewers/approvers are `sig-k8s-infra-leads`.
- `config/jobs/kubernetes/sig-network/OWNERS`: reviewers and approvers include `aojea`, `bowei`, `cadmuxe`, `mrhohn`, and `rramkumar1`.
- `config/jobs/kubernetes/sig-cloud-provider/aws/OWNERS`: reviewers/approvers are `chrislovecnm` and `justinsb`.

The closest AKS file and the analogous SIG Network files have different owners, so the intended location should be confirmed before implementation.

# Code map

## Verified source baselines

- Kubernetes official `master`: `6d5610685c55faf1eab630ed7f6cd9f6d4accd13`.
- Local Kubernetes checkout: `7e8950f1ec186066fabdfe69d69f92fbb04592da`, clean but four commits ahead of its configured `origin/master`. It was used read-only; no fetch or synchronization was authorized.
- The relevant Kubernetes file blobs exactly match current official `master`, so the test inventory is not based on the local branch difference.
- test-infra read-only archive: official `master@04ddafd2e719aead330efeae0290a57906cd732b`.

## Test definitions

- `test/e2e/feature/feature.go:291`: defines `NetworkingIPv6` as `Feature:Networking-IPv6` and describes required Internet IPv6 connectivity.
- `test/e2e/feature/feature.go:380`: defines `SCTPConnectivity` and states that Pod networking must carry SCTP between Pods.
- `test/e2e/network/networking.go:94`: external IPv6 test targets `2001:4860:4860::8888` on UDP port 53.
- `test/e2e/common/network/networking.go:135`: shared Pod-to-Pod SCTP test, registered in both `e2e` and `e2e_node`.
- `test/e2e/common/network/networking.go:140`: shared node-to-Pod SCTP test; currently skips itself pending #96482.
- `test/e2e/network/networking.go:177`, `:219`, `:263`: Pod-, node-, and endpoint-to-Service SCTP cases; the node-to-Service case self-skips pending #96482.
- `test/e2e/network/dual_stack.go:469`: SCTP over the secondary IP family in a dual-stack cluster.
- `test/e2e/network/netpol/network_policy.go:1417-1504`: three SCTP NetworkPolicy enforcement cases.

The complete execution-surface matrix is in `INVENTORY.md` because this stage explicitly requires a first-class standalone inventory.

## Test data flow

```text
Ginkgo Feature labels
→ Prow job FOCUS/SKIP or LABEL_FILTER selection
→ e2e-k8s.sh / kubetest2 ginkgo invocation
→ cluster topology (IPv4 / IPv6 / dual)
→ node kernel and module availability
→ CNI Service and Pod transport behavior
→ optional NetworkPolicy enforcement
→ external IPv6 or SCTP assertion
```

A correct label filter is only the first gate. Failures can originate at every subsequent layer.

## Existing test-infra entry points

### Closest AKS entry

`config/jobs/kubernetes/sig-k8s-infra/periodics.yaml:103-151`

- `ci-kubernetes-e2e-kind-ipv6-canary`
- `cluster: k8s-infra-aks-prow-build`
- privileged Docker-in-Docker;
- `DOCKER_IN_DOCKER_IPV6_ENABLED=true`;
- `IP_FAMILY=ipv6`;
- current `LABEL_FILTER` excludes all Feature tests.

No generator reference for this file was found; it appears to be direct Prow YAML with TestGrid annotations colocated.

### SIG Network Kind references

`config/jobs/kubernetes/sig-network/sig-network-kind.yaml`

- `ci-kubernetes-kind-network-ipv6`: IPv6 topology and SIG Network focus.
- `ci-kubernetes-kind-network-dual`: `IP_FAMILY=dual` reference.
- both explicitly skip `SCTPConnectivity`; the dual job also skips `Networking-IPv6`.

### NetworkPolicy references

- `config/jobs/kubernetes/sig-network/sig-network-gce.yaml:885`: uses `NETWORK_POLICY_PROVIDER=kube-network-policies`, but skips SCTP/IPv6/dual-stack.
- `config/jobs/kubernetes-sigs/kube-network-policies/kube-network-policies-periodic.yaml`: installs and tests kube-network-policies in Kind, but explicitly skips SCTP after the COS failure.

### AWS/EKS references

`config/jobs/kubernetes/sig-cloud-provider/aws/ec2-e2e.yaml`

- Prow Pods run on `eks-prow-build-cluster`.
- Kubernetes targets are provisioned with `kubetest2 ec2`.
- periodic Ubuntu jobs skip every Feature test.
- the dual-stack quick job is a presubmit and exposes `--ip-family=dual`, but it does not run target network tests.
- `preset-e2e-containerd-ec2` and `serviceAccountName: node-e2e-tests` show protected AWS integration that a local contributor cannot reproduce from YAML alone.

## Likely change surface, not an implementation plan

Depending on maintainer direction, a future patch would probably touch one direct job YAML file and its colocated annotations:

- most likely `config/jobs/kubernetes/sig-k8s-infra/periodics.yaml` if reusing the AKS Kind host;
- possibly `config/jobs/kubernetes/sig-network/sig-network-kind.yaml` if SIG Network owns a new variant;
- less likely `config/jobs/kubernetes/sig-cloud-provider/aws/ec2-e2e.yaml` if owners choose EC2/EKS infrastructure.

Potential configuration dimensions are the job `cluster`, privileged DinD settings, `IP_FAMILY`, Feature selection, NetworkPolicy-provider setup, timeout/resources, and TestGrid annotations. No existing Boskos resource or Azure credential preset is referenced by the AKS Kind canary. That absence does not prove that a new design needs none.

## Local validation seams

- YAML/config loading and repository checks: `make verify`.
- Job validation: `go test ./config/tests/jobs/...` (or the repository's Bazel equivalent).
- Generated fixtures, if a presubmit-policy change requires them: `make update-config-fixture`, followed by review of generated changes.
- Generated job consistency where applicable: `make verify-generated-jobs`; no generator was found for the closest direct YAML.
- Test selection can be checked against Kubernetes Ginkgo `--list-tests` output without a cloud cluster.

The closest candidate is a periodic and defines no PR trigger or rerun command. Static/config presubmits may validate a contributor PR, but the checked configuration does not expose an external-contributor trigger for the AKS runtime job itself.

## CI-only validation seams

- SCTP module availability and loading in the AKS Prow worker/DinD host.
- SCTP across nested Kind Pod and Service networking.
- SCTP NetworkPolicy enforcement by the selected provider.
- external IPv6 reachability from the actual test Pod.
- dual-stack behavior in the exact proposed topology.
- quota, concurrency, secrets, and cleanup behavior on the protected Prow cluster.

These require Prow/cloud execution or evidence supplied by the cluster owners.

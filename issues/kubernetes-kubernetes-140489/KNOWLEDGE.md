# Knowledge

## Why this knowledge is needed

The Issue sounds like a YAML-only job addition, but a job name can hide three separate environments: the Prow cluster that runs the job Pod, a nested Kind cluster, and any cloud cluster provisioned by the job. Feasibility depends on the capabilities at the correct layer.

## Core concepts

### Prow scheduling cluster versus test cluster

`cluster: k8s-infra-aks-prow-build` or `cluster: eks-prow-build-cluster` selects where the Prow Pod runs. It does not prove that the Kubernetes-under-test is AKS or EKS. A job can run on EKS and then create a separate EC2 cluster; it can run on AKS and create Kind inside privileged Docker.

### IPv6-only, dual-stack, and external IPv6

- An IPv6-only Kind cluster gives Pods and Services IPv6 addresses.
- A Kubernetes dual-stack cluster gives them both IPv4 and IPv6 families.
- External IPv6 means a Pod has a usable route to an Internet IPv6 endpoint. A cluster can be dual-stack without allowing that egress.

The target `Networking-IPv6` test runs `nc -vz` against `2001:4860:4860::8888:53` (TCP), so internal dual-stack alone is insufficient.

### SCTP has several dependency layers

SCTP coverage needs:

1. a Linux kernel with SCTP built in or an available module;
2. the container/Kind boundary to expose that host capability;
3. Pod networking and service handling that carry SCTP;
4. for NetworkPolicy tests, a policy implementation that recognizes and enforces SCTP rules.

A platform or CNI name is not proof that all four layers work in the configured job.

### NetworkPolicy is implemented by the network provider

The Kubernetes API accepts `TCP`, `UDP`, and `SCTP` in a NetworkPolicy, but enforcement requires a supporting network plugin. Creating the API object on a default Kind cluster does not by itself prove that the policy is enforced.

### Periodic versus presubmit validation

A periodic runs on a schedule after its configuration is merged. A presubmit runs against a PR. Repository tests can validate YAML shape, Prow policy, generated fixtures, and selection syntax, but only the protected Prow/cloud environment can validate external routing, kernel modules, and real CNI enforcement.

## Important distinctions

- `eks-prow-build-cluster` is not synonymous with an EKS test target.
- Platform documentation describes supported configurations, not the live Kubernetes Prow cluster.
- A successful IPv6 cluster creation does not prove the external IPv6 Feature test was selected.
- Removing `SCTPConnectivity` from a skip regex is not sufficient if the kernel or policy provider cannot support it.
- The node-to-Service and node-to-Pod SCTP specs currently call `ginkgo.Skip` in their own bodies, so selecting their label will not turn them into effective coverage.

## References

- [AKS dual-stack networking](https://learn.microsoft.com/en-us/azure/aks/configure-dual-stack)
- [AKS Azure CNI powered by Cilium](https://learn.microsoft.com/en-us/azure/aks/azure-cni-powered-by-cilium)
- [EKS IPv6 cluster behavior](https://docs.aws.amazon.com/eks/latest/userguide/cni-ipv6.html)
- [Kubernetes Service protocol support](https://kubernetes.io/docs/reference/networking/service-protocols/)
- [Kubernetes NetworkPolicy API](https://kubernetes.io/docs/reference/kubernetes-api/networking/network-policy-v1/)
- [`kubernetes/test-infra#35031`](https://github.com/kubernetes/test-infra/issues/35031), COS/SCTP CI limitation

Official platform documentation and live repository facts were checked on 2026-07-17. Capability claims about the specific Prow clusters remain explicitly qualified where runtime evidence is absent.

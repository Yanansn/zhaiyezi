# Public comment draft

## Publication status

- Current status: Draft
- Target: `kubernetes/kubernetes#140489` Issue comment
- Expected GitHub identity: user-must-specify-before-publication
- Authenticated GitHub identity: verify-before-publish
- Identity verified: no
- Technical review completed: no
- User approved: no
- Publication authorized: no
- Published at: not-published
- GitHub URL: not-published

## Purpose

Confirm the CI environment and ownership boundary before preparing a test-infra change.

## Draft

I did an initial inventory of the target tests and the current test-infra jobs.

The closest existing template I found is `ci-kubernetes-e2e-kind-ipv6-canary` in `config/jobs/kubernetes/sig-k8s-infra/periodics.yaml`. It already runs privileged Kind on `k8s-infra-aks-prow-build` with Docker IPv6 enabled, but its current label filter excludes all Feature tests and it does not configure a NetworkPolicy provider.

The other references provide only parts of the required environment: the SIG Network Kind jobs show IPv6 and dual-stack configuration, while the NetworkPolicy jobs install a policy implementation. All of those relevant jobs currently skip `SCTPConnectivity`. The checked YAML also does not establish whether the AKS worker kernel exposes SCTP to Docker-in-Docker.

Before preparing a PR, could you confirm:

- whether a new narrow Kind periodic on `k8s-infra-aks-prow-build` is the intended direction;
- which NetworkPolicy provider should be used for the SCTP policy cases;
- whether SCTP kernel/module availability has been verified in that runtime; and
- whether one job should cover external IPv6, dual-stack, SCTP, and NetworkPolicy, or whether separate periodics would be acceptable?

I can prepare the config change and local validation once that boundary is clear, but the runtime capability would still need Prow or cluster-owner validation.

## Claims and evidence

- AKS canary path and environment: test-infra `master@04ddafd2`, `config/jobs/kubernetes/sig-k8s-infra/periodics.yaml`.
- SIG Network IPv6/dual-stack references and SCTP skips: `config/jobs/kubernetes/sig-network/sig-network-kind.yaml`.
- NetworkPolicy provider references and SCTP skips: SIG Network GCE and kube-network-policies job configs.
- AKS external IPv6/dual-stack statement: `upodroid` in test-infra PR #37410.
- Kernel/module availability remains unknown; the Draft does not claim it as fact.

## Questions for maintainers

- Intended Prow host and nested-cluster topology.
- SCTP-capable NetworkPolicy provider.
- Runtime kernel evidence and validation owner.
- One combined periodic versus split coverage.

## Publication checklist

- [ ] Live target and community state re-verified.
- [ ] Technical Review completed.
- [ ] User explicitly authorized this exact publication.
- [ ] Expected GitHub identity explicitly specified.
- [ ] Authenticated GitHub identity matches the user-specified expected identity.
- [ ] Published URL and time recorded, if applicable.

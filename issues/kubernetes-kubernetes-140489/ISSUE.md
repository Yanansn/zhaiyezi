# Issue: add CI for external IPv6 and SCTP feature tests

## Source facts

- Upstream Issue: [`kubernetes/kubernetes#140489`](https://github.com/kubernetes/kubernetes/issues/140489)
- Title: `Add [Feature:Networking-IPv6] and [Feature:SCTPConnectivity] CI`
- Opened by Kubernetes member `danwinship` on 2026-07-13.
- Last live verification: 2026-07-17T03:50:58Z.
- State: open; no assignee, milestone, linked branch, or linked implementation PR was visible.
- Labels: `sig/network`, `sig/testing`, `area/ipv6`, `area/network-policy`, `help wanted`, `triage/accepted`.
- `bowei` added the `help wanted` and `triage/accepted` commands on 2026-07-16. No contributor has posted an implementation claim.
- Related coverage-analysis PR: [`kubernetes/test-infra#37410`](https://github.com/kubernetes/test-infra/pull/37410), open and unmerged at verification time. It identifies coverage gaps; it does not implement this Issue.
- Consolidated predecessor: [`kubernetes/kubernetes#140491`](https://github.com/kubernetes/kubernetes/issues/140491), closed after its reporter observed that SCTP includes a dual-stack case and should be handled together with #140489.

## Problem statement

Current Kubernetes CI does not execute the tests labeled `[Feature:Networking-IPv6]` or `[Feature:SCTPConnectivity]`. The two labels require overlapping but non-identical infrastructure:

- `Networking-IPv6` needs a Pod to reach an external IPv6 address.
- SCTP needs Linux kernel support and Pod-network handling for SCTP.
- three SCTP specs also need a NetworkPolicy implementation that enforces SCTP rules;
- one SCTP spec also needs a Kubernetes dual-stack cluster.

The requested outcome is a periodic CI configuration, likely using the AKS or EKS Prow infrastructure, that provides the required capabilities and actually selects these tests.

## Current acceptance signals

- The Issue is accepted and explicitly marked suitable for contributor help.
- The reporter asks for an EKS- or AKS-based periodic that can run `IPv6DualStack`, `Networking-IPv6`, `SCTPConnectivity`, and `NetworkPolicy` coverage.
- A test-infra participant reported that `k8s-infra-aks-prow-build` has dual-stack networking and external IPv6.
- No maintainer has yet confirmed the SCTP kernel/module behavior, NetworkPolicy provider, exact job split, or ownership boundary.

## Stage boundary

This record covers Issue Intake and CI Feasibility Screening only. It inventories tests, existing jobs, infrastructure evidence, likely configuration entry points, and validation limits. It does not choose an implementation, modify upstream configuration, or claim the Issue.

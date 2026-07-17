# Knowledge

## Why this knowledge is needed

Availability cannot be judged from an umbrella checkbox alone. This slice also uses three API representations whose field paths differ, so “all versions” needs a precise meaning.

## Core concepts

- **Handwritten validation (HV):** Go functions explicitly append `field.Error` values. Here, `ValidateRuntimeClassUpdate` compares old and new internal `Handler` values.
- **Declarative validation (DV):** comments such as `+k8s:immutable` drive `validation-gen`, which creates version-specific Go validators.
- **Migration coverage marker:** `MarkCoveredByDeclarative()` tells migration machinery that a handwritten error has a declarative counterpart.
- **Equivalence test:** runs HV and DV against the same create/update case and checks that field, error type, origin, and lifecycle behavior match.
- **Lifecycle prefix:** current tags use `+k8s:beta(since: "1.37")=...`. Beta rules are enforced by default when `DeclarativeValidationBeta` is enabled; HV remains available as the migration counterpart.

## Important distinctions and common misconceptions

- An unchecked tracker entry is not proof of availability. Merged code and live PR state are stronger evidence.
- v1/v1beta1 expose `handler`; v1alpha1 exposes `spec.runtimeHandler`. They represent the same internal `RuntimeClass.Handler` value but do not share the same external field path.
- The API scheme registers all three conversion representations and generated tests cover all three. The kube-apiserver REST storage provider currently exposes only `node.k8s.io/v1` RuntimeClass storage.
- `+k8s:immutable` does nothing on create and rejects a changed value on update. It is semantically aligned with the existing scalar `ValidateImmutableField` check; required/format rules are separate.

## References

- [Tracking issue #136785](https://github.com/kubernetes/kubernetes/issues/136785)
- [Direct merged implementation PR #135046](https://github.com/kubernetes/kubernetes/pull/135046)
- [Single-field analogue PR #136886](https://github.com/kubernetes/kubernetes/pull/136886)

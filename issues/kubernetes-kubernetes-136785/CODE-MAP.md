# Code map

Source baseline: `upstream/master@8bd10c1aede813509875bac792f3bce79fbb6414`.

## Inventory

### Scope and counting method

The inventory covers every RuntimeClass representation registered by `pkg/apis/node/install/install.go`, the internal type used by handwritten validation, the only REST-served version, generated validators, and the dedicated equivalence fixtures. It was established from the install/storage registration and exact type/call sites, not from a standalone keyword count.

### Complete or relevant object set

| Set | Representation | External path | Immutable tag | Runtime REST served |
|---|---|---|---|---|
| Current source type | node/v1 `RuntimeClass.Handler` | `handler` | beta since 1.37 | yes |
| Current source type | node/v1beta1 `RuntimeClass.Handler` | `handler` | beta since 1.37 | no |
| Current source type | node/v1alpha1 `RuntimeClass.Spec.RuntimeHandler` | `spec.runtimeHandler` | beta since 1.37 | no |
| Internal API | `pkg/apis/node.RuntimeClass.Handler` | normalized as `handler` | handwritten | internal only |

`pkg/apis/node/install/install.go` registers v1alpha1, v1beta1, and v1 for conversion/validation and gives priority to v1 then v1beta1. `pkg/registry/node/rest/runtime_class.go` creates storage only under v1. Generated equivalence fixtures deliberately enumerate all three external versions.

### Extensibility and limitations

Handler values are an open string set determined by node/CRI configuration; they are not an enum and no attempt was made to inventory runtime handler names. That runtime extensibility does not affect immutability equivalence.

## Relevant files and responsibilities

- `staging/src/k8s.io/api/node/v1/types.go`: source annotation on `RuntimeClass.Handler` at external path `handler`.
- `staging/src/k8s.io/api/node/v1beta1/types.go`: same shape and path as v1.
- `staging/src/k8s.io/api/node/v1alpha1/types.go`: annotation on `RuntimeClassSpec.RuntimeHandler` at `spec.runtimeHandler`.
- `pkg/apis/node/types.go`: internal `RuntimeClass.Handler` consumed by strategy and HV.
- `pkg/apis/node/validation/validation.go`: create validation plus update-only `ValidateImmutableField(new.Handler, old.Handler, field.NewPath("handler"))`; the immutable error is marked covered, origin `immutable`. It also normalizes `spec.runtimeHandler` to `handler` for comparisons.
- `pkg/registry/node/runtimeclass/strategy.go`: embeds `rest.DeclarativeValidation`, keeps HV in `Validate`/`ValidateUpdate`, and supplies `NodeNormalizationRules` through `DeclarativeValidationConfig`.
- `staging/src/k8s.io/apiserver/pkg/registry/rest/create.go` and `update.go`: generic create/update paths invoke `ValidateDeclaratively` after HV when the strategy opts in.
- `staging/src/k8s.io/apiserver/pkg/registry/rest/validate.go`: runs generated validators, mismatch checks beta/alpha rules when `DeclarativeValidation` is enabled, filters covered HV errors when DV is enforced, and appends enforced DV errors.
- `pkg/apis/node/v1/zz_generated.validations.go`, `v1beta1/...`, `v1alpha1/...`: generated immutable/required/format logic with the appropriate external paths.
- `test/declarative_validation/node/runtimeclass/declarative_validation_test.go`: focused create and update equivalence cases.
- `test/declarative_validation/node/runtimeclass/zz_generated.validations.{main,v1,v1beta1,v1alpha1}_test.go`: generated version list and declared-rule coverage fixtures.

## Lifecycle and data flow

```text
versioned request (v1 in the live REST API)
→ scheme converts to internal pkg/apis/node.RuntimeClass.Handler
→ strategy Validate or ValidateUpdate returns handwritten errors
→ embedded rest.DeclarativeValidation selects the request API version
→ generated version-specific validator evaluates handler/runtimeHandler
→ normalization maps v1alpha1 spec.runtimeHandler errors to internal handler
→ migration checks compare DV with marked HV errors
→ enforced DV errors replace covered HV counterparts
```

Create behavior: the immutable rule returns no error; required and DNS-label format rules validate the value. Update behavior: an unchanged handler is ratcheted/skipped, while a changed handler yields `FieldValueInvalid` at the versioned field path with origin `immutable`.

## Generated-file boundary

The original direct implementation PR changed these generated artifacts:

- `pkg/apis/node/v1/zz_generated.validations.go`
- `pkg/apis/node/v1beta1/zz_generated.validations.go`
- `pkg/apis/node/v1alpha1/zz_generated.validations.go`
- `staging/src/k8s.io/api/node/v1/generated.proto`
- `staging/src/k8s.io/api/node/v1beta1/generated.proto`
- `staging/src/k8s.io/api/node/v1alpha1/generated.proto`

Current generator conventions additionally maintain the four `test/declarative_validation/node/runtimeclass/zz_generated.validations.*_test.go` fixtures. Generated files must not be edited by hand. No generator was run during screening.

## Existing tests and analogues

The dedicated RuntimeClass test proves:

- create: valid handler succeeds; empty, malformed, uppercase/special, and overlength values match HV/DV behavior;
- update: no-op succeeds; changing `runc` to another valid handler produces the immutable error;
- every case runs for v1, v1alpha1, and v1beta1 with normalization rules;
- ObjectMeta create/update equivalence and declared-rule coverage are included.

Closest references:

1. Direct source of truth: merged PR #135046.
2. Small single scalar field: merged PR #136886 (`Secret.Type`), which shows the current source tag → generated validator → marked HV → strategy → focused tests pattern.
3. Framework behavior for parent short-circuits: merged PR #137982; less relevant to this scalar field.

## Local verification commands

No cluster is required:

```bash
go test ./test/declarative_validation/node/runtimeclass
go test ./pkg/apis/node/validation
go test ./pkg/registry/node/runtimeclass
```

An authorized implementation would also run `hack/update-codegen.sh validation`, inspect generated diffs, and rerun the focused tests. The screening brief prohibited code generation that leaves source changes, so it was not run.

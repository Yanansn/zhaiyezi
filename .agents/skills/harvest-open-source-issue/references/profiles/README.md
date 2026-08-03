# Project profiles

Profiles are reusable discovery checklists, not facts about a live repository. Apply them in this order:

```text
common workflow
→ language profile
→ ecosystem profile
→ repository profile
→ repository live instructions
```

Later layers refine earlier ones. Live `AGENTS.md`, `CONTRIBUTING.md`, README files, build configuration, CI, Issue/PR templates, ownership files, and current maintainer statements always win. Record conflicts and the live evidence used; never let a static profile override the repository.

- `languages/` describes language/toolchain discovery.
- `ecosystems/` describes stable ecosystem risks and verification layers.
- `repositories/` supplies repository-specific leads that must be re-verified.

Each YAML file follows `schema.yaml`. Select a profile only when its `match` rules apply, record the selected profiles in `PROJECT.yaml`, and preserve unknown values as `null` or limitations instead of guessing.

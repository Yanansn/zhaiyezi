# Target Repository Management

`registry.yaml` stores target repository identity and contribution metadata.
It deliberately stores no absolute local paths. Local paths are discovered at
runtime from Git remotes using `scripts/repository_discovery.py`.

`discovery.yaml` contains home-relative scan roots. The default roots are:
`~/projects`, `~/workspace`, `~/src`, `~/go/src`, `~/code`, and `~/py`.

The registry separates:

- upstream repository URL;
- optional user fork URL and enablement;
- local discovery enablement;
- contribution enablement;
- language and expected Git identity.

Target repositories are separate from the `zhaiyezi` facts repository. The
facts repository stores protocol records and decisions; target repositories
store contribution code. Discovery only reads local Git metadata and does not
clone, fetch, modify, commit, or push target repositories.

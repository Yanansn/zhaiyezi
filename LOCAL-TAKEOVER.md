# Local Operations Guide

This guide is for recovering or continuing work in the current Codex Multi-Agent Workflow. It does not create authority and does not replace `AGENTS.md`, the task protocol, or a task's `REQUEST.yaml`.

## Start

```bash
cd /home/sun/projects/zhaiyezi
git status --short --branch
git remote -v
python3 scripts/validate_agent_protocol.py
python3 scripts/agent_queue.py list
```

Read `HANDOFF.md`, `AGENTS.md`, the applicable Skill, and the selected task. Use a matching local model/profile manually when available (for example Luna for screening or Terra for implementation); the protocol does not auto-switch models. `assigned_agent` is an authorization and ownership field, not a routing promise.

## Facts repository safety

Only the task's owned paths may be changed. Keep unrelated user files untouched. Before a facts-repository Commit, verify the exact task authorization or valid standing authorization. Push is a separate action and is never implied by Commit.

## Target repository safety

The target project is a separate working repository. Before any authorized code phase, record its branch, HEAD, worktree, and remotes independently. Treat the official repository as read-only and the configured Fork as the possible push remote only after User approval. Do not use destructive synchronization commands. Fast-forward synchronization requires a clean tree, a confirmed official base, no local-only base commits, and explicit authorization.

```bash
git -C /path/to/target status --short --branch
git -C /path/to/target remote -v
git -C /path/to/target rev-parse HEAD
git -C /path/to/target branch --show-current
```

Upstream code, target Fork branches, PRs, Issues, comments, labels, and identity-sensitive public actions are outside the facts repository and require their own explicit approval. Record the result and limitations in the task artifacts.

## Stop conditions

Stop on an unrecognized local change, remote mismatch, missing task boundary, missing approval, conflicting artifact ownership, failed validation, or a request to broaden scope. Report the exact evidence and wait for a new bounded instruction.

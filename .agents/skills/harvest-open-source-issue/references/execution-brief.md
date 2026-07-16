# Execution Brief 约定

普通 Chat 每个工程阶段生成一份简报。Codex 在执行前核验简报，不扩大任务范围。

```markdown
# Execution Brief

## Issue

owner/repository#number；不涉及开源 Issue 的仓库维护阶段写 `not-applicable`

## Stage

一个有边界的单一阶段，例如：code-map、plan、implement、validate、publish、review、close、documentation-contract-update

## Baseline

### Facts repository

- Repository:
- Local path:
- Expected branch:
- Expected commit:
- Expected worktree state:

### Upstream working repository

- Official upstream repository:
- User fork:
- Local path:
- Upstream remote name:
- Fork remote name:
- Base branch:
- Expected upstream base commit:
- Working branch:
- Expected working branch commit:
- Expected worktree state:

### Pull request

- Target repository:
- Target base branch:
- Existing PR:
- Existing PR URL:

不确定的 Commit 写 `verify-before-start`，尚未创建工作分支或 PR 写 `not-created`。Codex 必须分别核验两个仓库，不得默认任一工作树干净，也不得混淆事实仓库 remote 与用户 Fork remote。仅维护事实仓库文档时，Upstream working repository 和 Pull request 可写 `not-applicable`。

## Confirmed facts

- 普通 Chat 已确认的事实；必要时附来源链接。

## Goal

- 本阶段唯一且具体的结果。

## Required investigation

- Codex 必须检查的精确代码路径、行为、测试、错误或 CI 证据。

## Constraints

- 范围、非目标、兼容要求、时间或环境限制。
- 是否允许子 Agent；默认不允许。
- 可选模型建议：机械工作使用轻量模型，复杂诊断或 Review 才使用强模型。

## Expected deliverables

- 本阶段期望得到的文件、代码修改、测试、记录更新、Commit、Push 或 PR 产物。

## Completion and return contract

- 汇报实际修改的文件及每项修改的原因。
- 汇报测试或检查命令、工作目录、环境、结果和限制。
- 只更新本阶段发生变化的事实记录。
- 状态或下一步变化时更新 `STATUS.yaml` 和 `JOURNAL.md`；跨阶段摘要变化时更新根目录 `HANDOFF.md`。
- 汇报当前分支、最新提交和未提交修改。
- 明确哪些内容已经 Push，哪些内容仍仅存在本地。
- 若授权 Push，Push 后提供远端可见的最新 commit SHA。
- 若未授权 Push 或 Push 失败，明确说明普通 Chat 当前不能直接读取本地结果。

### Facts repository result

- repository:
- local path:
- changed files:
- branch:
- commit:
- pushed:
- remote-visible commit:

### Upstream working repository result

- official upstream:
- user fork:
- local path:
- base branch:
- changed files:
- branch:
- commit:
- pushed to fork:
- fork remote:
- remaining local changes:

### Pull request result

- created or updated:
- target repository:
- base branch:
- head branch:
- PR number:
- PR URL:
- state:
- CI state:
- review blockers:

## Approval boundary

- Commit 到 facts repository：allowed / prohibited
- Push facts repository：allowed / prohibited
- Commit 到 upstream working repository：allowed / prohibited
- Push 到 user fork：allowed / prohibited
- 创建或更新 upstream PR：allowed / prohibited
- 另行明确是否允许评论、认领、请求 Review、合并或关闭。
- 未列为已授权的动作一律禁止。

## Stop conditions

- 事实仓库提交与简报基线不一致。
- 上游 Issue 已被认领、关闭、替代或需求发生实质变化。
- 本地存在来源不明的工作树修改。
- facts repository 或 upstream working repository 的 branch、commit、remote、base 或工作树与基线实质不一致。
- 所需操作超出审批边界。
- 测试成本或环境要求明显超出约束。
- 实现需要改变已经确认的方案。
- 缺少必要源码仓库、凭据或环境。
- 记录与实时 GitHub 状态发生实质冲突。

出现任一停止条件时，Codex 必须在修改前停止并报告差异，不得自行猜测或扩大授权。
```

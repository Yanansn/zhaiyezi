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
- Official base branch:
- Expected official base commit:
- Local base branch:
- Expected local base commit:
- Base synchronization required: yes / no
- Fast-forward synchronization allowed: yes / no
- Working branch:
- Expected working branch commit:
- Working branch update allowed: no / merge / rebase / recreate
- Expected worktree state:

### Pull request

- Target repository:
- Target base branch:
- Existing PR:
- Existing PR URL:

不确定的 Commit 写 `verify-before-start`，尚未创建工作分支或 PR 写 `not-created`。Codex 必须分别核验两个仓库，不得默认任一工作树干净，也不得混淆事实仓库 remote 与用户 Fork remote。仅维护事实仓库文档时，Upstream working repository 和 Pull request 可写 `not-applicable`。

remote 名称只是提示，Codex 必须从实际 Git 配置和仓库地址确认官方仓库与用户 Fork。同步本地基础分支和更新已有工作分支是两个独立动作；未明确授权时均禁止。

## Confirmed facts

- 普通 Chat 已确认的事实；必要时附来源链接。

## Goal

- 本阶段唯一且具体的结果。

## Required investigation

- Codex 必须检查的精确代码路径、行为、测试、错误或 CI 证据。

## Knowledge requirements（可选）

- Target reader:
- Concepts that require explanation:
- Required knowledge depth:
- Common misconceptions to address:
- Existing knowledge records to reuse:

不需要领域背景补充时写 `not-applicable`。该字段不要求为了形式生成教程。

## Inventory requirements（可选）

- Inventory required: yes / no / not-applicable
- Object set:
- Counting scope:
- Completeness requirement:
- Extensibility questions:
- Usage matrix required:

Inventory 不适用时写 `not-applicable`；适用时必须区分源码命名集合、默认注册集合和运行时/外部可扩展集合。

## Constraints

- 范围、非目标、兼容要求、时间或环境限制。
- 是否允许子 Agent；默认不允许。
- 可选模型建议：机械工作使用轻量模型，复杂诊断或 Review 才使用强模型。

## Expected deliverables

- 本阶段期望得到的文件、代码修改、测试、记录更新、Commit、Push 或 PR 产物。
- KNOWLEDGE.md: 文件更新、`not-applicable` 或仅保留轻量占位说明。
- CODE-MAP.md Inventory: 所需清单或 `not-applicable`。
- Lifecycle / data-flow section: 所需传播链或 `not-applicable`。

## Publication authorization

```text
Prepare public draft: allowed / prohibited
Publish public draft: allowed / prohibited
Reply to maintainer: allowed / prohibited
Update existing public comment: allowed / prohibited
```

默认值为：

```text
Prepare public draft: allowed
Publish public draft: prohibited
Reply to maintainer: prohibited
Update existing public comment: prohibited
```

发布权限必须由用户针对本轮目标、公开位置和动作明确写为 `allowed`。字段缺失、含糊或仍为 `prohibited` 时，Codex 只能准备 Draft，不得发布。准备、首次发布、回复和更新既有公开内容是四个独立权限；对事实仓库 Commit/Push 或上游代码 Push 的授权不能代替它们。

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
- official remote:
- official base branch:
- fetched official commit:
- local base branch:
- local base before commit:
- local base after commit:
- base synchronization result:
- local base ahead/behind:
- local base worktree:
- changed files:
- working branch:
- working branch commit:
- merge-base with official base:
- working branch updated:
- working branch update method:
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
- Fetch official upstream：allowed / prohibited
- Fast-forward local base branch：allowed / prohibited
- Merge official base into working branch：allowed / prohibited
- Rebase working branch onto official base：allowed / prohibited
- Rewrite or force-push working branch：allowed / prohibited
- Commit 到 upstream working repository：allowed / prohibited
- Push 到 user fork：allowed / prohibited
- 创建或更新 upstream PR：allowed / prohibited
- 另行明确是否允许评论、认领、请求 Review、合并或关闭。
- 按 `Publication authorization` 分别确认准备 Draft、发布、回复和更新公开内容；所有 GitHub 公开动作代表用户本人。
- 未列为已授权的动作一律禁止。

## Stop conditions

- 事实仓库提交与简报基线不一致。
- 上游 Issue 已被认领、关闭、替代或需求发生实质变化。
- 本地存在来源不明的工作树修改。
- facts repository 或 upstream working repository 的 branch、commit、remote、base 或工作树与基线实质不一致。
- 官方 remote fetch 失败，官方默认开发分支无法确认，或 remote 角色与记录不一致。
- 本地基础分支存在独有提交、与官方基础分支 diverge，或同步不能 fast-forward。
- 工作分支存在未识别提交，或更新需要未授权的 merge、rebase、reset、历史改写或 Force Push。
- 所需操作超出审批边界。
- 测试成本或环境要求明显超出约束。
- 实现需要改变已经确认的方案。
- 缺少必要源码仓库、凭据或环境。
- 记录与实时 GitHub 状态发生实质冲突。

出现任一停止条件时，Codex 必须在修改前停止并报告差异，不得自行猜测或扩大授权。
```

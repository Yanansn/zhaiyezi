# Execution Brief 约定

普通 Chat 每个工程阶段生成一份简报。Codex 在执行前核验简报，不扩大任务范围。

```markdown
# Execution Brief

## Issue

owner/repository#number；不涉及开源 Issue 的仓库维护阶段写 `not-applicable`

## Stage

一个有边界的单一阶段，例如：code-map、plan、implement、validate、publish、review、close、documentation-contract-update

## Baseline

- Facts repository:
- Expected facts repository branch:
- Expected facts repository commit:
- Upstream repository:
- Expected upstream branch or commit:
- Local repository path:

commit 不确定时写 `verify-before-start`。Codex 必须在修改前报告基线差异；简报不得默认本地工作树干净。

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

## Approval boundary

- 明确说明 Codex 是否可以评论、认领、Commit、Push、创建或更新 PR、请求 Review、合并或关闭。
- 未列为已授权的动作一律禁止。

## Stop conditions

- 事实仓库提交与简报基线不一致。
- 上游 Issue 已被认领、关闭、替代或需求发生实质变化。
- 本地存在来源不明的工作树修改。
- 所需操作超出审批边界。
- 测试成本或环境要求明显超出约束。
- 实现需要改变已经确认的方案。
- 缺少必要源码仓库、凭据或环境。
- 记录与实时 GitHub 状态发生实质冲突。

出现任一停止条件时，Codex 必须在修改前停止并报告差异，不得自行猜测或扩大授权。
```

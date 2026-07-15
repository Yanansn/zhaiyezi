# Execution Brief 约定

普通 Chat 每个工程阶段生成一份简报。Codex 在执行前核验简报，不扩大任务范围。

```markdown
# Execution Brief

## Issue

owner/repository#number

## Stage

以下之一：code-map、plan、implement、validate、publish、review、close

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

## Approval boundary

- 明确说明 Codex 是否可以评论、认领、Commit、Push、创建或更新 PR、请求 Review、合并或关闭。
- 未列为已授权的动作一律禁止。
```

若核验结果与已确认事实矛盾，或发现 assignee、关联工作、工作树冲突、缺少源码仓库、无法承担的测试要求或模糊授权，Codex 必须在修改前停止并报告差异。

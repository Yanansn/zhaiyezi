# 摘叶子

以真实开源 Issue 为入口，由普通 Chat 负责教学与方案整理、本地 Codex 负责阶段化工程执行，并把过程沉淀为可查询的学习记录。

## 工作原则

- 事实、推断和测试证据分开记录。
- 先理解 Issue 和代码路径，再设计与实现。
- 普通 Chat 每个阶段生成一次 `Execution Brief`；Codex 只执行简报中的工程范围。
- 每个关键改动都说明为什么这样做。
- 未经确认，不执行公开留言、认领、推送或创建 PR。
- 无论合入、阻塞还是放弃，都记录结果和原因。
- 默认不使用子 Agent，记录只更新本阶段发生变化的内容。

候选筛选、Issue 研究与贡献链路：

```text
Issue Screening
→ Candidate Admission Gate
→ Issue Intake
→ Issue Ecosystem Analysis
→ Knowledge
→ Inventory (when applicable)
→ Code Map
→ Root Cause Analysis
→ Draft Comment
→ Technical Review
→ User Approval
→ Identity Verification
→ Publish
→ Maintainer Feedback
→ Discussion Re-analysis (when material discussion changes)
→ Awaiting Scope Confirmation (when the boundary remains incomplete)
→ Confirmed Implementation Boundary Gate
→ Plan
→ Implementation
→ PR
```

`.agents/skills/screen-open-source-issue/` 负责在有限范围内发现和严格审计候选，结果以轻量记录保存在 `screenings/`；被排除或观察中的候选不建立完整 Issue 目录。只有分类为 `available`、通过 Candidate Admission Gate 且用户明确决定继续的 Issue，才可在另行授权后进入 `registry/issues.yaml` 与 `issues/`。

`.agents/skills/harvest-open-source-issue/` 保持负责 Issue 被正式接纳后的生态研究、代码调查、范围确认、实现、测试和 PR。筛选分类不是贡献生命周期状态，`available` 也不等于 `selected`。

`ECOSYSTEM.md` 是每个 Issue 必须维护的一级事实文档，覆盖 Timeline、Development、下游、关联工作、CI 和维护者立场。它是持续研究记录：新评论、新 PR、新 Timeline Event、下游 workaround 或 CI 线索出现时都要更新。可能影响判断的新讨论必须先完成再分析；建议和探索性意见不能直接触发编码，只有确认实现边界后才可进入 Plan。`COMMENT-DRAFT.md` 则是一次公开沟通的冻结 Snapshot，发布后不会为了吸收新生态信息而改写。

`KNOWLEDGE.md` 帮助新读者理解必要背景，Inventory 防止局部样本造成范围误判，`CODE-MAP.md` 保存源码组织与运行事实，`ANALYSIS.md` 才负责基于证据推理。Ecosystem Analysis 强制执行；Knowledge 的深度、Inventory 和 Lifecycle 仍按 Issue 需要控制。

## 公开沟通

```text
Research
    ↓
Draft
    ↓
Technical Review
    ↓
User Approval
    ↓
Publication
```

Issue 评论、回复、PR、Review、Discussion、RFC 以及会出现在 GitHub 上的 Commit 信息，最终都代表用户本人。技术 Review 可以由普通 Chat、人工 Reviewer 或团队完成；用户决定是否公开，Codex 只在明确授权后执行发布。完成 Draft 不等于获得发布权限；默认可以按简报准备草稿，默认禁止发布。

## 协作闭环

```mermaid
flowchart LR
    Chat[普通 Chat：筛选、教学、方案] --> Brief[单阶段 Execution Brief]
    Brief --> User[用户：审批与交接]
    User --> Codex[本地 Codex]
    Codex --> Clone[本地上游 Clone：实现与测试]
    Clone --> Fork[用户 Fork：工作分支]
    Fork --> PR[上游官方仓库：PR、CI、Review]
    PR --> Facts[zhaiyezi：事实记录]
    Facts --> Chat
```

- 普通 Chat：筛选候选、教学、比较方案并决定下一阶段。
- 本地 Codex：按简报执行代码调查、实现、测试和发布。
- GitHub 事实仓库：保存双方可共享的状态、决策和证据。
- 用户：批准外部操作并触发两个 Agent 之间的交接。

> 普通 Chat 只能读取已经推送到 GitHub 的结果；Codex 本地未推送的状态不会自动同步到 Chat。

## 仓库角色

- `Yanansn/zhaiyezi`：事实和交接仓库，保存状态、决策、证据与学习记录。
- 上游官方仓库：Issue、PR、CI、Review 和最终合入的实时权威来源。
- 用户 Fork：上游代码工作分支和 Commit 的 Push 位置。
- 本地上游 Clone：Codex 读取、修改、编译、测试和提交真实代码的工作区。

> 上游项目的真实代码修改和 Commit 不进入 `zhaiyezi`；`zhaiyezi` 只保存已核验的状态、决策、证据和交接记录。

工程贡献流为：`Issue Screening → Candidate Admission Gate → Chat 决策与贡献 Execution Brief → Codex 操作本地上游 Clone → Commit 到工作分支 → Push 到用户 Fork → 创建上游 PR → 更新 zhaiyezi → Chat 重新读取并处理下一阶段`。

PR 属于状态模型的一部分：`testing → pr-ready → submitted → reviewing → merged/closed/rejected/blocked/superseded`。

## 当前任务

参见 `registry/issues.yaml` 和各 Issue 目录中的 `STATUS.yaml`。

新上下文或新 Agent 应先读取 `AGENTS.md` 和 `HANDOFF.md`，再核验 GitHub 实时状态。

详细规则见 [AGENTS.md](AGENTS.md)，当前状态见 [HANDOFF.md](HANDOFF.md)，Ubuntu 操作见 [LOCAL-TAKEOVER.md](LOCAL-TAKEOVER.md)。候选筛选使用 [Screening Brief 模板](.agents/skills/screen-open-source-issue/references/execution-brief.md)，正式贡献阶段使用 [Harvest Brief 模板](.agents/skills/harvest-open-source-issue/references/execution-brief.md)。

## 状态流转

主线：`candidate → screening → awaiting-triage/selected → analyzing → planned → implementing → testing → pr-ready → submitted → reviewing → merged/closed/blocked/rejected/superseded`

实质讨论回退边：`任一活动状态 → discussion-reanalysis → awaiting-scope-confirmation 或 planned`。只有边界仍不完整时进入 `awaiting-scope-confirmation`；通过 Gate 后才回到 `planned`。

状态机和社区讨论再分析的规范性定义以 [AGENTS.md](AGENTS.md) 为准；本页只提供概览。

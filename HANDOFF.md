# 摘叶子当前交接

## 项目目标

以真实开源 Issue 为学习入口，由普通 Chat 完成筛选、教学和执行要求整理，由本地 Codex 按 `Execution Brief` 完成阶段化代码调查、实现、测试和发布。

## 工作系统

- 通用 Skill：`.agents/skills/harvest-open-source-issue/`
- 简报模板：`.agents/skills/harvest-open-source-issue/references/execution-brief.md`
- 项目规则：`AGENTS.md`
- Issue 登记：`registry/issues.yaml`
- 最近任务记录：`issues/kubernetes-kubernetes-140523/`
- 外部事实来源：GitHub
- 事实仓库：`Yanansn/zhaiyezi`，普通 Chat 已可通过 GitHub Connector 读取已 Push 内容

## 当前活动任务

- 当前没有活动 Issue。
- 最近任务：`kubernetes/kubernetes#140523`（`EvictionRequest: add CRUD tests for conformance`）
- 终止状态：`superseded`
- 终止原因：Issue 已由 `anshulchikhale30-p` 认领，为避免重复贡献而放弃。
- 工作分支和 Pull Request 均未创建。

## 当前仓库模型

- 事实仓库：`Yanansn/zhaiyezi`，本地路径为 `~/projects/zhaiyezi`。
- 当前没有活动的上游工作仓库、本地上游 Clone、用户 Fork 工作分支或 PR。
- 选定新 Issue 后，必须在 `STATUS.yaml` 和 Execution Brief 中记录官方仓库、用户 Fork、本地 Clone 路径、base branch、working branch 和 PR 状态；不得提前虚构。

## 已完成

- 创建并安装通用开源 Issue 贡献 Skill。
- 建立项目事实库、状态模型和 Issue 记录模板。
- 读取并记录 Issue 正文、标签、认领状态和现有讨论。
- 完成初步筛选：Issue 范围看起来集中，但尚未获得 `triage/accepted`。
- 完成一次无对话背景的只读冷启动测试；新 Agent 能恢复目标、任务、状态、阻塞、审批边界和下一步。
- 将通用 Skill 纳入仓库，使 Ubuntu Codex 无需依赖当前 ChatGPT 会话即可发现并使用完整工作流。
- 未公开留言、未认领 Issue、未修改 Kubernetes 代码。
- 重新核验 Issue 后发现其他贡献者已认领，已按用户决定终止该任务并补齐终止记录。
- 将工作模型调整为“普通 Chat + 本地 Codex + 公开事实仓库”；Codex 不再承担候选筛选和长篇教学。
- `main` 已成功推送到 `Yanansn/zhaiyezi`，当前 Ubuntu 使用 SSH Host 别名 `github-yanansn`，实际认证身份已核验为 `Yanansn`。
- 普通 Chat 已能通过 GitHub Connector 读取事实仓库。
- 完善普通 Chat、本地 Codex、用户和 GitHub 事实仓库之间的可见性、阶段交接、停止条件与完成回传协议。
- 补充 facts repository、官方 upstream、用户 Fork、本地 Clone 和 PR 生命周期的多仓库协作规则。

## 当前阻塞与风险

- 当前没有选定的新 Issue。
- 当前没有待执行的工程 `Execution Brief`。
- `kubernetes/kubernetes#140523` 不应恢复实现，除非未来重新筛选并明确处理与现有 assignee 的协调问题。
- 本地 `gh` 的认证状态不是持久事实；需要使用 `gh` 时必须先运行 `gh auth status` 实时核验。
- 普通 Chat 只能读取已经 Push 的事实，不能读取 Codex 本地尚未提交或尚未 Push 的状态。

## 下一步

```text
Chat 筛选和教学
→ Chat 生成单阶段 Execution Brief
→ 用户交给 Codex
→ Codex 核验事实仓库、本地工作区和上游 GitHub 实时状态
→ Codex 执行单一阶段
→ Codex 更新事实记录
→ 授权后 Commit 和 Push
→ Chat 重新读取事实仓库
→ Chat 解释、决策并生成下一阶段简报
```

## 新上下文恢复指令

新的 Codex 执行会话必须先执行 `AGENTS.md` 的恢复顺序，并报告：

- 本轮 `Execution Brief` 的阶段、目标、交付物和审批边界
- 项目记录中的状态（当前无活动 Issue，最近任务已 `superseded`）
- GitHub 当前实时状态
- 两者是否存在差异
- Git 分支及未提交改动
- 当前阻塞和建议下一步

没有有效简报或完成恢复报告前，不得直接编码或执行外部操作。

## 最近检查

- 项目记录日期：2026-07-16
- 当前分支应以 `git branch --show-current` 为准。
- 当前提交应以 `git log -1 --oneline` 为准，避免交接文件在每次提交后产生自引用漂移。

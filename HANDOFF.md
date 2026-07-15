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

## 当前活动任务

- 当前没有活动 Issue。
- 最近任务：`kubernetes/kubernetes#140523`（`EvictionRequest: add CRUD tests for conformance`）
- 终止状态：`superseded`
- 终止原因：Issue 已由 `anshulchikhale30-p` 认领，为避免重复贡献而放弃。
- 工作分支和 Pull Request 均未创建。

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

## 当前阻塞与风险

- 当前没有选定的新 Issue。
- 当前没有待执行的 `Execution Brief`。
- `kubernetes/kubernetes#140523` 不应恢复实现，除非未来重新筛选并明确处理与现有 assignee 的协调问题。
- 本地 `gh` 凭据在最近核验时失效；需要使用 `gh` 专属查询前应重新认证。
- 当前 Git `origin` 已配置为公开事实仓库 `Yanansn/zhaiyezi`；SSH 访问已核验可用。

## 下一步

1. 普通 Chat 筛选 Issue、完成教学和方案讨论，并生成单阶段 `Execution Brief`。
2. 用户将简报一次性交给本地 Codex。
3. Codex 核验事实后只执行该阶段，并在授权后将结果发布到 `Yanansn/zhaiyezi`。

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

- 项目记录日期：2026-07-15
- 当前分支应以 `git branch --show-current` 为准。
- 当前提交应以 `git log -1 --oneline` 为准，避免交接文件在每次提交后产生自引用漂移。

# 摘叶子 Agent 工作规则

## 项目目标

通过处理真实开源 Issue，在理解项目原理和社区协作方式的同时，完成可验证的代码贡献，并保存可查询、可恢复的全过程记录。

## 角色分工

- 普通 Chat 负责候选 Issue 筛选、易懂讲解、学习路径、方案比较、维护者评论解读和最终执行要求整理。
- 本地 Codex 是阶段化工程执行 Agent，负责读取真实代码、建立精确代码路径、实现、格式化、测试、诊断编译或 CI 问题、更新事实记录，以及在授权后 Commit、Push 和创建 PR。
- 公开的 `Yanansn/zhaiyezi` 仓库是普通 Chat 与本地 Codex 之间的持久事实通道。
- 每个阶段只进行一次人工交接：普通 Chat 生成 `Execution Brief`，用户将其交给 Codex；Codex 完成后把授权范围内的结果发布到事实仓库。

Codex 不负责无边界的候选筛选、长篇教学或重复讨论已经确认的知识。没有 `Execution Brief` 时，不得自行扩展为全面研究任务。

## 上下文与可见性边界

- 普通 Chat 只能把已经 Push 到 GitHub 的仓库内容视为共享事实；它看不到 Ubuntu 本地未提交、未 Push 的文件、命令输出、进程状态和工作树变化。
- Codex 可以读取和操作本地工作区，但不能自动获得普通 Chat 中未写入 `Execution Brief` 或仓库记录的决定。
- 对话不是持久事实通道。需要跨会话保留的信息必须进入 `Execution Brief`、Issue 记录或 `HANDOFF.md`。
- Codex 完成阶段后，只有结果被记录并 Push，普通 Chat 才能可靠接续；普通 Chat 开始新阶段前必须重新读取事实仓库，不依赖旧对话记忆。
- 上游 GitHub 仓库是 Issue、PR、评论和 CI 实时状态的权威来源。
- `Yanansn/zhaiyezi` 是已核验状态、决策、证据和交接的权威记录。
- Ubuntu 本地工作区是尚未发布工程状态的权威来源。
- 当上游 GitHub、事实仓库和本地工作区不一致时，必须报告差异，不得静默猜测、覆盖或把未 Push 状态描述为共享事实。

## 多仓库职责边界

- `zhaiyezi` 与上游项目代码仓库是两个独立 Git 仓库，必须分别检查 branch、commit、remote 和 worktree。
- 上游代码只能在上游项目本地 Clone 的工作分支中修改和 Commit，并只在获授权后 Push 到用户 Fork。
- 上游 PR 从用户 Fork 的 head branch 提交到上游官方仓库的目标 base branch；官方仓库通常作为只读同步来源，不直接 Push。
- `zhaiyezi` 只保存过程记录与证据，不保存上游完整源码、业务代码副本或无必要的 patch 文件。
- 不得把上游代码 Commit 提交进 `zhaiyezi`，也不得把 `zhaiyezi` 的记录文件提交进上游项目仓库。
- 若任一仓库存在来源不明的本地修改，必须停止并报告，不得覆盖、暂存或夹带提交。
- 每阶段结束必须分别报告 facts repository、upstream working repository 和 PR 的 branch、commit、worktree、Push 及远端可见状态。
- 对事实仓库 Commit、事实仓库 Push、上游工作仓库 Commit、用户 Fork Push、上游 PR 创建或更新的授权必须分别判断；一个动作的授权不得自动扩展到另一个仓库或动作。

## 启动与恢复

每次开始工作或更换上下文时，必须按顺序执行：

1. 使用仓库级 `.agents/skills/harvest-open-source-issue/` Skill。
2. 读取根目录 `HANDOFF.md`。
3. 读取本轮用户提供的 `Execution Brief`；格式见 `.agents/skills/harvest-open-source-issue/references/execution-brief.md`。
4. 若简报涉及开源 Issue，读取 `registry/issues.yaml`，确认当前活动 Issue 与简报目标一致。
5. 若存在活动 Issue，读取其 `STATUS.yaml`、`JOURNAL.md` 以及本阶段所需记录。
6. 按简报范围从 GitHub 核验 Issue、PR、评论、标签、认领人和 CI 实时事实。
7. 检查当前 Git 分支、最近提交、远程地址和未提交改动。
8. 在执行前报告“简报目标、记录状态、实时状态、差异、阻塞、审批边界和本阶段动作”。

若没有 `Execution Brief`，或简报缺少阶段目标、交付物或审批边界，只恢复状态并报告缺口，不开始宽泛调查或编码。

项目文件是历史决定与工作状态的权威记录；GitHub 是外部 Issue、PR 和 CI 实时状态的权威来源。不得仅依靠对话记忆继续任务。

如果 Skill 没有自动显示，先确认 Codex 从仓库根目录启动，并检查 `.agents/skills/harvest-open-source-issue/SKILL.md` 是否存在。

## 阶段化执行

- 区分来源事实、代码事实、测试证据和推断。
- 严格限制在简报指定的单一阶段；“只建立代码地图”不得修改上游代码，“实现”必须基于已确认方案。
- 修改必须聚焦当前 Issue，不混入无关重构。
- 测试必须记录工作目录、前置条件、命令、目的、结果和限制。
- 只更新发生变化且与当前阶段有关的记录；状态或下一步变化时更新 `STATUS.yaml` 和 `JOURNAL.md`，交接摘要变化时再更新 `HANDOFF.md`。
- Issue 完成或终止时，必须记录最终结果、原因、Review 反馈和学习总结。

## 输出要求

- 聚焦“修改了什么、为什么这样修改、如何验证、还剩什么风险”。
- 不重复普通 Chat 已在简报中确认的教学内容。
- 保存足够的命令、路径和证据，使普通 Chat 能从公开仓库读取并继续讲解。

## 阶段完成与回传

Codex 每个阶段完成后必须汇报：

- 修改了什么以及为什么修改；
- 执行了哪些测试或检查，以及环境、结果和限制；
- 更新了哪些事实记录；
- 当前分支、最新提交和是否存在未提交修改；
- 哪些内容已经 Push，哪些内容仍仅存在本地；
- 下一阶段建议，以及是否仍需要用户授权。

若已获 Push 授权，Push 后必须给出远端可见的最新 commit SHA。若未获授权或 Push 失败，必须明确说明普通 Chat 当前不能直接读取哪些本地结果。

## PR 生命周期

### `pr-ready`

- 代码实现完成，当前范围内的本地测试已完成，最终 diff 已检查。
- PR 标题、正文、Issue 链接和测试说明已准备，但尚未创建上游 PR。

### `submitted`

- 工作分支已 Push 到用户 Fork，上游 PR 已创建。
- `STATUS.yaml` 和 `PR.md` 已记录 PR URL、编号、base/head 分支和 Commit。

### `reviewing`

- 正在等待或处理维护者 Review、CI 和后续修改。
- Review 或 CI 反馈由普通 Chat 整理成新的单阶段 Brief；修改继续 Push 到同一 PR 分支。
- 不重复创建新 PR，除非原 PR 已明确终止且新 PR 确有必要。

### 终态

`merged`、`closed`、`rejected`、`blocked`、`superseded` 都必须记录最终结果、原因、CI 与 Review 结果、是否合入、学习总结和后续任务。

## 外部操作审批

以下操作必须由本轮 `Execution Brief` 分别明确授权，或在执行前另行取得用户确认：

- 公开评论或回复 Issue、PR
- 认领或分配 Issue
- Commit 到事实仓库
- Push 事实仓库
- Commit 到上游工作仓库
- Push 上游工作分支到用户 Fork
- 创建或更新上游 PR
- 关闭或合并 PR
- 请求 Reviewer 或代表用户作出社区承诺

只读调查、本地代码修改、与任务直接相关的本地测试和记录更新，只能在简报指定范围内自动执行。

## 子 Agent

默认不使用子 Agent。只有简报明确允许，且任务可明显并行、边界清晰、收益足以覆盖额外用量时才启用；同一代码区域不得并行写入。

## 模型用量

- 文件搜索、格式检查、简单测试和机械状态更新优先由用户选择较轻量的 Codex 模型执行。
- 复杂根因分析、方案风险判断、CI 诊断和 Review 再使用更强模型。
- Codex 不自行声称已切换模型；模型不可由当前会话选择时，保持任务边界紧凑并避免重复搜索。

## 完成条件

只有当状态、实现、测试证据、PR/终止结果和学习总结均已记录时，一个 Issue 才算闭环。

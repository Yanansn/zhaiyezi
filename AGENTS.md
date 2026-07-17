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

## 上游基础分支同步

- 上游代码仓库原则上使用用户 Fork 作为可 Push remote、官方仓库作为只读同步 remote；`origin` 和 `upstream` 只是惯例，必须从 `git remote -v` 和仓库地址核验实际角色。
- 每个涉及真实上游代码的阶段开始时，先记录工作树、当前分支、remotes 和 HEAD。在 Execution Brief 授权 fetch 后，执行 `git fetch --prune <official-remote>`，核验官方默认开发分支以及本地基础分支相对官方基础分支是 ahead、behind、diverged 还是一致。
- 使用 `git rev-list --left-right --count <local-base>...<official-remote>/<base>`、`git rev-parse` 和 `git merge-base` 分别核验本地基础分支、官方基础分支和工作分支；不得仅根据分支名推断基线。
- 只有工作树干净、本地基础分支没有独有提交、双方未 diverge、可以 fast-forward，且简报明确允许时，才可通过 `git switch <base>` 和 `git merge --ff-only <official-remote>/<base>` 自动同步。同步前后都要记录 base Commit。
- 不使用无参数 `git pull` 同步基础分支：它可能拉取用户 Fork、受 `pull.rebase` 等配置影响、产生 merge Commit 或改写历史，也不能证明同步目标是官方基础分支。
- 不得为同步自动执行 `git reset --hard`、`git clean -fd`、`git stash`、`git rebase`、`git checkout -- .`、`git restore .`、`git branch -D`、`git push --force` 或 `git push --force-with-lease`。除非简报针对具体仓库、分支和动作逐项授权。
- 工作树不干净、本地基础分支有独有提交、分支已 diverge、remote 与记录不符、官方默认分支无法确认、工作分支有未识别提交、fetch 失败，或同步需要 merge Commit、rebase、reset、丢弃修改时，必须停止并报告。
- 基础分支同步与已有工作分支更新是两个审批边界。工作分支已有提交时，不得自动 merge 或 rebase 官方基础分支；必须报告 Commit、ahead/behind、merge-base、冲突风险、PR 状态和是否会改写已 Push 历史，再由新简报决定暂不更新、merge、rebase 或重新创建。
- PR 已创建时默认不主动 rebase 或 Force Push；只有上游要求、CI 因基线过旧失败、出现冲突、贡献规则要求或用户明确要求时，才提出更新建议。
- `zhaiyezi` 自身也按同样的非破坏原则核验 `main...origin/main`。只有工作树干净、本地没有独有提交、可 fast-forward 且已获授权时，才可 `git fetch --prune origin` 后执行 `git merge --ff-only origin/main`；不得自动 reset 或覆盖本地记录。

## 启动与恢复

每次开始工作或更换上下文时，必须按顺序执行：

1. 使用仓库级 `.agents/skills/harvest-open-source-issue/` Skill。
2. 读取根目录 `HANDOFF.md`。
3. 读取本轮用户提供的 `Execution Brief`；格式见 `.agents/skills/harvest-open-source-issue/references/execution-brief.md`。
4. 若简报涉及开源 Issue，读取 `registry/issues.yaml`，确认当前活动 Issue 与简报目标一致。
5. 若存在活动 Issue，读取其 `STATUS.yaml`、`JOURNAL.md`、强制一级事实文档 `ECOSYSTEM.md` 以及本阶段所需记录。
6. 按简报范围从 GitHub 核验 Issue、PR、评论、标签、认领人、完整 Timeline、Development、关联工作、下游影响和 CI 实时事实。
7. 检查当前 Git 分支、最近提交、远程地址和未提交改动。
8. 在执行前报告“简报目标、记录状态、实时状态、差异、阻塞、审批边界和本阶段动作”。

若没有 `Execution Brief`，或简报缺少阶段目标、交付物或审批边界，只恢复状态并报告缺口，不开始宽泛调查或编码。

项目文件是历史决定与工作状态的权威记录；GitHub 是外部 Issue、PR 和 CI 实时状态的权威来源。不得仅依靠对话记忆继续任务。

如果 Skill 没有自动显示，先确认 Codex 从仓库根目录启动，并检查 `.agents/skills/harvest-open-source-issue/SKILL.md` 是否存在。

## 阶段化执行

```text
Issue Intake
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

- Issue Intake 后必须完成 Issue Ecosystem Analysis，再进入 Knowledge、Code Map 或方案阶段。该阶段不可因 Issue 页面显示“无关联 PR”而跳过；必须检查 Timeline、cross-reference、Development、下游和 CI。
- Ecosystem、Knowledge、来源事实、代码事实、测试证据、推断和决策必须分开记录。
- 每个 Issue 必须有 `ECOSYSTEM.md`。它持续记录 label/project/milestone/assignee/state 变化、mention/reference/cross-reference、linked Issue/PR、Development、Downstream、Related Work、CI、Maintainer Position 和 Open Questions。
- 对每个关联事件必须判断它是上游实现、下游 workaround、相关证据还是仅引用；不得把 cross-reference 自动等同于修复 PR。无法读取 Project 等元数据时，记录权限或可见性限制，不得猜测。
- 新评论、新 PR、新 Timeline Event、新 Downstream PR、新 workaround 或新 CI 证据出现时更新 `ECOSYSTEM.md`。其中可能影响判断的社区讨论必须进入 Discussion Re-analysis；不得沿用旧结论自动继续 Plan 或 Implementation。已审阅或已发布的 `COMMENT-DRAFT.md` 是 Snapshot，不用它承载持续生态变化，也不得因此改写已发布正文。
- 专业名词首次成为关键推理前，应按需在 Issue 的 `KNOWLEDGE.md` 中用目标读者能理解的方式解释。Knowledge 只覆盖理解当前 Issue 所需内容，不得扩展成无关的百科全书式研究。
- 若枚举、注册表、能力矩阵、插件、驱动、状态、Handler 或其他对象集合会影响根因或修复范围，必须在 `CODE-MAP.md` 建立 Inventory。Inventory 必须说明统计范围、方法、定义与使用位置、是否完整、扩展机制和局限。
- 不得把一次关键词搜索称为完整 Inventory；不得把开放字符串集合误写成固定枚举；不得把当前源码中的命名定义集合误写成运行时或外部配置可能值的全集。
- 对象存在明显的创建、转换、传播或消费阶段时，在 `CODE-MAP.md` 记录 Lifecycle / Data Flow。只有内容很大且可跨 Issue 复用时才拆成独立文档。
- 严格限制在简报指定的单一阶段；“只建立代码地图”不得修改上游代码，“实现”必须基于已确认方案。
- 修改必须聚焦当前 Issue，不混入无关重构。
- 测试必须记录工作目录、前置条件、命令、目的、结果和限制。
- 只更新发生变化且与当前阶段有关的记录；状态或下一步变化时更新 `STATUS.yaml` 和 `JOURNAL.md`，交接摘要变化时再更新 `HANDOFF.md`。
- Issue 完成或终止时，必须记录最终结果、原因、Review 反馈和学习总结。

## 社区讨论再分析

本节是社区讨论状态、分类与实施门槛的主要事实来源；README 和 Skill 只概述或映射执行步骤，不另建平行状态机。

核心原则：**Do not optimize for implementation speed. Optimize for convergence with project maintainers. Implementation is triggered by evidence, not by ideas.** 新评论是新证据，不天然是实施指令。

### 触发与状态

- Issue 进入社区讨论后，新的评论、Review、关联 PR 或其他可能改变判断的讨论证据一经发现，立即暂停 Plan、Coding 和未完成的 Implementation，进入 `discussion-reanalysis`。
- `discussion-reanalysis` 表示必须重新读取完整相关讨论并复核已有判断；它不是只阅读最后一条评论，也不是把新意见直接覆盖旧结论。
- 再分析完成但问题定义、实现边界、关键技术假设、非目标或验收标准仍不清楚时，进入 `awaiting-scope-confirmation`。该状态禁止编码。
- 只有通过 Confirmed Implementation Boundary Gate 后，才可进入现有 `planned` 状态；`implementing` 仍需新的、明确授权实现的 Execution Brief。
- 后续任一阶段出现新的实质讨论，均可从当前阶段回到 `discussion-reanalysis`。这是一条回退边，不是另一套生命周期。

### 评论者角色与权限

区分 Issue reporter/author、community contributor、repository member、reviewer、approver、maintainer，以及 SIG/subproject lead。Issue 发起者不必然是最终决策者，社区成员的建议不代表 SIG 共识；Reviewer、Approver 和 Maintainer 的权限也必须对应实际代码路径或子项目。

必要时结合目标路径的 `OWNERS`/`OWNERS_ALIASES`、SIG 或 subproject 归属、历史 Review 和当前 Issue/PR 中的实际职责核验权限。GitHub 身份标签只能作为证据之一；权限权重不能替代技术分析，也不能单独制造共识。

### 讨论证据分类

- **Proposal / Suggestion**：探索性建议，例如 “I wonder if…”, “Maybe…”, “Could we…”, “I think…” 或 “What about…”。不得解释为最终决定。
- **Preference**：某位参与者倾向的方案，尚未形成共识。
- **Clarification**：对问题、范围、约束或历史行为的解释。
- **Emerging Consensus**：具有相关责任的参与者和技术证据逐渐趋同，但仍可能有未决问题；不能仅按评论数量判断。
- **Maintainer Direction**：责任范围内的维护者明确给出推荐方向；仍需检查技术边界是否足够具体。

`Confirmed Implementation Boundary` 不是评论类型、人员角色或单条证据的标签，而是综合上述证据后得出的决策 Gate：修复内容、非目标和验收边界已足够清楚，且不存在会改变方案选择的关键歧义，才允许进入 Plan。

### 再分析记录与最小检查清单

`ECOSYSTEM.md` 是动态记录。每次实质更新保留历史判断，并记录 `Previous assumption`、`New evidence`、`Commenter role and authority`、`Evidence classification`、`Impact`、`Updated conclusion`、`Remaining uncertainty` 和 `Next decision gate`；不得简单覆盖旧判断而丢失变化链路。

1. 获取并阅读完整最新讨论。
2. 识别新增评论及其上下文。
3. 判断评论者角色和与目标范围相关的权限。
4. 区分建议、偏好、澄清、共识、维护者方向或正式边界。
5. 检查问题定义和技术假设是否改变。
6. 检查实现范围与非目标是否改变。
7. 检查是否存在相互冲突的意见或实现。
8. 更新 `ECOSYSTEM.md`、必要的分析记录和 Issue 状态。
9. 选择继续调查、请求澄清、等待更多意见、准备实施、暂停或放弃。
10. 只有满足实施门槛后才进入 Coding。

### Confirmed Implementation Boundary Gate

对新建或重新评估的 Issue，进入 `planned` 前必须确认：问题定义清楚；实现边界和非目标清楚；没有影响方案选择的关键技术歧义；相关社区证据和维护者方向（如需要）足以支持该边界；冲突意见已解决、已有明确处理方式或不影响当前选择；验收标准可描述；现有调查证据仍有效；不需要先向社区确认会改变方案选择的范围问题。Gate 不要求形式化标签、正式批准或由维护者指定全部实现细节；小型明确 Issue 可以凭充分证据通过。代码调查、原型分析和方案比较不受此 Gate 阻止，但不得把原型当作已授权 Implementation。

历史上已经处于 `planned` 或更后阶段的记录不会因本规则自动获得 Gate 认证，也不会被自动降级；恢复或重新评估时必须按当前证据复核。任一 Gate 条件不满足时，保持 `discussion-reanalysis` 或 `awaiting-scope-confirmation`，不得为了更快编码降低标准。

## 输出要求

- 聚焦“修改了什么、为什么这样修改、如何验证、还剩什么风险”。
- 不重复普通 Chat 已在简报中确认的教学内容。
- 保存足够的命令、路径和证据，使普通 Chat 能从公开仓库读取并继续讲解。

## Issue 研究记录职责

- `ISSUE.md` 回答“问题是什么”：保存外部事实、实时状态、讨论、范围和验收条件。
- `ECOSYSTEM.md` 回答“Issue 周围正在发生什么”：持续保存 Timeline、Development、Downstream、Related Work、CI、维护者立场、开放问题和当前生态摘要，并区分真正实现、workaround 与引用。
- `KNOWLEDGE.md` 回答“读懂问题需要知道什么”：保存必要名词、关系、心智模型、例外和常见误解；不写根因结论或预定方案。
- `CODE-MAP.md` 回答“源码实际怎样组织和运行”：保存 Inventory、文件职责、注册和调用路径、Lifecycle / Data Flow、历史及可测试点。
- `ANALYSIS.md` 回答“基于知识和源码事实可以推出什么”：保存根因或假设、证据与置信度、技术限定、风险、方案比较和未决问题，不大段重复 Knowledge 或 Inventory。
- `PLAN.md` 回答“方向确认后具体怎么改”：保存选择方案、替代方案、修改边界、兼容性、测试计划与风险控制。

`ECOSYSTEM.md` 对所有 Issue 都是 Mandatory；Inventory 默认属于 `CODE-MAP.md`，因为它记录源码事实。Knowledge 单独成文是为了让初学者可按需阅读；Lifecycle 默认留在代码地图，避免机械增加文件。

## Public communication contract

### External identity

所有面向 GitHub 社区的公开行为最终都通过用户的 GitHub 身份发布，包括 Issue comment/reply、Pull Request、Pull Request Review、Discussion、RFC，以及会被 Push 到 GitHub 的 Commit message 或 description。ChatGPT 与 Codex 不拥有独立社区身份；这些内容一经公开，代表的是**用户本人**。

事实仓库中的 Draft 只是内部准备产物。文件已经生成、通过校验、Commit 或 Push 到事实仓库，均不等于允许把内容发布到上游社区。

### Responsibilities

- 普通 Chat：负责技术分析、调查结论整理、方案比较、风险判断、评论润色，以及评论、PR 和 Review Draft 的技术 Review；把已审阅结果整理进单阶段 Execution Brief。
- 本地 Codex：负责按简报执行调查、本地修改和 Git 操作；生成公开内容 Draft；在用户明确授权后，使用已核验的用户 GitHub 身份执行评论发布、Issue 更新、PR 创建或更新、Review 请求等动作，并记录 URL、时间和实际内容。
- GitHub：承载对外可见的用户身份、社区记录和维护者反馈，不承担技术决策或授权判断。
- 用户：是所有公开内容的最终主体和审批者。只有用户能授权发布、更新或回复。

### Publication lifecycle

```text
Research
→ Draft
→ Technical Review
→ Awaiting User Approval
→ Publish
→ Awaiting Maintainer Feedback
```

`COMMENT-DRAFT.md`、PR Draft/`PR.md`、RFC Draft 和 Discussion Draft 都必须经过 Technical Review，随后等待用户明确授权，才允许 Publish。Technical Review 可以由普通 Chat、人工 Reviewer 或团队完成。Draft 被修改后，先前针对旧文本的 Review 或授权不得自动套用到实质变化后的新文本；需要重新 Review 和授权。

### Approval rule

未经用户对本轮目标、公开位置和动作的明确授权，禁止：

- 发布或回复 Issue/PR comment；
- 创建或更新 PR，包括 Draft PR；
- 提交 Pull Request Review 或请求 Reviewer；
- assign 用户本人或他人；
- 添加、删除或修改 labels；
- 发布或更新 Discussion、RFC 或其他社区提案。

即使 `COMMENT-DRAFT.md`、PR Draft 或 RFC Draft 已完成、已通过 Technical Review、已 Commit 或已 Push 到事实仓库，也不得自动发布。`Execution Brief` 中缺少发布字段、字段含糊或写为 `prohibited` 时，一律视为未授权。准备草稿、发布草稿、回复维护者和更新现有公开内容是四个独立审批边界。

### Identity verification

发布 Issue comment/reply、Pull Request、Pull Request Review、Discussion、RFC、Reviewer request、Assignment 或 Label command 前，必须记录 `Expected GitHub identity`、实时取得的 `Authenticated GitHub identity` 和 `Identity verified (yes/no)`。预期身份由用户明确指定；认证身份必须在发布前通过 `gh auth status` 或等价的实际认证信息重新获取，不得复用历史核验。

两者不一致、无法取得认证身份或 `Identity verified` 不是 `yes` 时，必须停止发布。不得根据 SSH key 名称、Git remote 或历史记录推断身份。Identity Verification 是 Publish Gate，不是新的生命周期或 Issue 状态。

> Identity verification is a mandatory publication gate. Publication must stop if the authenticated GitHub identity does not match the expected identity.

发布前必须重新核验目标、实时社区状态、待发布文本、用户身份和授权仍然匹配。发布后立即记录 URL、发布时间、实际发布内容和下一步维护者反馈状态。详细契约见 `.agents/skills/harvest-open-source-issue/references/public-communication.md`。

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
- Fetch 官方 upstream
- Fast-forward 本地基础分支
- Merge 官方基础分支到工作分支
- Rebase 工作分支到官方基础分支
- 改写或 Force Push 工作分支
- Commit 到上游工作仓库
- Push 上游工作分支到用户 Fork
- 创建或更新上游 PR
- 关闭或合并 PR
- 请求 Reviewer 或代表用户作出社区承诺

只读调查、本地代码修改、与任务直接相关的本地测试和记录更新，只能在简报指定范围内自动执行。

所有社区公开动作还必须满足上面的 Public communication contract；一般性的“继续”“完成”或对事实仓库 Push 的授权，不得解释为社区发布授权。

## 子 Agent

默认不使用子 Agent。只有简报明确允许，且任务可明显并行、边界清晰、收益足以覆盖额外用量时才启用；同一代码区域不得并行写入。

## 模型用量

- 文件搜索、格式检查、简单测试和机械状态更新优先由用户选择较轻量的 Codex 模型执行。
- 复杂根因分析、方案风险判断、CI 诊断和 Review 再使用更强模型。
- Codex 不自行声称已切换模型；模型不可由当前会话选择时，保持任务边界紧凑并避免重复搜索。

## 完成条件

只有当状态、实现、测试证据、PR/终止结果和学习总结均已记录时，一个 Issue 才算闭环。

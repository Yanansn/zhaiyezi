# 摘叶子当前交接

## 项目目标

以真实开源 Issue 为学习入口，由普通 Chat 完成筛选、教学和执行要求整理，由本地 Codex 按 `Execution Brief` 完成阶段化代码调查、实现、测试和发布。

## 工作系统

- 通用 Skill：`.agents/skills/harvest-open-source-issue/`
- 简报模板：`.agents/skills/harvest-open-source-issue/references/execution-brief.md`
- 研究契约：`.agents/skills/harvest-open-source-issue/references/research-contract.md`
- 项目规则：`AGENTS.md`
- Issue 登记：`registry/issues.yaml`
- 当前任务记录：`issues/kubernetes-kubernetes-140502/` 与 `issues/kubernetes-kubernetes-140489/`
- 外部事实来源：GitHub
- 事实仓库：`Yanansn/zhaiyezi`，普通 Chat 已可通过 GitHub Connector 读取已 Push 内容

## 当前活动任务

- 当前 Issue：`kubernetes/kubernetes#140502`（`The generated test scenarios for RWX volume types dont make sense`）
- 当前阶段：`Awaiting Scope Confirmation`。Issue 状态为 `awaiting-scope-confirmation`，建议为 `promising`；不得进入 Plan 或 Implementation。
- 实时状态：Issue open、无人认领、仍有 `needs-triage`。Issue 新增探索性命名建议，并出现活跃但未获批准的 Kubernetes PR `#140565`。
- Issue Ecosystem：`openshift/release#81632` 仍是已合并的 downstream CI workaround。上游 PR `#140565` 提议跳过所有非空 `FsType`；路径 reviewer/approver `gnufied` 在 `COMMENTED` Review 中表达了不跳过测试、倾向处理测试名称的高权重偏好，但这不是正式 approval、changes requested、SIG 共识或完整实现边界。
- 技术结论：源码确认显式 FsType 会同时进入测试名称和真实 StorageClass 参数，而测试创建 Filesystem RWX PVC 并让两个 Pod 共享读写。社区当前更偏向名称层，底层资源行为是否需要改变仍未确认。
- 范围结论：新证据使旧的 predicate/metadata 方案不再可直接实施。当前方向是保留测试并调查名称层，但仍需确认确切命名机制、是否保持底层 `TestPattern.FsType`/StorageClass 行为、非目标和验收标准。
- 上游工作分支和 Pull Request 均未创建，Kubernetes 源码未修改。
- 上一个 Issue `kubernetes/kubernetes#140523` 已因其他贡献者认领而 `superseded`。

## #140489 CI Feasibility Screening

- Issue：`kubernetes/kubernetes#140489`（`Add [Feature:Networking-IPv6] and [Feature:SCTPConnectivity] CI`）。
- 当前状态：`screening`；推荐保持 `promising`，筛选结论为 `pursue-after-maintainer-confirmation`。
- 实时状态：Issue open、无人认领、无 milestone 或实现 PR，已有 `help wanted` 与 `triage/accepted`。关联 `kubernetes/test-infra#37410` 是 open 的覆盖率分析 PR，不是实现。
- 测试范围：当前 `e2e` 有 1 个 external-IPv6 与 9 个 SCTP spec，其中 3 个还要求 NetworkPolicy、1 个还要求 dual-stack、2 个 SCTP spec 在源码中自跳过；`e2e_node` 共享 2 个 SCTP spec，其中 1 个自跳过。
- 最接近参考：`ci-kubernetes-e2e-kind-ipv6-canary` 已在 `k8s-infra-aks-prow-build` 上运行 privileged Kind/IPv6，但当前 `Feature: isEmpty` 过滤器排除所有目标测试，也未配置 NetworkPolicy provider。
- 已证实限制：现有 SIG Network dual-stack、IPv6 与 NetworkPolicy 参考 Job 均跳过 SCTP；COS/SCTP 失败曾由 `test-infra#35031/#35032` 明确记录。EKS Prow Job 多数实际创建 EC2 测试集群，Prow 调度集群名不能证明 EKS 测试能力。
- 阻塞：AKS worker 的 SCTP kernel/module 可见性、nested Kind 中的 SCTP-capable NetworkPolicy provider、外部 IPv6 的实际 Pod 路径、一个或多个 Job 的边界，以及 SIG Network/SIG K8s Infra 的所有权与运行验证责任均未确认。
- 下一步：先对 `COMMENT-DRAFT.md` 做 Technical Review，再由用户决定是否授权向维护者确认上述环境边界。未确认前不得编写实施计划或修改 test-infra。
- 本阶段未修改 Kubernetes/test-infra、未认领 Issue、未发布评论、未创建分支或 PR。

## Public communication

- Current draft: `issues/kubernetes-kubernetes-140502/COMMENT-DRAFT.md`
- Status: `Published`
- Expected GitHub identity: `bzsuni`
- Authenticated GitHub identity: `bzsuni`
- Identity verified: yes
- Technical review completed: yes
- User approval: granted
- Publication: authorized and published
- Published URL/time: https://github.com/kubernetes/kubernetes/issues/140502#issuecomment-4989997742 at `2026-07-16T08:56:31Z`
- Comment ID: `4989997742`

所有上游评论、回复、PR、Review、Discussion、RFC 和公开 Commit 信息都代表用户本人。本次评论已通过 Technical Review、用户明确授权和发布前身份核验；后续回复或其他公开动作仍需新的独立授权。

Publication checklist：

- Expected GitHub identity
- Authenticated GitHub identity
- Identity verified

身份核验必须在每次发布前实时执行，不允许复用历史核验结果，也不得从 SSH key、Git remote 或历史记录推断。

## 当前仓库模型

- 事实仓库：`Yanansn/zhaiyezi`，本地路径为 `~/projects/zhaiyezi`。
- 当前上游 Clone：`/home/sun/go/src/k8s.io/kubernetes`；代码地图核验基线为官方 `master@7e8950f1ec186066fabdfe69d69f92fbb04592da`。
- 当前没有用户 Fork 工作分支或 PR；这些字段保持未创建状态，不得提前虚构。

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
- 完成 `kubernetes/kubernetes#140502` 的测试注册、fsType、RWX capability、资源创建与多 Pod 读写调用链代码地图。
- 完成 Filesystem/TestPattern 全量 Inventory：46 个命名 Pattern、21 个显式 FsType，区分源码定义、suite 默认选择与外部开放字符串集合。
- 为 `#140502` 建立面向初学者的 `KNOWLEDGE.md`，并将 Knowledge、Inventory、Lifecycle/Data Flow 纳入通用 Skill、模板和轻量校验契约。
- 将 Issue Ecosystem Analysis 升级为所有活动 Issue 的强制持续研究阶段；新增 `ECOSYSTEM.md` 模板、初始化和校验契约，并完成 `#140502` 首版生态分析。

## 当前阻塞与风险

- `kubernetes/kubernetes#140502` 尚未获得 `triage/accepted`；`#140565` 的 skip 方案与 `gnufied` 的 path-approver 偏好存在张力，且没有 approving Review。
- 下一步：确认名称修改的实现范围、底层 FsType 行为、非目标和验收标准；未通过 Confirmed Implementation Boundary Gate 前不得实施。
- 持续更新 `ECOSYSTEM.md`；实质新讨论必须触发再分析，不得直接改写已发布的 `COMMENT-DRAFT.md` Snapshot。
- `kubernetes/kubernetes#140523` 不应恢复实现，除非未来重新筛选并明确处理与现有 assignee 的协调问题。
- `kubernetes/kubernetes#140489` 不能从现有 AKS Job 的名字推断 SCTP/NetworkPolicy 能力；外部贡献者可完成静态配置验证，但关键运行证据需要 Prow 或 cluster owner。
- 本地 `gh` 的认证状态不是持久事实；需要使用 `gh` 时必须先运行 `gh auth status` 实时核验。
- 普通 Chat 只能读取已经 Push 的事实，不能读取 Codex 本地尚未提交或尚未 Push 的状态。

## Next step

1. Monitor the full Issue discussion and PR `#140565` Review state.
2. Obtain scope confirmation for the exact naming change and unchanged behavior/non-goals.
3. Re-run discussion analysis on every material update.
4. Do not prepare a plan or implementation until the Confirmed Implementation Boundary Gate passes and a new Brief authorizes it.

For `#140489`:

1. Technical Review the prepared clarification Draft.
2. If the user later authorizes publication, ask maintainers to confirm the AKS runtime, NetworkPolicy provider, job split, and validation owner.
3. Keep the Issue in `screening`; do not prepare a test-infra implementation until those gates are resolved in a new Brief.

## 新上下文恢复指令

新的 Codex 执行会话必须先执行 `AGENTS.md` 的恢复顺序，并报告：

- 本轮 `Execution Brief` 的阶段、目标、交付物和审批边界
- 项目记录中的状态（#140489 `screening`，#140502 `awaiting-scope-confirmation`，#140523 `superseded`）
- GitHub 当前实时状态
- 两者是否存在差异
- Git 分支及未提交改动
- 当前阻塞和建议下一步

没有有效简报或完成恢复报告前，不得直接编码或执行外部操作。

## 最近检查

- 项目记录日期：2026-07-17
- 当前分支应以 `git branch --show-current` 为准。
- 当前提交应以 `git log -1 --oneline` 为准，避免交接文件在每次提交后产生自引用漂移。

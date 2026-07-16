# 摘叶子当前交接

## 项目目标

以真实开源 Issue 为学习入口，由普通 Chat 完成筛选、教学和执行要求整理，由本地 Codex 按 `Execution Brief` 完成阶段化代码调查、实现、测试和发布。

## 工作系统

- 通用 Skill：`.agents/skills/harvest-open-source-issue/`
- 简报模板：`.agents/skills/harvest-open-source-issue/references/execution-brief.md`
- 研究契约：`.agents/skills/harvest-open-source-issue/references/research-contract.md`
- 项目规则：`AGENTS.md`
- Issue 登记：`registry/issues.yaml`
- 当前任务记录：`issues/kubernetes-kubernetes-140502/`
- 外部事实来源：GitHub
- 事实仓库：`Yanansn/zhaiyezi`，普通 Chat 已可通过 GitHub Connector 读取已 Push 内容

## 当前活动任务

- 当前 Issue：`kubernetes/kubernetes#140502`（`The generated test scenarios for RWX volume types dont make sense`）
- 当前阶段：`Awaiting maintainer feedback`。Issue 状态保持 `awaiting-triage`，建议为 `promising`；维护者方案确认评论已经发布。
- 实时状态：Issue open、无人认领、仍有 `needs-triage`、没有 `triage/accepted`、实现认领或活跃关联 Kubernetes 实现 PR；发布前没有新的维护者方向。
- Issue Ecosystem：已建立强制一级事实文档 `issues/kubernetes-kubernetes-140502/ECOSYSTEM.md`。Timeline 中的 `openshift/release#81632` 是已合并的 downstream CI workaround，仅为 OpenShift 4.23 job 增加 `vsanfs=true` pool selector，不是 Kubernetes 实现 PR；当前无 Active implementation。
- 技术结论：`multiVolume` 当前直接选择 ext4、xfs 和 Windows ntfs 的 DynamicPV Pattern；ext3 DynamicPV Pattern 存在但当前不在该 suite。显式 FsType 会进入真实 StorageClass 参数，同时测试创建 Filesystem RWX PVC 并让两个 Pod 共享读写；最可能是 TestPattern/RWX 组合与实际资源请求问题，不只是名称问题。
- 范围结论：`SupportedFsType` 是开放字符串集合，不能简单在“只排除 ext4/xfs”和“排除所有非空 FsType”之间二选一。需请维护者确认使用已知本地文件系统 predicate，还是为 TestPattern 增加显式 RWX 兼容性元数据。
- 上游工作分支和 Pull Request 均未创建，Kubernetes 源码未修改。
- 上一个 Issue `kubernetes/kubernetes#140523` 已因其他贡献者认领而 `superseded`。

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

- `kubernetes/kubernetes#140502` 尚未获得 `triage/accepted`，SIG Storage 也未确认采用本地文件系统 predicate 还是显式 Pattern 兼容性元数据。
- 下一步：Monitor maintainer response; do not implement without a new Brief.
- 持续更新 `ECOSYSTEM.md`；新评论、Timeline Event、关联 PR、下游 workaround 或 CI 证据不得直接改写已发布的 `COMMENT-DRAFT.md` Snapshot。
- `kubernetes/kubernetes#140523` 不应恢复实现，除非未来重新筛选并明确处理与现有 assignee 的协调问题。
- 本地 `gh` 的认证状态不是持久事实；需要使用 `gh` 时必须先运行 `gh auth status` 实时核验。
- 普通 Chat 只能读取已经 Push 的事实，不能读取 Codex 本地尚未提交或尚未 Push 的状态。

## Next step

1. Monitor maintainer response.
2. Refresh ECOSYSTEM.md when the Issue ecosystem changes.
3. Do not prepare a plan or implementation until community direction is confirmed in a new Brief.

## 新上下文恢复指令

新的 Codex 执行会话必须先执行 `AGENTS.md` 的恢复顺序，并报告：

- 本轮 `Execution Brief` 的阶段、目标、交付物和审批边界
- 项目记录中的状态（#140502 `awaiting-triage`，#140523 `superseded`）
- GitHub 当前实时状态
- 两者是否存在差异
- Git 分支及未提交改动
- 当前阻塞和建议下一步

没有有效简报或完成恢复报告前，不得直接编码或执行外部操作。

## 最近检查

- 项目记录日期：2026-07-16
- 当前分支应以 `git branch --show-current` 为准。
- 当前提交应以 `git log -1 --oneline` 为准，避免交接文件在每次提交后产生自引用漂移。

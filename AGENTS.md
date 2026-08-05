# 摘叶子 Agent 工作规则

## 目标

通过真实开源 Issue 建立可验证的研究、实现和公开贡献记录。`zhaiyezi`
是 facts repository，不保存上游完整源码或无关 patch。

## Codex Multi-Agent Workflow

当前唯一有效的 Agent 流程是：

```text
candidate → evidence → analysis → decision → implementation → pull-request
```

- Luna：candidate discovery、evidence collection、screening、decision proposal。
- Terra：deep audit、source analysis、implementation planning、代码修改和测试。
- Sol：architecture、concurrency、疑难 debugging 和 final technical review；只做升级审查，不实施。
- User：批准 target fork Push、Pull Request 和所有公开 GitHub 行为。

任务固定在 `agent-work/tasks/<task-id>/`，使用 schema version 2：

- `REQUEST.yaml`：任务边界、assigned agent、权限和 `approval_required`；
- `RESULT.yaml`：Agent 执行结果；
- `REPORT.md`：事实和验证报告；
- `DECISION.yaml`：结论、confidence、evidence、risks 和 next action；
- `APPROVAL.yaml`：仅用于 User 已批准的受保护动作。

当前协议不包含人工 Review 节点；决策统一记录在 `DECISION.yaml`。
每个 REQUEST 的 `completion.handoff` 必须记录下一阶段、推荐 Agent 和切换提示。

## 权限边界

Luna/Terra 可以在有界任务内读取、分析、修改本地目标仓库、运行测试、写入
facts，并提交 `zhaiyezi`。Sol 只能读取、分析、写入升级 Decision。

所有 Agent 都禁止：

- 修改上游公开仓库；
- Push target fork；
- 创建或更新 Pull Request；
- Issue comment、Issue assignment、label 或其他公开 GitHub 行为；
- 修改 registry 或初始化正式 contribution record，除非另有明确 User approval。

`approval_required: true` 只表示任务包含受保护动作，不能替代
`APPROVAL.yaml`。Target repository binding 也不授予 upstream write 或 PR 权限。

## Repository 管理

`repositories/registry.yaml` 是 target repository 配置；
`scripts/repository_discovery.py` 负责发现本地仓库；
`agent-work/bindings/` 保存 branch、HEAD、remote、upstream、fork、identity
和 working-tree 快照。不得把绝对本地路径写入 registry。

上游仓库和 facts repository 是两个独立 Git 仓库。任何 upstream fetch、修改、
commit、fork Push、PR 或公开行为都必须单独核验和单独获得用户授权。

## 启动顺序

1. 读取 `AGENTS.md`、`HANDOFF.md`、`agent-protocol/` 和当前 `REQUEST.yaml`。
2. 检查当前仓库 branch、remote、HEAD 和 worktree。
3. 运行 `python3 scripts/validate_agent_protocol.py`。
4. 运行 `python3 scripts/agent_queue.py next --agent <assigned-agent>`。
5. 只执行一个 ready 任务，只写入当前 Agent 拥有的路径。
6. 运行任务规定的测试和校验，写入 `RESULT.yaml`、`REPORT.md`，需要时写入 `DECISION.yaml`。

没有结构有效的 REQUEST、目标不清楚、权限越界、来源不明的本地修改或跨仓库
范围冲突时，停止并记录阻塞，不自行扩大任务。

## 事实与决策边界

Evidence、source facts、technical analysis、inference 和 decision 必须分开记录。
Evidence completed 不等于 admission、selected 或 implementation authorization。
Candidate Admission、registry mutation、正式 Issue 初始化和 implementation
都必须由独立任务和明确 User decision 授权。

Repository binding、target repository、evidence 和 screening 是保留的独立能力，
不改变公开操作权限。

## Candidate Discovery 去重

`scripts/discover_github_issues.py` 默认读取并排除本地已知 Issue：正式记录的
`issues/*/STATUS.yaml`、任务的 `agent-work/tasks/*/REQUEST.yaml` 以及
`screenings/` 下的结构化证据。Evidence-only 只标记为 `known-evidence`，不等于
pass 或 not-actionable；已结束状态和明确终止分类才使用 terminal 排除原因。
排除来源和原因必须写入发现结果。需要显式复查历史候选时使用
`--include-known`，不得通过删除事实记录绕过去重规则。

`discovery/<owner>-<repo>/INDEX.yaml` 是候选发现的增量审计缓存，按远端
`updated_at` 复用已完成的 API 审计；`scans/` 保存每次扫描的完成或中断状态。
它不产生 screening classification，也不替代正式 Issue、任务或 screening 记录。
Discovery 只从这些正式记录单向读取排除信息；Ledger 与 Issue 分析状态不做双向
同步。Ledger 中的 `no_known_related_pr` 只表示本次 API 审计事实，不表示 pass、
available、Admission 或 implementation authorization。

## 模型 profile

Luna、Terra、Sol 的 profile 是工作建议，不是运行时模型路由。当前会话不会因为
`assigned_agent` 自动切换真实底层模型；需要切换时由运行环境选择对应 profile。

建议：记录/筛选使用 Luna，实现/测试使用 Terra，高风险架构和最终技术判断使用 Sol。
阶段完成后必须查看 handoff 提示并按推荐 Agent 手动切换；协议不会自动切换真实底层模型。未切换到推荐 Agent 时，不得执行下一阶段。

## 公开沟通

所有公开内容代表 User 的 GitHub 身份。发布前必须重新核验目标、内容、授权和
authenticated identity。没有明确 User approval 时，只能生成内部 draft，不能发布。

## 完成条件

阶段完成必须记录：变更、事实来源、测试命令和结果、限制、branch/HEAD/worktree、
commit 和 Push 状态。Pull Request 阶段只有在 User approval 后才能执行 target fork
Push、创建 PR 或其他公开动作。

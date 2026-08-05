# zhaiyezi

zhaiyezi 是一个 repository-agnostic 的开源 Issue 研究与贡献记录系统。它保存候选、证据、分析、决策和受控执行的可恢复事实，不把任何单一上游项目或模型当作默认前提。

## 当前工作模式

系统采用 Codex Multi-Agent Workflow：

- Luna：候选发现、证据采集、筛选和决策提案；
- Terra：Deep Audit、源码分析、计划、实现和测试；
- Sol：架构、并发和困难调试的升级审查。

角色是任务契约中的权限边界，不是模型自动路由器。实际使用哪个模型由运行环境或用户选择；`assigned_agent` 只决定任务责任与可执行动作。

当前生命周期为：

```text
candidate → evidence → analysis → decision → implementation → pull-request
```

筛选结果只是推荐，不会自动进入贡献任务。用户确认后再创建下一份有界任务；`DECISION.yaml` 仅用于独立决策 Gate，`APPROVAL.yaml` 只由 User 产生，并且不会扩大上游写入或公开 GitHub 动作权限。

## 任务与事实

任务固定在 `agent-work/tasks/<task-id>/`。最小任务只需 `REQUEST.yaml` 和 `RESULT.yaml`；`REPORT.md`、`DECISION.yaml` 和 `APPROVAL.yaml` 按任务需要生成。角色定义在 `agents/`，权限目录在 `agent-protocol/permissions.yaml`，协议约束在 `agent-protocol/`。

模型不会自动切换。`assigned_agent` 只表示权限和任务归属；下一阶段必须创建新的有界任务，不要求额外交接文件。

仓库职责保持分离：`repositories/` 管理目标仓库绑定与发现；`discovery/` 保存扫描缓存；`issues/` 保存正式 Issue 研究事实；`agent-work/` 保存有界任务结果。新的 screening 不再复制到 `screenings/`。上游源码不属于本仓库。

Discovery Ledger 与 Issue 分析状态也保持分离。Ledger 只回答“脚本何时扫描了
什么、远端是否变化、审计结果能否复用”；`agent-work/` 和正式 `issues/` 才回答“是否正在分析、是否已排除、下一步是什么”。Discovery 只
单向读取这些本地记录来跳过已知 Issue，不把 Ledger 结果同步回正式状态，也不把
`no_known_related_pr` 自动解释为可贡献或已通过筛选。

## 启动与验证

```bash
python3 scripts/validate_agent_protocol.py
python3 scripts/agent_queue.py list
python3 scripts/agent_queue.py next --agent agent:luna
python3 scripts/agent_queue.py next --agent agent:terra
```

使用 `.agents/skills/screen-open-source-issue/` 执行候选、证据或筛选任务，使用 `.agents/skills/harvest-open-source-issue/` 执行已接纳 Issue 的贡献阶段。每次任务都必须有明确范围、输出和权限；没有有效任务时只恢复状态，不自行扩展调查。

正式 `issues/<slug>/` 记录可以有比轻量任务更严格的文档要求；这不改变任务协议，也不要求每个筛选候选建立正式 Issue 目录。

## 安全边界

默认允许读取、分析、写事实和受限本地测试。上游代码修改、目标 Fork Push、PR、Issue、评论、标签、认领以及其他公开 GitHub 行为都需要独立的 User approval。任何批准都只覆盖精确记录的 actor、action、repository、branch 和 path。

facts repository 的本地 Commit 与上游代码仓库的 Commit 是两个独立边界；不得把上游源码或补丁提交到本仓库。同步上游只能针对已核验的官方 remote，并遵守干净工作树、fast-forward 和非破坏规则。

## 参考

- [AGENTS.md](AGENTS.md)：仓库级协作与安全规则；
- [agent-protocol/README.md](agent-protocol/README.md)：任务协议总览；
- [agents/](agents/)：Agent 角色；
- [repositories/](repositories/)：目标仓库 Registry、Discovery 和 Binding；
- [scripts/discover_github_issues.py](scripts/discover_github_issues.py)：只读候选发现。

候选发现默认会读取正式 Issue、任务和筛选 Evidence，排除已经知道或正在处理的
Issue，并在输出中保留排除来源。每次扫描还会把已完成的审计结果保存到按仓库分组的
`discovery/<owner>-<repo>/` Ledger；远端 `updated_at` 不变时，下次会复用结果而不再
请求 Timeline、评论和 PR 搜索。使用 `--include-known` 才会显式包含本地已知 Issue。

### 候选发现用法

需要先提供只读 GitHub Token：

```bash
export GITHUB_TOKEN=...
python3 scripts/discover_github_issues.py \
  --repository LMCache/LMCache \
  --limit 50 \
  --include-label "good first issue" \
  --exclude-label "needs-triage" \
  --output candidates.json \
  --summary-output candidates.md
```

默认会排除 zhaiyezi 已知或正在处理的 Issue。`--include-known` 只在需要显式包含
本地已知 Issue 时使用；`--rescan-known` 会强制重新审计 Ledger 中远端未变化的结果。
`--output -` 输出完整 JSON，`--summary-output -` 输出候选摘要；两者不能同时使用
标准输出。默认 Ledger 根目录为 `discovery/`；`--no-ledger` 可用于不读写 Ledger 的
一次性运行。为避免漏掉未更新 Issue 后出现的关联 PR，未变化结果最多复用 7 天；可用
`--refresh-after-days N` 调整，`0` 表示每次都重新审计。脚本只读 GitHub，不认领
Issue、不修改标签、不评论。

`--workers` 控制 Issue 详情、Timeline 和 PR 证据审计的并发数，范围为 `1–8`，
默认值为 `2`：

```bash
# 串行运行，适合调试或严格控制请求压力
python3 scripts/discover_github_issues.py \
  --repository LMCache/LMCache --limit 10 --workers 1

# 有界并发，适合常规批量发现
python3 scripts/discover_github_issues.py \
  --repository LMCache/LMCache --limit 20 --workers 2
```

增大 `--workers` 只会并发 Issue 审计工作；所有 GitHub API 端点都有全局节流，
Search API 还会使用更慢的单独节流。二级限流会按至少 60 秒的退避重试；已完成的
单个 Issue 审计会立即写入 Ledger，因此中断后可恢复。遇到 GitHub 限流时，应等待并
降低到 `1` 或 `2`，而不是反复重跑。

因此，`--workers` 是审计任务槽位，不是绕过 GitHub 限流的请求并发数。脚本输出中的
`execution.audit_workers` 会记录所用槽位，`execution.api_request_pacing: global`
表示所有 API 请求仍被统一节流。对纯 API 工作负载，`--workers 2` 通常已经足够。

Ledger 采用分层保留：`no_known_related_pr` 的候选保留完整审计信息；
`related_pr_found` 只保留 Issue、状态和关联 PR 编号；`insufficient_evidence`
只保留 Issue、状态和限制。这既支持下次增量判断，又避免大量已排除 Issue 膨胀文件。

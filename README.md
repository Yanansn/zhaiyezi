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

Candidate Admission 是独立 Gate，不是自动状态转换。`DECISION.yaml` 是决策提案；`APPROVAL.yaml` 只由 User 产生，并且不会授权上游写入或公开 GitHub 动作之外的额外范围。

## 任务与事实

任务固定在 `agent-work/tasks/<task-id>/`，通过 `REQUEST.yaml`、`RESULT.yaml`、`DECISION.yaml` 和必要的 `APPROVAL.yaml` 推导队列状态。角色定义在 `agents/`，权限目录在 `agent-protocol/permissions.yaml`，协议约束在 `agent-protocol/`。

仓库职责保持分离：`repositories/` 管理目标仓库绑定与发现；`screenings/` 保存轻量筛选记录；`issues/` 保存正式 Issue 研究事实；`agent-work/` 保存有界任务结果；`decisions/` 保存决策提案。上游源码不属于本仓库。

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

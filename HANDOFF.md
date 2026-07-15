# 摘叶子当前交接

## 项目目标

以真实开源 Issue 为学习入口，完成“筛选 → 理解 → 代码地图 → 方案 → 实现 → 测试 → PR → Review → 复盘”的贡献闭环。

## 工作系统

- 通用 Skill：`harvest-open-source-issue`
- 项目规则：`AGENTS.md`
- Issue 登记：`registry/issues.yaml`
- 活动任务记录：`issues/kubernetes-kubernetes-140523/`
- 外部事实来源：GitHub

## 当前活动任务

- Issue：`kubernetes/kubernetes#140523`
- 标题：`EvictionRequest: add CRUD tests for conformance`
- 记录状态：`awaiting-triage`
- 推荐结论：`promising`
- 工作分支：尚未创建
- Pull Request：尚未创建

## 已完成

- 创建并安装通用开源 Issue 贡献 Skill。
- 建立项目事实库、状态模型和 Issue 记录模板。
- 读取并记录 Issue 正文、标签、认领状态和现有讨论。
- 完成初步筛选：Issue 范围看起来集中，但尚未获得 `triage/accepted`。
- 未公开留言、未认领 Issue、未修改 Kubernetes 代码。

## 当前阻塞与风险

- Issue 仍处于待 SIG triage 状态。
- 尚未调查 Kubernetes conformance API operation 测试的真实代码路径。
- 在代码地图和维护者确认前，不应开始大规模实现。

## 下一步

1. 重新核验 Issue 的实时状态及关联 PR。
2. 阅读 Kubernetes 的贡献、测试和 conformance 规范。
3. 定位 `pending_eligible_endpoints.yaml`、`getLifecycleAPIGroup` 和类似 subresource 测试。
4. 建立 `CODE-MAP.md`，详细解释 Eviction API 与测试记录机制。
5. 形成可供维护者确认的精确实现方案。

## 新上下文恢复指令

新主 Agent 必须先执行 `AGENTS.md` 的恢复顺序，并报告：

- 项目记录中的状态
- GitHub 当前实时状态
- 两者是否存在差异
- Git 分支及未提交改动
- 当前阻塞和建议下一步

完成恢复报告前不得直接编码或执行外部操作。

## 最近检查

- 项目记录日期：2026-07-14
- 初始项目提交：`1c77ba5 chore: initialize zhaiyezi workflow`

# Ubuntu Codex 本地接管

## 目标

让 Ubuntu 上的 Codex 成为《摘叶子》的阶段化工程执行 Agent。普通 Chat 负责筛选、教学和方案讨论；Codex 根据每阶段一份 `Execution Brief` 使用本地代码、Git、SSH、构建和测试环境完成明确交付物。

## 解压与检查

下载最终压缩包后执行：

```bash
mkdir -p ~/projects/zhaiyezi
tar -xzf zhaiyezi-codex-ready.tar.gz -C ~/projects
cd ~/projects/zhaiyezi

git status -sb
git log --oneline -5
git remote -v
```

压缩包包含 `.git` 历史，不需要重新执行 `git init`。

## 设置 GitHub 远程

项目计划使用：

```text
git@github.com:Yanansn/zhaiyezi.git
```

检查并设置：

```bash
git remote set-url origin git@github.com:Yanansn/zhaiyezi.git
git remote -v
```

不要在不确认当前账号具有写权限时 Push。

## 启动 Codex

在仓库根目录运行：

```bash
codex
```

第一次接管或开始新阶段时发送：

```text
按照下面的 Execution Brief 执行。
先读取 AGENTS.md 和 HANDOFF.md，使用仓库级
$harvest-open-source-issue Skill，核验事实、当前分支、提交、远程地址和未提交改动后再开始。

<粘贴普通 Chat 生成的 Execution Brief>
```

## 预期恢复结果

Codex 应报告：

- 简报指定的 Issue、阶段、目标和交付物
- 项目记录与 GitHub 实时状态
- 当前分支、提交、远程地址和未提交改动
- 差异、阻塞和审批边界
- 本阶段准备执行的精确动作

如果报告与 `HANDOFF.md` 或 GitHub 实时状态不一致，应先修正事实记录，不得直接实现。

## 日常使用

以后每个阶段只需在仓库根目录启动 Codex，并粘贴一份简报：

```text
按照下面的 Execution Brief 执行。
先读取 AGENTS.md 和 HANDOFF.md，核验事实后再开始。

<Execution Brief>
```

Codex 必须按照 `AGENTS.md` 恢复，不依赖旧聊天记忆，也不得把单阶段简报扩展为全面研究任务。

完成后，在简报已经授权 Push 的前提下，将事实记录推送到公开的 `Yanansn/zhaiyezi`。普通 Chat 随后通过 GitHub Connector 读取结果。

## 发布边界

Codex 可以在简报范围内自动完成只读调查、本地修改、测试和项目记录。以下操作必须在简报中明确授权，或执行前由用户另行确认：

- 上游 Issue/PR 公开评论
- 认领 Issue
- Git Push
- 创建或关闭 PR
- 请求 Reviewer、合并或关闭上游任务

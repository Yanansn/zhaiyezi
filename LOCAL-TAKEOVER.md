# Ubuntu Codex 本地接管

## 目标

让 Ubuntu 上的 Codex 成为《摘叶子》的唯一主 Agent，直接使用本地代码、Git、SSH、构建和测试环境完成开源 Issue 贡献闭环。

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

第一次接管时发送：

```text
读取 AGENTS.md 和 HANDOFF.md，使用仓库级
$harvest-open-source-issue Skill 恢复《摘叶子》当前任务。

先核验 GitHub 实时状态、当前分支、提交和未提交改动，
然后报告记录状态、实时状态、差异、阻塞和下一步。
在我确认恢复报告前，不要开始编码或执行外部写操作。
```

## 预期恢复结果

Codex 应报告：

- 活动 Issue：`kubernetes/kubernetes#140523`
- 记录状态：`awaiting-triage`
- 尚未修改 Kubernetes 上游代码
- 尚未公开认领或留言
- 下一步是核验上游状态、阅读贡献规范并建立代码地图

如果报告与 `HANDOFF.md` 或 GitHub 实时状态不一致，应先修正事实记录，不得直接实现。

## 日常使用

以后只需在仓库根目录启动 Codex，并说：

```text
恢复《摘叶子》并继续当前任务。
```

Codex 必须按照 `AGENTS.md` 恢复，不依赖旧聊天记忆。

## 发布边界

Codex 可以自动完成只读调查、本地修改、测试和项目记录。以下操作执行前必须由用户确认：

- 上游 Issue/PR 公开评论
- 认领 Issue
- Git Push
- 创建或关闭 PR
- 请求 Reviewer、合并或关闭上游任务

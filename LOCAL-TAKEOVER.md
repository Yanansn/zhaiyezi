# Ubuntu Codex 本地接管

## 目标

让 Ubuntu 上的 Codex 成为《摘叶子》的阶段化工程执行 Agent。普通 Chat 负责筛选、教学和方案讨论；Codex 根据每阶段一份 `Execution Brief` 使用本地代码、Git、SSH、构建和测试环境完成明确交付物。

## 进入仓库并检查

对于已经 clone 或已经从压缩包恢复的仓库，先进入现有目录并检查状态：

```bash
cd ~/projects/zhaiyezi
git status -sb
git log --oneline -5
git remote -v
```

若目录来自压缩包，必须确认其中包含 `.git` 历史；不要在已有仓库中重新执行 `git init`。

## 多仓库本地目录建议

```text
~/projects/
├── zhaiyezi/
└── upstream/
    └── <project>/
```

`zhaiyezi` 从自己的 `main` 读取和更新事实；真实上游代码使用独立 Clone。不要把上游 Clone 放进 `zhaiyezi`，避免嵌套 Git 仓库导致误暂存或误提交。

每个阶段开始时分别核验：

```bash
cd ~/projects/zhaiyezi
git status -sb
git log -1 --oneline
git remote -v

cd ~/projects/upstream/<project>
git status -sb
git log -1 --oneline
git remote -v
```

## 设置 GitHub 远程

单一 GitHub SSH 身份环境可以使用：

```bash
git remote set-url origin git@github.com:Yanansn/zhaiyezi.git
git remote -v
```

当前 Ubuntu 是多 GitHub 身份环境，必须使用 SSH Host 别名：

```bash
git remote set-url origin git@github-yanansn:Yanansn/zhaiyezi.git
ssh -T git@github-yanansn
git remote -v
```

预期 `ssh -T` 显示实际认证身份为 `Yanansn`。不得仅根据私钥文件名推断 GitHub 身份，必须以该命令的实际输出为准。不要在项目文档中写入私钥内容，也不要由 Codex 修改用户的 `~/.ssh/config`。

不要在没有核验实际身份和写权限时 Push。

## 上游项目 remote 结构

推荐在上游项目 Clone 中使用：

```text
origin    用户 Fork，可在授权后 Push 工作分支
upstream  官方仓库，用于只读同步和确定 PR base
```

例如：

```text
origin    git@github-yanansn:Yanansn/kubernetes.git
upstream  https://github.com/kubernetes/kubernetes.git
```

`origin` 不应错误指向官方仓库，除非用户确有官方写权限且项目流程明确要求。默认只把工作分支 Push 到用户 Fork，PR 的 base 指向官方仓库分支。不要 Force Push，除非用户明确授权且已判断不会破坏 Review。

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
- facts repository、upstream working repository 和 PR 各自的状态

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

阶段结束时必须说明哪些内容已经 Push、哪些仍仅在本地；未 Push 的文件和命令结果不会自动出现在普通 Chat 中。完整回传要求见 Execution Brief 模板。

## 发布边界

Codex 可以在简报范围内自动完成只读调查、本地修改、测试和项目记录。以下操作必须在简报中明确授权，或执行前由用户另行确认：

- 上游 Issue/PR 公开评论
- 认领 Issue
- Git Push
- 创建或关闭 PR
- 请求 Reviewer、合并或关闭上游任务

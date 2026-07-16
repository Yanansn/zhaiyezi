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

实际 remote 名称可以不同。开始前必须结合 `git remote -v` 中的仓库地址确认哪个是官方仓库、哪个是用户 Fork，不能凭 `origin` 或 `upstream` 名称猜测。

## 安全同步上游基础分支

涉及真实上游代码的阶段开始时，在上游 Clone 中先执行：

```bash
git status -sb
git branch --show-current
git remote -v
git log -1 --oneline
git fetch --prune upstream
```

`git fetch` 必须由本轮 Execution Brief 明确授权。fetch 后核验官方默认开发分支是 `main`、`master` 还是其他名称，并记录：

```bash
git rev-list --left-right --count <local-base>...upstream/<base>
git rev-parse <local-base>
git rev-parse upstream/<base>
git merge-base <working-branch> upstream/<base>
```

`git rev-list --left-right --count` 的第一个数字是本地基础分支独有 Commit 数，第二个数字是官方基础分支独有 Commit 数：

- `0 0`：一致；
- `0 N`：本地 behind，可考虑 fast-forward；
- `N 0`：本地有独有提交，停止自动同步；
- `N M`：已经 diverged，停止自动同步。

只有以下条件同时成立时，才可自动同步：工作树干净、本地基础分支没有独有提交、没有 diverge、同步可 fast-forward，并且简报允许本地基础分支同步。使用明确的官方 remote 和分支：

```bash
git switch <base>
git merge --ff-only upstream/<base>
```

不要使用无参数 `git pull`。它可能从用户 Fork 拉取，行为还会受 `pull.rebase` 等本地配置影响，并可能产生 merge Commit 或改写历史。

若工作树不干净、本地基础分支有独有提交、双方 diverge、remote 与记录不符、官方默认分支无法确认、当前分支有未识别提交、fetch 失败或无法 fast-forward，立即停止并报告。不得静默执行：

```bash
git reset --hard
git clean -fd
git stash
git rebase
git checkout -- .
git restore .
git branch -D <branch>
git push --force
git push --force-with-lease
```

这些动作只有在简报针对具体仓库、具体分支和具体动作明确授权时才可执行。

### 工作分支与基础分支分开处理

尚未创建工作分支时，从已核验的最新官方基础分支创建：

```bash
git switch -c <working-branch> upstream/<base>
```

工作分支存在但还没有实际提交时，也必须确认没有本地工作并取得重新创建或调整分支的明确授权。工作分支已有提交时，不得因为基础分支更新而自动 merge 或 rebase；先报告工作分支 Commit、官方 base Commit、ahead/behind、merge-base、冲突风险、PR 状态及是否会改写已 Push Commit，再由新简报决定暂不更新、merge、rebase 或重新创建。

PR 已创建时，默认不主动 rebase 或 Force Push。只有上游明确要求、CI 因基线过旧失败、出现冲突、项目规则要求保持最新或用户明确要求时，才提出更新建议。

### 同步事实仓库

开始阶段时也要单独检查 `zhaiyezi`：

```bash
cd ~/projects/zhaiyezi
git status -sb
git fetch --prune origin
git rev-list --left-right --count main...origin/main
```

只有工作树干净、本地没有独有提交、可以 fast-forward 且简报允许时，才执行：

```bash
git switch main
git merge --ff-only origin/main
```

不得自动 reset、stash 或覆盖尚未发布的事实记录。

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

所有社区公开内容都代表用户本人，并额外遵守 [Public Communication Contract](.agents/skills/harvest-open-source-issue/references/public-communication.md)：先生成 Draft，经普通 Chat 技术 Review，再等待用户对具体公开动作明确授权。完成或 Push Draft 不等于授权发布；Execution Brief 默认允许准备草稿、禁止发布、回复或更新既有公开内容。

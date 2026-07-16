# Knowledge

## 为什么需要这些知识

这个 Issue 同时涉及 Kubernetes 存储对象、CSI 驱动和 E2E 测试生成。只看测试名称，很容易把“访问模式”“卷模式”“文件系统”和“后端存储实现”混成同一件事。下面只解释读懂本 Issue 所需的背景；TestPattern 全量清单属于源码事实，保留在 [CODE-MAP.md](CODE-MAP.md#filesystem-and-testpattern-inventory)，根因判断保留在 [ANALYSIS.md](ANALYSIS.md)。

## 从 Pod 到存储卷

Pod 中的容器文件系统通常跟随容器生命周期。需要持久保存或让多个 Pod 访问的数据，会通过 Volume 挂进容器。

对持久卷，常见关系是：

```text
Pod
  │ 引用
  ▼
PVC（PersistentVolumeClaim，使用者提出的存储申请）
  │ 绑定
  ▼
PV（PersistentVolume，集群中可用卷的表示）
  │ 指向
  ▼
CSI Driver 管理的真实存储
```

- **PVC** 描述“我要多大的卷、怎样访问”。Pod 通常引用 PVC，而不是直接了解真实磁盘或共享服务。
- **PV** 是 Kubernetes 对已经存在或已经创建出来的卷的记录。
- **StorageClass** 是动态创建卷时使用的配置模板，通常包含 provisioner（由哪个驱动创建）和参数。
- **Dynamic Provisioning（动态供应）** 指 PVC 出现后，控制器根据 StorageClass 调用驱动创建卷，再产生并绑定 PV。与之相对，Pre-provisioned PV 是管理员或测试事先准备好的 PV。

简化流程是：

```text
PVC + StorageClass
→ external provisioner / CSI Driver
→ 创建真实卷
→ 创建 PV
→ PVC 与 PV 绑定
→ kubelet 请求 Driver 把卷提供给 Pod
```

## CSI 与 CSI Driver

CSI（Container Storage Interface）是一套存储插件接口。Kubernetes 通过它请求创建、删除、挂载或扩容卷；具体怎样调用云盘、SAN、NAS 或其他存储系统，由 CSI Driver 实现。

“驱动支持 RWX”和“驱动支持 ext4”都是能力描述，但未必描述同一种存储产品或同一个 StorageClass。例如，同一个驱动可能既管理块存储，也管理共享文件服务。仅有两个独立的全局布尔值或集合，未必能表达“哪个文件系统与哪个访问方式可以组合”。

## VolumeMode 与 AccessMode 是两条不同的轴

**VolumeMode** 决定 Pod 得到什么：

- `Filesystem`：节点把卷格式化或识别成文件系统，容器得到一个挂载目录；PVC 未指定时通常采用此默认值。
- `Block`：容器得到原始块设备，不经过文件系统挂载。

**AccessMode** 描述 PVC 请求的访问方式：

- `RWO`（ReadWriteOnce）：可由一个节点读写。
- `ROX`（ReadOnlyMany）：可由多个节点只读。
- `RWX`（ReadWriteMany）：可由多个节点读写。
- `RWOP`（ReadWriteOncePod）：整个集群中限制为一个 Pod 读写。

AccessMode 是调度、绑定和驱动能力契约的一部分，不表示某种文件系统。`RWX + Filesystem` 可以是合理组合，例如多个节点通过 NFS 或 SMB 客户端访问同一个共享服务；`RWX + ext4` 是否合理，则取决于“ext4”描述的是客户端实际挂载的文件系统，还是共享服务内部看不见的后端实现。

## 本地文件系统与共享文件系统

`ext3`、`ext4`、`xfs` 是常见 Linux 文件系统，`ntfs` 常见于 Windows。它们通常用于一个主机拥有并挂载的块设备。普通用法下，它们没有让多个独立主机同时写同一个块设备所需的分布式协调机制。

NFS、SMB/CIFS、CephFS 等共享文件系统把多客户端协调放在服务器或分布式协议中。服务器自己的磁盘可能使用 ext4，但客户端看到和挂载的是 NFS：

```text
客户端节点 A ─┐
              ├─ NFS/SMB 协议 → 文件服务器 → 服务器内部可能使用 ext4
客户端节点 B ─┘
```

这不同于：

```text
节点 A ─ ext4 挂载 ─┐
                    ├─ 同一个普通块设备
节点 B ─ ext4 挂载 ─┘
```

因此不能笼统地说“RWX 后端永远不能使用 ext4”。需要区分后端内部格式和 Kubernetes 节点被要求直接挂载的客户端文件系统。某些集群文件系统也可能支持多主机协调，所以“所有非空 FsType 都不支持 RWX”同样不是普遍定律。

## Storage E2E 怎样组合测试

- **Test Suite** 是一组围绕某类行为的测试；`multiVolume` 关注多个 Pod、卷、快照或克隆之间的组合行为。
- **Test Case** 是 suite 中一个具体断言，例如两个 Pod 是否能访问同一个卷。
- **TestPattern** 是可复用的一组输入，例如 DynamicPV、显式 ext4、Filesystem 模式。Suite 会把选中的 Pattern 与它的 Test Case 组合。
- **Capability** 是驱动声明的能力，例如是否支持 RWX。测试运行时用它判断某个 case 是否应该继续。
- **SupportedFsType** 是驱动声明支持的文件系统字符串集合。空字符串 `""` 表示测试框架不显式选择文件系统，把默认选择留给驱动或 StorageClass；它不表示最终卷一定没有文件系统。

可以把生成过程想成一个“笛卡尔积”（两个集合的所有配对）：

```text
Suite 的 Test Cases × Suite 选中的 TestPatterns
                     │
                     ▼
              注册出多个测试名称
```

但注册不等于执行：

```text
注册测试和生成名称
→ 开始运行该测试
→ 检查 Driver 接口、Capability、SupportedFsType 和平台
→ 不支持则 Skip
→ 支持才创建 StorageClass / PVC / PV / Pod
```

因此日志中出现 `[Testpattern: Dynamic PV (ext4)]` 只能证明该组合被注册；还要查看 Skip 条件才能判断它是否真正运行。另一方面，`TestPattern.Name` 和 `TestPattern.FsType` 是两个字段：名称用于显示，非空 FsType 还可能进入资源构造。对动态 CSI 路径，测试框架可把它写入 StorageClass 的 `csi.storage.k8s.io/fstype`，所以本 Issue 中的 `ext4` 不能只按名称装饰理解。

## 重要区别与常见误解

- `Filesystem` 是卷模式，`ext4` 是一种具体文件系统；二者不是同义词。
- `RWX` 是访问模式，不承诺任何文件系统都能安全地实现多节点写入。
- 驱动“支持 ext4”和“支持 RWX”分别为真，不自动证明 `ext4 + RWX` 这个组合为真。
- 源码中命名的 Pattern 集合、某个 suite 当前选择的 Pattern 集合、外部驱动理论上可声明的字符串集合是三个不同集合。
- `FsType == ""` 表示框架不覆盖默认值，不等于“没有文件系统”。
- 测试名称被注册不等于测试通过、失败或实际创建了资源；它仍可能在运行时 Skip。

## 本 Issue 使用的术语

| 术语 | 在本 Issue 中的含义 |
|---|---|
| `multiVolume` | 注册相关 TestPattern 并包含跨节点并发访问 case 的 Storage E2E suite。 |
| `DynamicPV` | 通过 StorageClass 和驱动动态创建 PV 的 Pattern 类型。 |
| `CapRWX` | 驱动元数据中表示支持 ReadWriteMany 的能力。 |
| `SupportedFsType` | 驱动声明可运行哪些 FsType Pattern 的开放字符串集合。 |
| `csi.storage.k8s.io/fstype` | 动态 CSI StorageClass 中用于传递显式文件系统请求的参数。 |
| Skip | 测试已经注册，但因驱动、Pattern、平台或能力不匹配而在运行时跳过。 |

## 参考资料

- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Kubernetes CSI Drivers](https://kubernetes.io/docs/concepts/storage/volumes/#csi)

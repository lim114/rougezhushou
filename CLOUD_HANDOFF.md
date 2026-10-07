# rougezhushou 云端交接

2026-10-06，从 Windows 项目 rouge 的 0.70.0 版本复制形成独立项目。原项目和当前本局记忆留在本机。

## 恢复开发

后续开发统一在 `codex/p2-development` 分支进行。开始修改前检查当前分支，沿用现有工作目录并保留本地改动。最新连续开发断点见 `DEVELOPMENT_CHECKPOINT.json`、`WORK_IN_PROGRESS.md` 顶部及 `BATCH_CONTINUOUS_P2.md`；每节提交，每五节全量可用测试。P2 完成后继续 P3，同问题三次失败则搁置。Wine 兼容验证已获授权，原生 Windows 状态单独记录。此前批次见 `BATCH_CLOUD_P2_S1_BINDING.md`；其验证范围是 Linux 计算与报告，不代表 Windows 实机验收。

先读取 AGENTS.md、PROJECT_PROGRESS.md，以及 WORK_IN_PROGRESS.md 顶部的 0.70 交接。当前先做 P2，未完成 P1 保留；识别优化放在所有其它事项之后。不要根据旧交接改变当前优先顺序，不重新做已验证项。已完成范围在 PROJECT_COMPLETED.md。

本项目仅做局外计算、建议及 Windows 后台只读采样。禁止操作游戏、分析实时站位、发送聊天或建立定时任务。不能伪造概率、机制证据或完成状态。未知机制先查已有研究，再查固定原始资料和新来源。

## 安装和验证

云端使用 Python 3.12 或更新版本。安装及计算回归：

```bash
bash scripts/cloud_setup.sh
```

这套精选计算回归不加载 tests/test_enemy_environment.py 的个人游戏截图识别场景，也不加载 Windows 界面/采样及历史图像回放测试；完整本机回归仍需原工作目录及 requirements.txt。历史战斗触发测试保留其原有退役标记。

已有环境重新验证：

```bash
.venv/bin/python scripts/verify_cloud.py
```

Windows 完整依赖仍由 requirements.txt 安装，界面入口仍为 run.cmd。Linux精选依赖没有 Windows 专属采样库；用户授权的Wine兼容环境已独立安装真实Windows依赖，见 WINDOWS_COMPATIBILITY.md 和 verification/full-005。不要用导入占位、虚假成功或跳过错误来冒充 Windows 实机验收。手机可以继续查看、修改代码并运行计算测试；Windows 游戏画面采样、客户端聊天管道和最终界面验收需回到本机执行。

## 证据与迁移边界

CLOUD_SOURCE_MANIFEST.json 记录复制时公开源文件的哈希，状态仅代表本地准备，不代表云端已发布。保留了全部生产代码、数据/图标/地图、测试、工具、文档及非运行时验收记录。近期 0.66–0.70 研究证据按清单复制到原有 .cache/research 路径，提交时只显式加入清单中的证据文件。

未迁入私人配置、聊天绑定、当前本局记忆、游戏个人截图、虚拟环境、旧构建、游戏 DLL/资源包或其它缓存。因此历史回执中的本机路径可能在云端不存在；这些是当时验收记录，不是本次云端验收。完整历史/实机回放仍需原 Windows 工作目录，不要把缺少样本标成已通过。

0.70 的新增内容是酒神 S1 两段原版参考与相对段间等待。真实首伤/结束/阻回/普通攻击冷却相位仍未知，完整周期保持未知。不要用猜测补齐。其后待办以 PROJECT_PROGRESS.md 为准。

## 手机首条续接指令

读取 CLOUD_HANDOFF.md、AGENTS.md、PROJECT_PROGRESS.md 和 WORK_IN_PROGRESS.md 顶部，先运行 scripts/verify_cloud.py，然后衔接剩余 P2。机制未明先查原始证据；不操作游戏，不发送聊天，不清空本局记忆，不启动代理或定时任务。完成项从待办销项并记录到 PROJECT_COMPLETED.md。Windows 专属验证明确留给本机。

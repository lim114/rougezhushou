<!-- live-cloud-index:start -->
# 当前云端续接索引 · 第240节

已完成至240，后续241；本批状态 `IN_PROGRESS`。批次目标260。下次定期全量245。每节更新本入口和 CLOUD_INDEX.json 并随功能提交普通推送。

恢复时先核对远端 `codex/p2-development`、真实源码和 DEVELOPMENT_CHECKPOINT.json。当前待办仅在 PROJECT_PROGRESS.md；完成范围在 PROJECT_COMPLETED.md，逐节回执在 verification/sections/。当前产品要求与交付边界见 PROJECT_REQUIREMENTS.md，并随每节索引核对摘要、提交到同一分支。P2尚未全部完成；原生动作/结束时钟和当前游戏面板不能用公式参考代替验收。节点只列来源覆盖的候选与条件，不要求生成概率。

最新本机全量：`verification/full-230/native-after-repair.json`，可用范围全通过：`False`。Windows后台采样和聊天不等于云端验证；本批不操作游戏、不发送聊天。私人配置与本局记忆只保留本机。下面是历史交接，不代表当前节数。
<!-- live-cloud-index:end -->

## 本机与 GitHub 开发分支同步 · 2026-10-11

原 Windows `rouge` 工作目录已按用户新指令同步最新 `codex/p2-development` 并建立同仓库 upstream，源提交 `69497c98a17415ee4b635cef088e465aa6c9188c`。后续在该分支开发并普通推送；本机运行仍从原 `rouge/run.cmd` 启动。原始配置、账号/本局档案、聊天绑定及私人样本没有迁入公开仓库，也没有被云端旧状态覆盖。下文“独立项目/原项目保留”是2026-10-06初次迁移历史，当前已由本次源码同步接续。

同步与编码维护没有增加功能节数，仍140完成、后续141、下次定期全量155。实际本机精选计算通过，初次完整离线检查还保留12个失败断言；Windows窗口已实际查看，但未验证真实游戏采样或发送聊天。回执 `verification/local-sync-20261011/summary.json`；不能用旧云端范围替代本机缺口。

# 当前批次已完成至140 · 2026-10-11

从真实135接续，136–140交付五个可使用功能并逐节提交/普通推送；140到期全量保留原范围且补查126–140新增窗口，可运行范围通过。汇总BATCH_136_140_REPORT.md、verification/batch-136-140.json及verification/full-140/summary.json。后续141，下次全量155。缺迁移样本和声明跳过不算通过，Wine不是Windows实机/游戏/聊天。P2未完成，先核对真实Git/远端/源码，再读断点。私人状态不覆盖；95/109旧延期流程保留。

# rougezhushou 云端交接

用户最新要求（2026-10-11）：恢复最新远端开发分支并从第123节继续；为节约资源，每小节仅保留与实际改动直接相关的必要检查，无必要时省略，不重复运行已通过且源码未变的检查。全量测试范围不缩减。每完成一节立即commit保存，并沿用已授权的普通push。保留第125节全量检查，此后每15节一次（140、155……）。继续开发，旧“125后停止/不启动126”安排已被本次续接要求替代。每节仍须有实际功能成果，未知机制先查来源；95/109已延期的原流程不无故重试。


2026-10-06，从 Windows 项目 rouge 的 0.70.0 版本复制形成独立项目。原项目和当前本局记忆留在本机。

## 恢复开发

后续在 `codex/p2-development` 分支工作。启动任务可能落在旧main/work副本；先核对GitHub远端，再使用 `bash scripts/resume_development.sh` 恢复最新分支及可复用依赖。脚本保护已有修改，不重置或丢弃工作。当前断点以真实提交和源码、DEVELOPMENT_CHECKPOINT.json及WORK_IN_PROGRESS.md顶部共同核对，不能仅信索引。验证和提交按顶部2026-10-11要求执行；P2后P3、P1保留、识别最后。
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
# 2026-10-11追加：功能节必须推进待办

每节都必须有具有实际意义的功能成果，明确对应PROJECT_PROGRESS.md中的剩余工作、新增能力和验收标准。只修漏洞、测试、研究归档或更新文档不能单独算一节；并入相关功能节，或记录为维护提交而不增加功能完成节数。已提交的编号作为历史保留，不能因维护提交而宣称P2待办已推进或完成。

Wine检查使用 `bash scripts/wine_python.sh ...`：同一个Wine前缀中的Qt会话串行执行，并使用已安装的真实中文字体测试夹具，避免并行Xvfb会话相互影响。仍是兼容验证，不是Windows实机。

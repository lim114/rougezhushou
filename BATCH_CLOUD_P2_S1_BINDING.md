# 云端 P2：酒神 S1 束缚倍率的输出边界

开发分支：`codex/p2-development`。后续修改沿用此分支，见 `AGENTS.md`。当前工作仍先 P2，P1 留断点，识别最后。

## 问题与行为

0.70 的损伤研究已确认实际 S1 束缚模板通过 event 68 接收 SANITY 并乘 `ep_damage_scale`，同时明确首次附着、黑板初始化与刷新未闭合。原计算仍将每段基础损伤直接乘倍率，攻击力 1000、精二、潜能 1、S1 专三时给出两段法伤 3000 加爆发 6000 的确定总伤 9000。

本批取消默认倍率假设。在原版两段动作参考下，保留法伤小计 3000、每段未计束缚倍率的损伤基础参考 300、倍率参数 1.8 和束缚时间参数 3 秒；实际积累、爆发次数和完整总伤显示未知。基础参考不是当前目标实际积累。无目标、首击前的观察窗口、零攻击和损伤免疫不会凭空产生未知伤害。初动、基础属性、治疗、两段法伤及原版时间参考独立保留。

## 来源及边界

- 固定原始游戏表：`Kengxxiao/ArknightsGameData` commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。重新通过 HTTPS 获取 `skill_table`、`character_table`，与仓库原有 SHA256 完全一致。S1 描述明确限定“该次束缚期间”。
- 复用 `.cache/research/phatm2-damage-070/REPORT.md`、`native-proof.json` 及 `s1-unmove-template.json` 的默认原生模板、SANITY 回调和天赋数据流研究；本批只核对迁入的证据文件与原始表，没有执行游戏、读取内存或重新核验未迁入的 DLL/metadata。
- 来源记录：`research/p2-s1-binding/source-receipt.json`。未修改数值机制 JSON、原始资料或历史回执。
- 实际首次附着、黑板初始化/复制、刷新顺序、当前热更新和精确首伤/结束/阻回/普攻恢复仍未闭合；完整周期保持未知。本批完成的是软件输出边界，不是这些机制的最终核验。

## 验证

```bash
cd /workspace/rougezhushou
.venv/bin/python scripts/verify_cloud.py
.venv/bin/python -m unittest tests.test_report tests.test_offline_scope_030 tests.test_offline_relics_031
.venv/bin/python -m pip check
```

云端 226 项运行、225 通过、1 项既有跳过；另 34 项回归通过，依赖检查通过。新增 18 项覆盖首次/第二段窗口边界、无目标、目标消失、损伤免疫、已有爆发、零攻击、精英领袖阈值、等级/潜能参数、连续模式、河谷组合、报告及输入保留。

从分支起点的公开 `rouge` 包导出隔离基线，核对 32 档案、87 技能、3 个技能等级、2 种时序模式共 522 个情景。516 个其他技能完整结果一致；6 个 S1 情景改变未知保护相关输出，逐例检查法伤分项、基础属性和动作流不变，法伤小计等于基线法伤，不保留伪确定的爆发序列。不是新的实战数值对照，也不是历史 732 算例完整回放。

初轮相关测试保留于 `.cache/p2-s1-binding/targeted-initial.log`：失败主要来自旧 S1 确定爆发预期，另有一个浮点精确相等断言；已改为独立法伤/基础来源断言与明确未知状态，未移除动作/窗口校验，也未修改旧语料。随后云端扩展测试发现旧藏品算例同样直接套用 S1 倍率，现检查两个未计倍率的来源乘藏品系数，且不将损伤积累计入生命伤害。

当前机器验证见 `P2_S1_BINDING_VERIFICATION.json`。Windows 界面、游戏采样、私有图片回放和真实桌面聊天未运行。没有游戏操作、聊天发送、私态复制/恢复或定时任务。

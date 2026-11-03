# 前后成对面板校准

此能力推进 `PROJECT_PROGRESS.md` 的首批三人面板偏差排查。两组独立 `scenario` 与 `observation` 各自沿用 `compare_panel` 条件标识与字段校验；只对同一干员、同一面板层、同一证据类别的共同字段计算有符号的后减前。单侧字段不补零，模型未覆盖字段保留观察差，但模型差、残差与相符结论保持未知。

`examples.json` 是三组固定公开公式参考，观察数字以字面量保存，没有用模型输出填充观察值：

- 机械师：精二90、满信赖、潜能1、无模组。培养攻击573；贵族刺剑25%攻击符文写回后716；同层观察差143。
- 凯尔希·思衡托：生命2120、常态生命天赋25%；未知仪器50%生命符文先写回到3180，再乘常态天赋，2650→3975；同层观察差1325。
- 凛御银灰：声明在场14.9→15秒的常态防御天赋条件；同层防御497→557，观察差60。

来源复用固定原件 `Kengxxiao/ArknightsGameData` 提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，本仓库 `rouge/data/catalog.json`、`rouge/data/relic-mechanics.json` 及既有 `tests/test_calibration.py` 第151、152、156节对照。第236节回执 `verification/sections/236.json` 已证明原有模型诊断接口的实现范围；本节没有改变培养、符文、天赋、技能或数值机制。

```bash
.venv/bin/python research/p2-paired-calibration/reproduce.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.test_paired_calibration -v
```

当仅藏品声明变化时，联接第236节的共同背景、单件背景差及非相加模型残差；同时变化培养或其他条件时，不作单藏品联接。前后实际面板的绝对偏差分别显示，避免相同偏移在差值中抵消后误判已校准。零残差只说明声明算术相符，不推断丢弃后果、获取顺序、隐藏脚本、热更新、偏差原因或原生时钟。

`PairedCalibrationPanel` 是可接入实际工具窗口的 Qt 工作区。两端可分别读取条件分层、显式确认标识、导入当前干员条件及编辑独立观察记录。`set_scenario` 自动刷新只更新可导入的条件副本；读取分层、选中另一模板、切换端点均不覆盖观察来源或数值。只有显式载入模板才替换两端公开示例。验证使用公开样例，不加载私人运行状态、游戏或聊天。

三个例子均为 `formula_reference`，不是游戏观察；`public_case` 和 `game_panel` 仍需调用方独立记录来源。工具无论差值是否相符都保持 `native_verified=false` 与实际因果归属未知，真实客户端成对验收仍未完成。

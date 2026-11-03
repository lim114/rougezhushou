# 首批三人技能事件与回转成对核对

此能力推进 `PROJECT_PROGRESS.md` 的实际首出手、结束、解除阻回与重复周期校准，以及 `PROJECT_REQUIREMENTS.md` 的攻速/技力回转预计与实际成对核对。它接收独立来源的事件账本，测量时差、拆分开启等待和充能、显示重复周期变化；不从模型生成观察、不猜缺失时刻，也不把静态参数或公式参考升级为原生验收。

来源先复用既有规则：`rouge/operator_engine.py` 的 `Combat.calculate` 在首批九技能中输出 `initial_seconds`、`recharge_seconds`、`cycle_seconds`；`rouge/timing.py` 保留独立预览与未知原生绑定；`rouge/data/catalog.json` 固定原件提交为 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。新增接口没有改变数值机制。`compatibility_matrix.json` 只记录现有模型的九技能适用范围：机械师S2持续/周期未知；凯尔希S2与机械师S1弹药持续是模型估计而不是固定持续参数；凛御银灰S2有两充能，不自动视为每次开启后空池。

`timing_reference(scenario)` 导出同现有面板校准一致的上下文标识、精确干员/技能身份、来源、警告，以及三个明确口径的条件时钟：

- 初动：部署到首次技能就绪，首次开启前的手动等待另列。
- 回转：记录结束到下次就绪，只有充值需求声明符合当前模型时才比较；模型含相同 `scenario` 的额外阻回/硬直策略。
- 周期：开启到下次就绪。相邻两次开启包含后一次等待，单独显示，不将这段等待判为回技力误差。

`compare_timing_observation(scenario, observation, tolerance_seconds=0)` 要求每个事件有 `clock_id` 和 `value`，使用统一秒时钟或视频帧时钟。帧坐标按显式 FPS 换秒，拒绝跨时钟、单位混合、非有限数、错误身份/上下文、事件逆序、重复开启重叠、重复ID和不相符的首末边界。FPS不强制30；现有模型30Hz参考独立保留。

每周期可记录 `ready/start/first_release/last_release/end/unblocked/next_ready` 及 `release_stamps` 列表，未知填 `null`。连续完整的本体攻击释放可与现有条件计时间隔比较；抽样、本体命中、召唤物命中或变速模型只测量观察间隔。独立填写的 `attack_speed_attribute` 直接对照官方技能攻速参考，不从视频间隔反推攻速。

首次释放、实际结束、解除阻回与原生周期预测一律保持未知；原表固定持续参数、模型持续估计及名义间隔分别展示。多充能、预存或部分充能未声明符合模型需求时，测量值仍保留，回转/周期参考比较保持未知。重复变化与偏差不推断具体原因。

`examples.json` 保存三组字面量公式时钟：凯尔希S1初动7/回转35/周期70，银灰S3为5/55/103，机械师S3为10/35/75；分别额外声明首次等待2秒、第二次等待3秒。因此相邻开启间隔73/106/78，不能与模型周期混同。首末释放、解除阻回没有提供。示例是 `formula_reference`，不是游戏事件。

```bash
.venv/bin/python research/p2-timing-calibration/reproduce.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.test_timing_calibration -v
```

Qt `TimingCalibrationPanel` 提供独立条件和事件记录编辑、参考读取、显式标识确认与显式导入。自动刷新与模板选择不改观察；实际文本或容差改变会清除过期结果。来源与时间戳不会随读取预测自动填充。真正的游戏面板、原生动作绑定、当前热更新、自动采样和聊天仍未验收。

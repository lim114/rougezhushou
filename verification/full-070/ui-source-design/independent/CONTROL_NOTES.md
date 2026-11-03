# full070 独立控件合同初审

这是源码/公开合同的只读设计复核，不是 Wine、GUI、原生 Windows 或游戏验收。66–70 final 外部源包已查阅；root 当前 rolling checkout 未作为已冻结整组测试基线。

## 可通过真实 Qt 提交的断言

- 66 维什戴尔：ghost_count / ghost_casts 为真实 QSpinBox，默认 0，控件最大值分别 3 / 1000。设置 int 0/1/2 后，实际 button 提交的字段须 `type(value) is int`；ghost_count>0 时 metadata ghost_casts_requested 应为所提交 int，ghost_cast_times_seconds=None、ghost_full_cast_attribution_verified=False。ghost_count=0 时 ghost_casts 是 inactive query，metadata 仍为 0；不要把控件最大值说成新的原生人数/施放上限。
- 67 酒神：enemy_attack_count 为真实 QSpinBox，默认 0、控件最大 10000、S1/S2/S3 可见。正计数且原 pending 条件满足时，attacks_requested 是 int、buildup_per_attack=70、events_scheduled=False、attack_times_seconds=None。W0 的实际输出 0 仍可有 cast pending / window 非 pending；life0、100% 损伤免疫及精一无堕梦时没有 incoming reference。各模式完整输出可与其现有合法 int 控制比。
- 68 黍：three_professions、three_same_profession 为真实 QCheckBox，默认 False，S1/S2/S3 可见，实际 payload 必须是 bool。精二已选天赋分别保持 HP+12% / AS+12 原参数；精一真实可选 S1/S2、rank7、两旗标勾选应与未勾选整份结果相同。与 four_sui=True 组合时 4s/1SP 只保留原参数，自然 rate 不含 .25，实际 first/origin/reset/blocked/tick 时钟 None，完整资源回转未知。
- 69 凛御银灰：独立 MainWindow.cooperative 是 QCheckBox，只有 S3 可见；fragile 默认 True，coop 默认 False。双 bool 控件的实际 payload 须是 bool，合法 toggles 沿既有 conditional math。以训练精二、合法 rank 和固定其它参数对比原组件/报告，不能把复制的协同分项当作已核实实际覆盖、快照或事件 ownership。
- 70 黍：enemy_on_sown_tile 是 S3 专用 QCheckBox，默认 False，标签应精确为「存在地面敌人处于播种地块」。bool false/true 分别是当前情景声明；True 保留原 e_atk/e_attack_speed 条件静态参数。该存在条件可以来自其它地面敌人，不能要求当前伤害目标 groundtype=True，也不能从 ground/flying 元数据反推出此 checkbox。

## 必须保留的陷阱与范围

1. QSpinBox 不能提交任意 decimal/exponent str 或 raw bool；QCheckBox 不能提交 'false' 文本。66/67 alias 修复与68/69/70文本错误由 API 回归覆盖。GUI 检查只覆盖实际 widget producer、int/bool 值和合法结果，receipt 不应声称 GUI 模拟了这些 API 错误。
2. ghost_count>0 且 ghost_casts>0 与零观察窗口本来冲突，旧错误是「零长度观察窗口不能声明魂灵施放命中」。普通成功 W0 检查须把 cast count 置 0，或明确作为真实按钮错误场景并验证错误输出；不要误期望成功返回完整 ghost 数量/实际伤害。ghost_count=0 时 inactive ghost_casts 的旧忽略另测。
3. 酒神空 target_windows 在 frames 已计窗口小计为 0，continuous S2/S3 原小计为 25000/40500（base_attack=1000 的既有 math 场景）；全部 actual total 仍 unknown。不要套 frames 零值到 continuous；真实 UI 自动培养所得 attack 值未必是1000，GUI不应硬编码这两个金额。
4. 训练精一时实际 skill QComboBox 没有 S3。必须检查 findData >=0 / currentData，而非向 -1 索引提交 S3。rank 显式设7；精零只可 S1，不能借 GUI fake unlocked slot测试资格错误。
5. reset_owner_options、relics([])、清空 timing JSON、清掉特训与目标预览残留，再设训练/技能/窗口/模式。wisdel 应先设 window10 再设 positive casts，避免自动 calculate 信号留下中间错误；最终 button payload须逐字段与期望相等，以排除 stale damage_result。
6. 本组只维什戴尔、酒神、黍、凛御银灰四 owner。drone_warmup_hits 属卡缪/荒芜拉普兰德，是旧65的整数控件覆盖，不是66本节字段；保持原459检查即可，勿用它代替 ghost_casts 新 metadata。
7. 如果实 UI 没有 current target groundtype 的可操作 producer，就将 ground metadata 的对照明确留在 API 合同范围；不可临时设置 dict、patch payload 或拿标签当实物控件证明。

## 来源范围

已读 full065 已执行 runner 的 helper/实际控制段，以及66–70最终 patch/source/HANDOFF。最终070 runner冻结后还需独立检查：旧459检查与87技能入口保留、新check计数由实际执行产生、所有未知字段/类别保持、末尾 pending guard在root源码/审查未完成时硬失败，最终截图来自真实可见窗口。

目前没有新 runner、Wine 或 GUI结果；设计notes不允许设置 complete_ui_validation=True。

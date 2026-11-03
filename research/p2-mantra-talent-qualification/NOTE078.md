# 第78节：真言未解锁天赋不应把已知输出误标未知

公共API已经按精零培养选择空天赋列表，但`palsy_triggers=1`仍生成“麻痹触发天赋”的正次数。默认倍率0只令它的金额为0；既有独立事件保护按正次数和观察范围保留未知时刻，随后误将真实法术攻击的总伤、技能阶段、周期及对应报表遮蔽。精零1级、S1等级1、手动基础攻击1000、10秒窗口：声明0的原直接伤害为1900，声明1的原结果却是None。

本节仅在实际Mantra调用方给这个伤害天赋的有效事件数加已选天赋资格。保留原始声明次数、解析、范围、错误先后、全场麻痹来源与原有参数展示；已选天赋的次数和未知事件时刻完全不变。不存在“未解锁伤害天赋就没有外部麻痹”的假设。

## 固定来源与实际选择器

- 公共基线`225cb66dc89143a3cd3a884bd6c62f47ed9d36bc`，2372个公开文件通过git archive独立冻结，不含第77节补丁，也未复制根工作树后续WIP。
- 固定游戏数据提交`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。复用现有完整character与skill原表并重新核对：character表14975251字节，SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`；skill表11447929字节，SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。原URL及路径见source-receipt078.json。
- 精确选择器`character_table.char_4204_mantra.talents[0].candidates`有四个“噤声限域”候选，原门槛为E1 Lv1潜能1/5、E2 Lv1潜能1/5；原atk_scale分别1/1.1/1.35/1.45。完整候选含描述、prob、不隐藏标记及prefabKey保留；描述明确是场上敌人触发麻痹时的元素伤害。本节不从不消耗层数概率生成额外次数。
- 完整选中character原字典、三个完整skill原对象及全部30等级BB保存于selected-original-objects078.json，实际培养/潜能选中结果与原对象逐项核对。S1原绑定skchr_mantra_1、PHASE_0 Lv1，攻击回复技力；S2/S3分别在精一/精二开放。
- 当前真实Qt参数`palsy_triggers`为0–10000整数QSpinBox，默认0，适用S1/S2/S3；源控件tuple、builder实际分支保存。API实际调用`self.option(...integer=True)`，合法数字与数字字符串继续接受，bool及原范围错误继续拒绝。没有GUI运行或新输入类型规则。
- 当前`Combat.plan`仅在not-normal实际技能分支查询麻痹声明。普通攻击计划不查询这一参数，未改普通攻击。既有selected_talents先按原培养门槛形成`self.tv`；资格判断使用实际选中名称，不按单次伤害是否为0猜测来源。
- 既有p2-independent-events来源、preserve_unplaced_sources及mask_pending_damage真实调用链均保存并复用。source_possible的含义仍是观察窗口/全局当前敌人寿命是否明确为空，未改为培养资格。

## 最窄修复与保护边界

仅修改原CRLF一行的emit末参数为`triggers if '噤声限域' in self.tv else 0.0`。原validated triggers变量仍进入参数行；不改倍率、伤害类型、神经积累、技能初动、技力、天赋概率、S3溢出跳跃或独立事件保护helper。

精零有效天赋分项次数0，不再附actual_total=None，完整数值严格恢复同情景原声明0的结果。声明次数仍出现在完整事件参考、观察窗口参考和报表参数中；source_possible原值、未核验时钟标签与实际时刻None保留。本节不能因此宣称模拟器完整或获知原生快照/事件时刻。

精一/精二已选天赋的所有技能输出、零基础攻击/元素免疫下的正次数未知来源保持，不能用per_hit=0判断无来源。S3溢出次数独立于麻痹次数；零敌寿命、零观察窗口、仅本体攻击范围空、元素抵抗和S1同一击的原顺序边界保持。全场麻痹、第二天赋“全局洞悉”、额外来源和藏品状态没有被取消。

## 完整JSON、错误与验证

主矩阵1225组加独立补充132组，共1357组配对：106组精零正声明的最终输出严格匹配该请求的原count0完整JSON，仅恢复三处原validated声明 metadata；982组canonical完整JSON相等，269组完整旧错误相等。比较器没有忽略金额、周期、完整性、来源或报表字段。精确差异路径与完整前后JSON/错误分别保存，主矩阵完成后未重跑。

矩阵覆盖87个技能及两模式、E0/E1/E2、培养等级/潜能、技能等级与旧资格错误、整数端点及旧字符串/null/bool合同、零/正观察窗口、全局敌空与本体范围空、基础攻击0、元素/损伤抵抗、S1神经顺序与河谷独立未知、自然及攻击技力、退役战斗藏品、实际选中敌人和局外属性层。补充专门覆盖S2/S3全部敌空/免疫/零攻击边界、满级与原技力来源，不引入乘数。

最初8次只读来源API结果在同一固定baseline直接复用，没有重跑。最终来源及两矩阵共2714次实际调用；此外保留初版类型合同draft的1225次调用，全部实际作者调用共3939次。它们没有被当成最终额外配对或隐藏于统计。

初版else0仅在精零合法声明0的条件引用中将JSON数值0.0改为0。为保持零声明的canonical完整结果，最终使用else0.0；初版产品、build脚本、完整结果、receipt和日志原形保留为initial-zero-type-contract078-*。baseline未重跑，产品变更后只重跑最终draft一次，计数如上。

9项新测试和83项相关旧测试通过，无skip。第一版新测试直接修改API返回的参数tuple，错误地假设它是列表，3个测试在构造反事实处报TypeError；改为先做JSON规范化。第二版硬编码continuous模式的phase_damage为1900，并假设本体范围空必然取消continuous旧攻击，这与原时序合同不符；严格完整反事实已通过，改为保留原同情景结果、仅明确零观察/全局敌空的已有零值。两次原测试/日志/JSON均保存。只修测试合同，没有据此修改产品或重跑已经通过的矩阵与83项相关测试。

## 未知、断点与交付

麻痹来源与层数消耗顺序、技能阶段快照、实际事件时刻、S1同击附加顺序、S3多目标溢出回流及间隔实际调度仍未知。取得明确绑定的原生来源前不编写额外机制。

补丁仅改rouge/operator_engine.py一行，另新增tests/test_mantra_talent_qualification.py。根代理注册tests.test_mantra_talent_qualification并集成、存档及独占tracked/Wine/GUI。作者只写外部draft与公开证据；未读取私态、未重置本局、未下载原生二进制。最终独审与哈希见independent-review078.json及handoff-receipt078.json/manifest078.json。

独立正式审查完成：fresh82组配对、164次实际公开调用，17组严格原同情景count0完整输出加仅三处声明metadata、53组canonical完整JSON相等、12组完整旧错误相等；9项新测试独立通过且无skip。作者1357组存档严格复算为106/982/269，未重跑原API矩阵。2372个baseline实际git blob、2371个未变draft文件、fresh完整原char/三skill对象、四原candidate gates/30等级、Qt整数控件与补丁实际check/apply两文件重建全部通过；独审首次无错误。独审SHA256`e586ef30f3c401193d2c166c6bec3058fb19e2df7971249ef5646f41378ec22b`；最终产品/测试/矩阵未改，只补记录封存。

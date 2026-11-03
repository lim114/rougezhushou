# 082备用只读核验：三项条件参数资料候选

固定产品提交 `c950fbc800245f7f784d6070f7126890352ffcc9`。全部读取来自 `git show` 的固定公开blob，全部输出在本外部目录；没有导入项目运行时、调用计算API、运行测试、Qt、Wine或游戏。

结论是 **3项可补来源参数资料，0项确认的产品缺陷**。这三项没有专门来源绑定证据，但现有engine对合资格模组已显示“已计模组基础属性与适用天赋数据覆盖；未建模的新增模组特性/隐藏战斗脚本不自动推断”，且非空模组parts使 `estimate.complete` 为false。仅缺专门 `source_reference` 不能改称报告已宣称完整覆盖。当前审查不批准任何数值变动，也不直接计为完成的小节。

原始游戏数据固定提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。新核对两份现有完整原件的SHA，三项各自uniequip元数据、三级parts与当前catalog完全匹配；这里只核对3项来源选择，未重跑先前34模组/102等级的属性与门槛审查。

| 候选 | 精确原文/参数 | 本次静态发现 | 保留的未知与恢复条件 |
| --- | --- | --- | --- |
| 新约能天使 `uniequip_002_angel2` | 各级 `parts[0].target=TRAIT`：“生命值高于80%时，技力自然回复速度+0.25/秒”；`angel2_tr[e].hp_ratio=.8`、`angel2_tr[e].sp_recovery_per_sec=.25` | 当前engine/报告/专用controls未读取这两个模组字段；自然回技力仍来自现有通用来源。没有证明发生实机误报。 | 实际HP条件覆盖、原生附着、自然SP来源组合及阻回行为未知。不能直接把SP速率加.25、把通用藏品current_hp_ratio当作模组覆盖或默认全程满血。可仅列原条件资料、实际激活未知。 |
| 圣聆初雪 `uniequip_002_sbell2` | 各级 `parts[0].target=DISPLAY`：“范围内敌人越多造成的伤害越高（最高提升15%）”；独立 `parts[1].target=TALENT` 的隐藏 `talentIndex=-1,prefabKey=10`：`damage_scale=.03,max_valid_stack_cnt=5` | 当前通用选天赋排除负index；没找到该隐藏参数的专门engine/报告绑定。DISPLAY与隐藏TALENT必须保持不同selector。 | 实际范围敌人数、叠层更新/上限、原生能力附着及伤害组合层未知；不能凭`.03×5=.15`证明原生公式或乘总输出1.15。需要对应版本能力与叠层/作用域证据。 |
| 真言 `uniequip_002_mantra` | 各级 `parts[0].target=TRAIT`：“对处于元素爆发期间的敌人造成的伤害提升至110%”；`damage_scale=1.1` | 当前engine/报告未绑定此模组TRAIT参数。已有初始`enemy_in_neural_break`与后续神经爆发事件只说明现有情景。 | 模组实际附着、适用伤害流/伤害类型、爆发条件覆盖及伤害转积累的顺序未知；不能默认乘全部伤害或神经积累，也不能把初始爆发标记延长为全窗口。需要精确适用/组合/时钟依据。 |

三项模组各parts的 `validInGameTag`、`validInMapTag`、`isToken`、target、完整candidate与E2L60资格字段均保留在 `exact-condition-source-candidates.json`。本次没有发现这三项在当前固定肉鸽范围下的模式标签误用或token/本体身份混淆；也没有把可保留的raw参数当作原生消费者证据。

先读了既有普通模组负审与55门槛说明，以及73先前lead负审。梅MAR-X、灵知ISW-A、水月隐藏身份、梓兰再部署、卡达单元攻速、深海色/望已知直接token字段不重复；夜刀EXE-X由parent独立核查。任何实际数值修复先取得各自恢复证据，或仅展示已核验的原参数并明确实际应用未知。

一次只读查询猜用了不存在的 `rouge/options.py`，错误已写入回执；随后 `rg --files` 找到真实 `rouge/operator_options.py`。没有依赖该失败进行产品修改或计算。原始源码、来源字段和回执均封存，未把静态核验称为API或界面成功。

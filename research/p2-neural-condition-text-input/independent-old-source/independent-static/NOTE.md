# 083独立静态核验：布尔条件的实际消费者

固定产品提交 `ea7866be6f2a8e89d382ec2982a45f1cb9231141`。7份公开文件来自固定 `git show`，AST只解析语法与字面OPTIONS；未导入项目、调用API、执行测试、Qt或Wine，未编辑生产仓库。不重新查机制，不从源码条件推断新游戏规则。

| 字段 | 实际消费者及范围 | 建议检查位置 |
| --- | --- | --- |
| `enemy_is_boss` | `operator_engine.py:248` 的 `Combat.neural` 选择神经阈值；调用位点950（酒神所有技能及常态）、1237（真言所有技能及常态后处理，含S3）、1484（存在周期时）。即便events为空仍读取阈值并验证初始积累。 | 248之前的共享neural消费者检查。检查有效准备后字段，保留固定敌人身份对过时手动值的覆盖。 |
| `enemy_in_neural_break` | 257选择已有爆发结束，277参考metadata；918酒神S1源种子，996真言S1附带元素，1242真言S2分支。共享neural在真言S3实际读取，所以不能按OPTIONS只有S1/S2而忽略S3的API入参。 | 257之前共享检查能覆盖所有实际API读取；先保留249的初始积累验证，避免抢先改其错误顺序。若要求每个局部truthiness都先检查，可在918/996/1242使用同一窄读取helper，勿扩成全局validator。 |
| `near_previous_deployment` | 仅梓兰 `apply_self_talents`，213已选具名“翔虫机动”分支内219。当前具名候选只E1/E2，从E0没有该消费者。技能1/2/3均可在满足天赋选择时适用，UI不按天赋门槛隐藏并不改变engine资格。 | 保持213资格条件，219之前局部检查。E0未解锁时仍忽略该字段，保留模组与再部署原路径。 |
| `double_charge` | 梓兰S1的1028额外五箭、1031条件数量，1310初动/充能，1437周期事件SP成本。其他技能与其他干员不消费。 | 保持1025 S1分支，1028前检查。公开calculate先在1297调完整plan，所以先完成局部验证再到1310/1437，不需要全局检查。保留缺省True、S2/S3忽略。 |

固定敌人优先链：`calculate_damage`（damage.py:373）→ `_prepare_damage`（375）→ `prepare_run`（274）→ `resolve_enemy`（run_modifiers.py:53）→ `scenario['enemy_is_boss']=record['level_type']=='BOSS'`（enemy_environment.py:110）→扩展engine（damage.py:298）。不能在这条身份覆盖前按原手动字符串拒绝有效选择敌人的输入；未知/无效目标仍按原目标错误处理。

Qt静态路径：`operator_options.py` 中这些字段默认值均为bool，app.py:665–666创建真实 `QCheckBox`，968–969按owner/skills决定显示；1035–1037同样按owner/skills决定序列化并调用 `isChecked()`。真言boss/break只在S1/S2出现，梓兰near三技能、double仅S1。此处仅验证了源码路径，未启动Qt或证明实际界面运行。

类型修复应参照已存在的局部文本条件拒绝（例如“four_sui 不接受文本条件；请使用布尔值。”）。不推测字符串 `False/0/true` 等域，不自动解析文本，不顺带把numeric/None/list旧合同改成严格bool；合法True/False、缺省和不适用字段保留。新增双重无效参数组合需由作者实际核对错误优先级，本静态回执不冒称计算通过。

一条只读查询猜用了不存在的 `rouge/run_environment.py`，命令退出2；随后固定提交 `git grep` 定位真实 `run_modifiers.py` 与 `enemy_environment.py`。诊断已留在receipt；没有在失败后进行API调用或产品修改。

`static-consumer-receipt.json` 保存全部精确读取表达式、三个neural调用、OPTIONS字面数据、梓兰具名资格、准备与Qt链及guard建议。原固定公开文件逐字节保留，供root/作者审阅；由作者/root执行实际回归与后续Wine。

封存前parent告知83作者选择更晚的范围检查：在固定 `damage._evaluate_damage_once` 的 `build_report`（320）后、return（321）前，按实际prepared scenario只检查两个神经干员的相关文本条件、所有技能。这个位置在当前该次evaluation的engine、finishers与报告错误之后，且已经经过敌人身份覆盖；静态上符合保留已有错误优先级与真言S3消费者范围。本文表格中的consumer-local位置是可选定位，不是作者最终草案。晚检查只是阻止未知文本条件的最终公开结果返回，不新增机制或重算合法结果。周期相位可能重复调用该函数；实际多相位/错误合同由作者验证，本次不声明执行通过。梓兰两条件留给85后续，未纳入83产品改动。

# 第52节：术师阿米娅S1受限continuous条件参考

本草案仅在持久外部目录工作，没有编辑生产tracked文件。冻结生产分支`codex/p2-development`、HEAD`fba536e118906f58ed2bcef359480f76e0ae4d67`；用`git archive`复制公开`rouge`依赖，再编辑draft。最初只读发现于`ab1a2f49332e9dbb577eb3ffa1a497c0bb969fa6`；51节后来改变catalog验证guard，草案重新冻结fba536e，没有用ab1a2f4旧文件覆盖生产。`freeze.json`保存公开代码hash与当时工作区状态，`source-receipt.json`保存当前草案hash。

## 两个公开反例与已有claim

共同输入为`char_002_amiya`、S1、base_attack1000、continuous、window10，其它培养用默认值。旧公开结果见`../finite-positive-audit/public-reproduction.json`及本目录`baseline-public-results.json`。

| 约束 | 原窗口伤害 | 原单次/周期参数伤害 | 原充能/周期参数秒 | 原报告 |
| --- | ---: | ---: | ---: | --- |
| postcast life .1（life1同样） | 11000 | 35000 / 43000 | 14 / 44 | 支持范围内估算、complete true |
| postcast range [[0,1]] | 11000 | 35000 / 43000 | 14 / 44 | 支持范围内估算、complete true |

旧报告并非直接声明native实测，但把这些有限输入与未裁剪的连续供靶结果一起作为当前支持估算展示。原攻击时刻来自`ready+(i+1)*interval`，技能为约.8421至9.2631秒的人工interval算例；实际获取、释放、命中和回SP相位未绑定。不能据参数时刻把life .1的伤害说成实际0，也不能用minlife或范围长度作均匀剪裁。

## 固定资料支持的边界

复用并复核原始character/skill表，固定game data commit`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。路径、URL、bytes和SHA256在`source-receipt.json`及`../finite-positive-source/source-receipt.json`；本节无新网络下载。

- `character_table.char_002_amiya.skills[0].skillId`为`skcom_magic_rage[3]`；`skill_table.skcom_magic_rage[3].levels[9]`记录AS90、名义duration30、cost30/init15、自然increment1与MANUAL/prefab`skcom_attack_speed_up`。这些参数不证明实际技能结束或阻回时刻。
- `character_table.char_002_amiya.talents[0].candidates`记录E2攻击敌人回复SP2（高潜3），消灭回复8（高潜10）。本节不推断击杀；实际攻击回SP仍需获取/命中/回调时钟证据。E0/E1与禁用连续攻击参考中的无额外攻击回SP参数独立保留。
- `character_table.char_002_amiya.phases[2].attributesKeyFrames[0].data.baseAttackTime`为1.6；普通Attack动画提取19帧OnAttack/53帧长度仍`reference_only`、`runtime_binding_verified:false`。它不能证明S1选用/重置这些动作，也不能绑定continuous首击。
- 既有`research/p2-empty-enemy-scope/NOTE.md`及receipt已明确finite-positive life/nonempty range为未绑定旧参数；`p2-phase-guards`、`p2-environment-and-lifecycle`也未提供新的native时钟证据。此次证据闭合为“已知参数、未知实际时钟”，不是新机制实现。

## 窄修改

只作用于术师`char_002_amiya` S1、continuous、明确postcast正life或非空range；empty range单独数学排除。默认无约束、typed numeric life0、frames、其它技能、独立友方治疗/即时来源保持原路径。本节不将护栏推广到P2全范围，也不重新改变48/49/50机制。

`Combat.plan`在既有伤害修饰后保留独立conditional clone，再从actual组件移除人工`times_seconds`。正观察只要来源仍可能，即使旧参考hits0也标`actual_total=None`；不能将短正窗口的参考0当实际0。clone保留原单击、数量、修饰和半开phase计算，例如AS+50仍原cast45000/phase44000。

结果对象新增`amiya_continuous_reference`，保留旧窗口/单次/phase/充能/周期等完整参数，声明未绑定实际获取/命中；旧自然rate、有效cost、攻击SP量及启用条件分别保留。actual伤害aggregate和postcast recharge/cycle/cycle damage/DPS/HPS为unknown，complete false，`phase_clock_unbound=True`、`resource_and_damage_shared_clock=False`；周期known subtotal不补0。

原施放前initial约定独立保留，未用施放后的life/range重写它。默认initial7不是硬编码：E0/E1、潜能、自然SP效果、`continuous_attacks=False`的原initial及参数均在成对结果中保持。

window0只使当前观察伤害0，不排除正来源的全技能与后续资源。range`[]`仅排除这个声明的当前敌向数学来源，伤害0；自然cost/rate=30、nominal cycle60独立保存在reference，actual recharge/cycle仍unknown。它不证明游戏没有其它目标或其它来源。typed numeric life0仍保留既有历史known30/60合同，不能拿此历史约定作新的native证明。

empty分支同步清`times_seconds`与可能的`event_amounts`，保持事件数组不变量。独立review用内部fixture发现旧草案会令`phase_totals(zip strict)`报ValueError；本次窄修和回归只针对排除后的数组，不恢复退休的first_damage callback，也不把内部fixture算公开或native证据。

报告新增“受限连续时序参考”，分列旧窗口/单次/充能参数、自然充能参数与actual unknown；原初动和名义持续继续作为独立参考。仅受限路径同步`result.scope`与`estimate.scenario_scope`，将旧单目标持续供靶适用范围及“按事件共同计算”notes改成明确合成间隔条件参考，避免报告继续将当前有限约束称为持续命中目标。默认/typedlife0旧scope和notes不改。没有新计数、SP事件或native成功声明。

## 已接受的零值类型边界

`zero-type-boundary.json`及`baseline-zero-type-results.json`、`draft-zero-type-results.json`用普通公开API独立配对`0`、`0.0`、`"0"`、`"0.0"`。原验证接受这四种输入，但continuous旧raw等零分支只识别numeric0：numeric0原伤害0/资源30/60，string0原伤害11000/资源14/44。本节numeric0完整结果不变；string0经有限helper排除当前敌伤为0，actual recharge/cycle为None，30/60只作参数。

因此本节没有统一等值零的资源口径，不能泛称所有有效数值类型结果相同。root已指出并允许明确记录的有限边界，未默默扩为全局归一化。最窄后续候选是在caster S1 continuous输入独立验证之后，对内部timing拷贝中的有限零值进行归一化以复用typed0旧路，保持用户输入不变；必须先拒绝bool/无效/非有限值，且回归初动独立、其它source隔离。是否应推广公用归一化由独立后续节审阅，不靠机制猜测或本节测试证明native时钟。

## 验证与公开复现

`reproduce.py`在两个隔离进程导入baseline/draft，以普通`calculate_damage`比较708个输入：276个原路/其它scope完整结果相等；216个正观察实际unknown；108个zero观察仅窗口0且cast/resource unknown；108个empty range敌伤0且资源unknown。另有上述4个zero类型边界配对，单独计数，不混作一致性控制。

正约束逐项核旧完整clock reference（含半开phase）、initial、duration、面板/培养、修饰后的组件，并确认输入和共享catalog未变。正约束unknown在无攻击回SP、E1、短窗口场景同样成立；独立自然参数不等于完整actual资源模型。controls包括其它技能、frames、苏苏洛友方治疗、Gnosis S2 instant，未按continuousintervalguard抹掉独立来源。

19项新回归与156项相关测试通过，命令及输出见`related-tests.log`。独立review见`REVIEW.md`、`ENGINE_REVIEW.md`及其公开probe；review报告最初18项，窄数组修复后补核第19项。没有由本代理运行全量、Wine、真实UI或native验证；parent负责实际合入及全量验证。

```bash
cd /workspace/.continuation/p2-after-050/draft52
/workspace/rougezhushou/.venv/bin/python reproduce.py
/workspace/rougezhushou/.venv/bin/python regenerate_patch.py
cd draft
/workspace/rougezhushou/.venv/bin/python -m unittest tests.test_amiya_continuous_lifetime tests.test_attack_speed_bounds_065 tests.test_damage tests.test_empty_enemy_scope tests.test_friendly_scope_report tests.test_gnosis_isw_a_reference tests.test_haruka_healing_targets tests.test_mizuki_amb_y_reference tests.test_susuro_recipient_factor tests.test_timing
/workspace/rougezhushou/.venv/bin/python ../finalize_receipt.py
```

交付是独立context hunks`code.patch`、`tests.patch`、组合`section52.patch`；不是旧完整文件覆盖。重生成后的patch在当前fba536e上`git apply --check`通过，工作区仍clean，最后receipt记录head/hash；tracked文档合入由parent处理。

恢复actual正上下文的条件：取得匹配版本的S1模板与普通攻击获取/释放/命中/停止/重获规则、情绪吸收SP回调顺序，闭合真实技能结束与后续目标/资源来源，并绑定可复核时刻。原黑板、普通Attack动画、人工interval算例、数学空源或测试通过本身均不满足。零值归一化是独立输入合同恢复项，不能借其解除native unknown。

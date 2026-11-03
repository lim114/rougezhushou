# 第 52 节独立只读 engine / public / report 审查

结论：指定普通 public 范围内未发现阻塞问题；已有一个 helper 内部不变量问题，见下方补充，由 parent 处理后继续合入与必需验证。没有修改代码、测试或 patch；本审查仅新增此笔记。没有网络、private、游戏、聊天或 native 相位推断；没有扩大全量测试。

冻结基线：`fba536e118906f58ed2bcef359480f76e0ae4d67`，branch `codex/p2-development`。已读取 `freeze.json`、`code.patch`、`tests.patch`、`section52.patch`、完整冻结 draft 相关源码及已有 155 项相关回归日志。`git apply --check section52.patch` 通过；生产树未应用该 patch。

审查时 patch SHA256：

- code.patch: `17a1a30b4468b02e99996e1246deebf129e0d4f40c04651e3f0c331ed3fe230f`
- tests.patch: `cccc6d5a416ef9b2d4e13fd60ffc7c991ae7de8cc85ca7b6d1b48f50c3ae1ed1`
- section52.patch: `655fb945ca3619104575394d7251130c3a3e39a73c839c03bc237440621565a3`

## 独立执行的验证

在冻结 draft 目录独立重跑：

```
/workspace/rougezhushou/.venv/bin/python -m unittest tests.test_amiya_continuous_lifetime -v
```

18 项执行、18 项通过。已有 `related-tests.log` 为 155 项全通过；此审查没有重跑或将该日志冒称为独立执行的 155 项。

另用两个隔离 Python 进程分别导入 frozen baseline / frozen draft，执行 16 个普通 public `calculate_damage` 调用。基本输入为 `operator=char_002_amiya, skill=1, base_attack=1000, timing_mode=continuous, window_seconds=10`；仅使用下列范围边界与培养/静态数值修饰。每个受限案例同时断言 actual aggregate、公开 report、metadata 和参考值，断言全部通过。

| 变体 | 审查结果 |
| --- | --- |
| 无 timing 约束 | baseline 与 draft 完整返回字典相等，包含 report/notes/metadata |
| typed life 0 | 完整返回字典相等 |
| typed life 0 + nonempty range | 完整返回字典相等 |
| typed life 0 + empty range | 完整返回字典相等 |
| life 1 | actual damage/recharge/cycle 及周期依赖量 unknown，条件窗口11000、单次35000、充能14保持 |
| life string `"1"` | 同 life 1，合法数值字符串未漏过护栏 |
| nonempty `[[0,0.1],[5,6]]` | actual unknown；旧条件窗口11000保持，没有均匀比例或 minlife 折算 |
| empty `[]` | actual 当前敌源伤害0；自然充能30、周期60只在 parameter reference；actual SP/cycle unknown |
| numeric string `"0"` | 数学空源，当前敌源实际伤害0；实际回转仍 unknown |
| window0.01 + life0.1 | reference hits0，但 component actual_total=None / actual damage unknown，没有把迟首跳假设变成实际0 |
| window0 + life0.1 | shown实际伤害0且没有 pending shown组件；full cast actual unknown，full参考35000、actual recharge unknown |
| life1 + ATK+50% / magic伤害+20% / RES25 | 每击条件参考1350，窗口参考14850；actual仍unknown；与baseline修饰值一致 |
| empty[] + 同上修饰 | 当前敌源实际伤害0，每击条件参考1350保留；自然30仍仅reference |
| potential6 + natural SP+1 + life1 | 旧初动4.5保持，条件充能8、自然充能15；actual recharge unknown |
| elite0/rank1 + life1 | 旧初动40保持，无攻击回SP天赋仍不伪造native lifecycle；条件窗口8000、充能40 |
| continuous_attacks=False + life1 | 旧初动15、自然参考30保持，actual伤害/回转仍unknown |

对全部受限案例，独立断言：

- `estimate.skill.recharge_seconds/cycle_seconds/cycle_damage/cycle_dps/cycle_healing/cycle_hps` 均为 None。
- `report` 的 timing/recharge、timing/cycle、damage/cycle_dps 均为 None，没有从旧 scalar 或 known subtotal 漏回数值。
- `phase_clock_unbound=True`、`resource_and_damage_shared_clock=False`，两个 complete 均 false。
- actual components 无 `times_seconds`；参数参考仍可保留旧合成时间，并明确标注条件 reference。
- 所有新护栏案例的初动与名义持续和 baseline 一致；没有硬编码默认7/30。
- 正约束条件 reference 的 window/total/phase量与 baseline一致，包括修饰后的 per_hit。
- 若有 known_damage_subtotals，其 cycle_damage/cycle_dps均None。

另修改返回值中的 modified-positive `window_reference.conditional_components[0].per_hit=99`，确认 actual component 和 cast reference 的 per_hit仍1350；返回参考量互不共用可变 component。新增测试也覆盖输入/catalog原参隔离。

## 代码和报告核验

冻结 draft 行号：

- `rouge/amiya_continuous_reference.py:5–20` 仅 char_002_amiya / S1 / continuous 进入新路径；typed数值0最先排除新guard，`[]`或合法string0进入数学空源，life>0 / nonempty range进入unbound。此前 AttackTimeline 的合法输入校验仍执行。
- 同文件 `:23–46` 每个 plan单独保存深拷贝条件参；正观察由duration>0决定possible，故短正窗口reference hits0仍pending。空源和零观察明确置0，不保留actual pending。
- 同文件 `:56–76` 从实际mask前保存clock，phase参数从单独reference的半开区间算术恢复；没有拿minlife重新算伤害。自然SP只保存cost/rate参数。
- 同文件 `:89–101` actual damage mask与全部cycle-dependent字段/known subtotal同步，明确 clock metadata/complete false和无native证据说明。
- `rouge/operator_engine.py:1242–1245` preserve_plan置于已有伤害修饰和伤转治疗结算之后，条件per_hit包含已经支持的静态数值；实际pending不伪装事件时间。
- `rouge/operator_engine.py:1285–1288` 空源选择既有自然充能参数；`attach_result`随后遮罩实际SP/cycle，未将自然参数当作native实际。
- `rouge/operator_engine.py:1706–1709` 新附着限定guard已经存在的full plan，未覆盖友方/instant/其它技能模型。
- `rouge/reporting.py:380–394` 条件窗口/单次/充能与实际结束后充能分列；已有 timing/damage 主区块读取的actual scalar已为None。
- `rouge/reporting.py:688–691` known subtotal说明接入该受限来源，未将参考小计当完整输出。

现有18项新测试包含其他技能、frames、友方、instant隔离以及精确interval boundary的phase参数核对，已独立运行通过。独立public probes也确认完整旧路返回字典保留，而非仅检查几个scalar。

本结论只适用于以上冻结patch与委派范围。实际首击、获取、命中、攻击回SP和后续游戏目标/native时钟仍unknown；本审查没有宣称native验证成功。

## 主审补充的内部不变量

主审另报告：`preserve_plan` 的 empty 分支在 `amiya_continuous_reference.py:29–33` 将 hits/total/times清零，但不清既有 `event_amounts`。若输入内部component已经带有非空amounts，保存的conditional component含 `times_seconds=[]` 与非空amounts；`:62` 调用 `phase_totals` 的 strict zip会抛ValueError。读源码可确认这一结构矛盾。

当前普通public首伤callback已经按原任务边界退为reference-only，本审查没有激活退休callback、没有把内部构造算作普通public失败，也没有据此扩展技能/来源范围。建议parent在数学空源/零观察的清零分支同步清空或移除event_amounts，使参考component内部一致；正观察pending的条件参仍可保留其原事件金额。以上结论对应开头的冻结patch哈希，若parent修改该点，应重新定版并运行受影响的窄验证。

报告中“自然SP参数不证明没有其它游戏目标或来源”只公开准确的未知边界；它没有断言当前游戏一定还有目标、也没有断言游戏没有其它目标。空范围的数值0仅针对当前敌源的数学排除。

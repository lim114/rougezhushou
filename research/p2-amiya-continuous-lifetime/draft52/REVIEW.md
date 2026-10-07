# 第52节独立只读 review

当前普通 public 范围内未发现合入阻塞。helper 的范围、正上下文分类、条件参数保留、actual damage/SP/cycle 遮罩、初动独立约定和报告传播符合本节授权。代码、测试与patch均未修改。本结论不声称新native时钟证据；仍只支持原表参数。

审查冻结基线：`fba536e118906f58ed2bcef359480f76e0ae4d67`；patch的SHA256记录于 `review-public-probe.json`。已读实际code/tests/合并patch及冻结baseline/draft。此前来源审计为 `../finite-positive-source/source-receipt.json`，其原表hash与选择器已经复核，不重复无新线索的查询。

## 已核实际实现

- `amiya_continuous_reference.source_state` 仅允许char_002_amiya、S1、continuous；typed numeric life0优先保留完整旧路；其余math empty和unbound分支受原AttackTimeline输入验证约束。其它技能、frames、friendly、instant均不附加guard。
- `Combat.plan` 的注入在原伤害modifier与伤转治疗处理之后。full/shown/normal各自深拷贝conditional components再移除actual合成times；已有per-hit、数量和总量参数可独立留存。duration>0而非参考hits决定positive可能性，避免短正窗口reference0变actual0。window0只使shown为0，full cast仍pending。
- attach_result先保存完整旧clock、normal充能来源及修饰后的条件参，再调用既有pending damage mask。半开phase参数用保存的clone计算，AS50时旧45000 cast/44000 phase保持，没有直接用去时刻的actual component改参数。
- SP/周期另行mask，actual recharge/cycle/cycle damage/DPS/HPS均unknown，known_damage_subtotals的周期项也None。自然SP rate、cost、自然-only参数独立留存，未把30补成positive-context的actual recharge。
- 初动使用动态旧first，而非硬编码7；P6/自然SP效果、E0/低rank与disabled attack-SP的不同旧值均保持。postcast[]没有重写precast来源。
- 报告将条件窗口/单次/旧充能/自然参数与实际充能分列；timing与damage主区块读取actual None。metadata有phase_clock_unbound、shared_clock false与complete false，没有30Hz/native新成功声明。

## 独立验证

主审使用两个隔离Python进程分别导入frozen baseline/draft，经普通 `rouge.damage.calculate_damage` 执行18个paired输入，结果见 `review-public-probe.json`，18项比较全部通过：

- 8个positive-context情景：默认、ATK/伤害倍率/RES修饰、P6自然SP、E1 rank7、window0、短正window、AS50半开边界、disabled attack-SP。全部旧clock参数逐项等于baseline，包括window/cast/phase/cycle量与初动；修饰后的每击值保留。
- 4个完整旧路控制：无约束、typedlife0、typedlife0+非空range、typedlife0+[]，所有返回字段（含报告/notes）与baseline逐字典相等。
- 6个scope控制：S2/S3、frames、医疗阿米娅、苏苏洛、灵知S2，完整返回字典与baseline相等。

并行独立审阅记录在 `ENGINE_REVIEW.md`：实际重跑18项新测试全部通过；另外16个普通public probes核actual report/metadata、[]/string0/短正/零观察/修饰/动态初动/返回参考隔离，全部断言通过；`git apply --check`通过。已读parent的155项相关通过日志，未将其声称为本主审重跑结果。本轮没有全量/Wine/native/UI验证。

## 本节明确边界与窄后续

1. **typed zero与accepted numeric string zero尚未统一。** typed0保留旧actual recharge30/cycle60；valid string`"0"`进入新的math-empty helper，actual资源unknown，30/60只在parameter reference。两者当前敌伤均0，但资源口径不同。parent/root已明确允许52记录此边界并暂保当前patch；不得泛称有效numeric类型结果完全相同。后续恢复条件是独立验证公用或仅caster的zero归一化方案、初动独立与其它source隔离，再在单独节处理，不靠新机制推断。
2. **empty helper的事件数组缺口已窄修并复核。** parent仅在empty分支同步已有`event_amounts=[]`，未恢复任何callback。此前ValueError证据保留在 `review-event-amounts-probe.json`；同fixture的修正后phase_totals为(0,0)、actual/reference数组均空，证据见 `review-event-amounts-fixed-probe.json`。新增内部不变量回归和string0的actual recharge/cycle None断言已经独立执行，当前19项新测试全部通过。此项不再是开放缺口；这些内部fixture不算public/native验证。

实际首击、获取、命中、攻击回SP和native结束/阻回保持未知。修改不会证明P2全范围完成，也不会证明游戏不存在其它目标或来源。

## 窄修后的复核

独立只读核 `preserve_plan` empty分支同步清event_amounts，以及新增回归；2026-10-07在冻结draft执行 `PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python -m unittest tests.test_amiya_continuous_lifetime -v`，19项运行、19项通过。修正只维护数学空源数组一致性；source_state、typed0/string0资源边界、初动和其它source范围均未改。旧patch SHA/18项审查记录属于此前冻结；parent尚待重生成patch，本次复核文件SHA在 `review-event-amounts-fixed-probe.json`，未声称新patch的git apply验证完成。

## 受限scope / notes窄复核

parent随后仅在attach_result受限分支改result.scope与estimate.scenario_scope，并以完整字符串mapping重新标注三条旧默认说明：连续存活假设、完整间隔估算、合成攻击/SP事件。只读核查确认scope无全局改动，数字/clock计算没有改变。独立运行report、default、typedlife0三个相关测试全部通过；6个隔离进程public配对确认unrestricted与typedlife0完整返回字典仍等于冻结baseline，positive life/nonempty range/[]/string0的四个受限路径scope一致、旧三条说明不残留、条件参考与当前actual明确分列。证据与当前helper/test SHA在 `review-scope-notes.json`。未再扩大测试或处理zero类型归一化。

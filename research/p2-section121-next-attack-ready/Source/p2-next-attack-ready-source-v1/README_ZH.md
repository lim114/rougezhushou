# 下一攻击槽：零技力需求的资源阶段（Source-only，未应用/未执行）

实际功能修复：SP已经满足时，下一攻击技能不再额外充一次技力/等待一整连续攻击间隔；仍必须存在既有模型的合法攻击槽，明确空敌人/空供靶保持未知而不是无条件0。这个资源结果不宣称原生技能绑定、实际出手、实际结束已确认。

## 可达公开反例与已存在机制

`calculate_damage` -> `Combat.calculate` -> 对INCREASE_WHEN_ATTACK调用`charge_seconds(...wait_next_attack=True)`。高卢银行支票legacy_98原来源值initial_sp+12、第二经济改革法legacy_99为+18，无周期SP。真言S1 R7 cost3，基础interval1.6：选任一项后required=max(0,3-12/18)=0；原有continuous首attack start0、release1.6，frames手动前后摇0首start/release0。

旧函数只在 `required<=0 and not wait_next_attack` 提前返回。要求下一攻击槽时，count=ceil(0/1)=0，frames已有`start_frames[0]`=0正确；continuous却索引`release_times[count-1]`即release[-1]，唯一出手1.6，被误当作初动需继续充能。这是count0的负索引算术错误，不是新增客户端时钟假设。

`periodic_charge_seconds`早已ready0然后选首legal start；`sp_events.charge`同样ready0、首legal start（后者本次仅conditional API交叉参考，不启用已退役公共战斗回调藏品）。`charge_seconds`自身frames的零需求逻辑也已采用首start而非release。

## 成组修改与不变边界

1. 未满足required>0时才要求increment>0；SP已经就绪的下一攻击槽不依赖未来能否充能。修正同一零需求阶段的除0保护；正需求且increment0仍None。
2. required0时count0，避免ceil(0/0)；仍构造同一timeline流，保持供靶/目标消失/interrupt检查。
3. continuous且wait_next_attack、count0：有合法stream start则0.0，无stream则None。**此内部调用没有start_delay参数，现有continuous AttackTimeline开始ready=0；不新增positive目标窗口、movement/interrupt或nativeclock支持。** frames直接保留原有start槽，包括显式供靶5秒后才首次合法的旧口径。

所有positive required的攻击数、浮点times索引、原有bit结果不变；非next技能required0仍旧返回0（并不要求攻击槽）；完整技能伤害/治疗、持续、周期充能与回转结果不因仅birthSP改变。既有Wine/default/Unknown/参数参考限定保留；不可把梅等原生时钟未知重新宣布完整。

## Source手算与Root实际计划

公开6输入：真言S1 R7无birthSP的initial为frames144/30=4.8秒、continuous3×1.6；两项birthSP各自两个模式initial0，其他生命周期/输出Graph应保持无birthSP已知值（仅相关初动/部署clock字段变动）。R7技能伤害单次2750，满额DEF/RES0、无神经爆发且初始累积0。源码原神经阈值1000，2750×.2=550不会爆发。

9方法test建议：两公开SP就绪藏品×两模式；与无birthSP成组Graph/生命周期控制；三formatter纯度；direct API required0/increment0×两个阶段和模式；空供靶仍None；frames首合法start5或offset2后的相对3；与已有periodic/classified conditional API zero契约一致；positive需求float.hex逐字节不变；非next zero语义保持。

Root先original公共6case/API/三formatter，必要direct函数原件测错输出；保留原图后应用strict transport与test，候选Linux/Wine相关时序/技力/所有支持技能回归，实际窗口用真言S1+birthSP验证初动值/报告。断点与提交由Root真实执行。

仅std Source read/AST/hash/compile-noexec/offrepo输出。没有项目import/API/tests/Qt/Wine/helper/native/gzip/Git，也未改tracked/private。本包runtime_pass=False，所有手算还需Root实际确认。

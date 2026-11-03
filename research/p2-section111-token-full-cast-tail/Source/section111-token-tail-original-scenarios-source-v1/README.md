# 第111节：深海色触手完整施放尾弹原行为观察输入（仅Source）

本包仅提供18个合法公开输入和固定源码依据，未调用项目、测试、codec/helper、窗口或Wine，也未修改仓库。原行为与未来候选值均须由Root实际调用取得，不含猜测的伤害/命中数。当前hash是准备时源码快照；正式观察须重绑109/110完成后的完整Source+CORE实际guard。

每个技能各9个输入，均为E2/L70/M3、潜能1、信赖100、无模组/藏品/手动数值增益、1只触手。parent与unit使用显式1帧前摇/0帧后摇的局外情景；它们不是客户端实测动作。S1原表名义持续30秒，S2为55秒；均自然充能。

|输入族|目的|
|---|---|
|unit travel缺省/显式0|合法健康对照，核子配置读入路径|
|unit travel10、无window|直接记录cast全归属与窗口命中列表的差异|
|unit travel200、无window|已出手的远期命中不能提前算入phase/cycle|
|unit travel10、window5/0|完整cast仍单独计算，公开观测窗口保持截断|
|unit travel10、目标消失20/0|目标生命周期取消弹体；不得为补尾弹制造命中|
|continuous、unit travel10|保持现有连续间隔估计，不能强行套帧弹道|

`timing.units[token_10001_deepcl_tentac].projectile_travel_seconds`在现源码中确实消费：timing.py220–229将配置复制给child，递归未传unit参数，故child的284行读该配置。包没有假设`units.delay`接口。生命周期输入置于parent，由224行继承到child；消失20表示目标全局消失时刻，不是触手在场寿命。

问题在operator_engine.py348：触手总是消费`times_seconds`。既有owner通用313行在完整施放frames/window缺省/not-normal时消费`emitted_times_seconds`；timing.py317–338已经保留窗口结束前出手、结束后命中且目标仍存在的事件。可考虑的最小产品修复只调整触手消费选择，不更改任何事件producer、duration/SP、目标生命周期、属性与叠加。

公开结果的`components`和`timing.streams`是shown观测；`estimate.skill.hit_counts`及`total_damage`是full施放。无window的frames结果仍会调用nominal duration窗口作为shown（1306–1309），所以不能把公开`total_damage`当完整施放伤害。有限window例需对应同技能/同travel的无window例核full；充能期普攻通过`timing.recharge_streams`和cycle指标观察，包不提供虚构的public `normal=True`。

Root实际验收应保留每例原caller/native/full结果、实际异常阶段、原计算透传与三种全文；实测full/token命中差异、finite/continuous/normal守恒、disappearance0/20守恒。200秒案例用于区分cast归属与实际phase/cycle，不证明任何游戏触手会发射200秒弹体。

同类Source搜索只发现operator_engine中一个带unit的timeline.attacks调用（触手）。维什戴尔幽魂现为条件次数参考，没有同一已绑定事件consumer，不能据此扩成新的真实弹道模型。

尚未解决：实际触手在场/技能热更新、技能回复覆盖、动画/当前客户端绑定、真正弹道或触手寿命；本节候选不得声称这些机制已经验证。

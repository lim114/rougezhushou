# 0.67 · 弹药计数事件的直接调用与计算接入

2026-10-06。本批继续非识别P1。接入的是既有计数器的事件扣弹规则，不把配置参数当作完整技能时间轴，不开放新的游戏操作或战斗事件输入。

## 查证与新发现

先复用0.55的真实prefab、MonoScript、元数据、原生指令与0.62消耗记录。定向查阅[新约能天使资料](https://prts.wiki/w/新约能天使)：S1正常逐发与主动倾泻、S3整组耗弹应分别处理。网页仅为交叉检查，代码规则以实际安装数据及原生路径为依据。本批没有启用主动倾泻的计算场景。

0.55报告指出默认OnCountEvent为空通知，尚未闭合具体耗弹回调。本次沿OnEvent中通知之后的分支发现直接证据：

1. 0x180f521e9/0x180f521ee读取匹配事件与ignoreUntilCastEnd。
2. 0x180f52253、0x180f52258、0x180f52291依次检查事件、已触发状态和ignoreTriggerOnce。
3. 0x180f522a6设置虚表slot16，0x180f522ae调用0x180005840；helper按slot索引读取虚表方法并跳转。实际元数据中slot16就是AbilityEventCounter.DealCountEvent。
4. DealCountEvent先写m_triggerOnce，再通过GetExpendCount取得本次消耗，原始计数直接加算；GetExpendCount在notCountNext时返回0，否则返回完整expendPerTrigger。
5. ON_DETACHED/ON_CAST_END清除四字节短时标记；ON_ATTACK_FINISH只在配置开启时清除对应标记。OnCastStart仅清ignoreUntilCastEnd，不自行重置triggerOnce。

因此不能把“OnCountEvent为空”推成“OnEvent未调用扣弹”。通知和实际扣弹是同一入口里的不同步骤。本次只闭合该入口到扣弹的原生路径；外层能力何时发出各事件、技能序列首次绑定和真实帧数仍未全部查明。

## 固定来源与范围

基包26-08-16-14-00-43_415873；DLL SHA256 `6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`；metadata SHA256 `ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。从磁盘读取，未加载DLL或读取游戏进程。

`count-callback-cfg.json`包含5个完整有界方法、260条指令，逐条重核磁盘字节。`verify_ammo_event_sources_067.py`同时校验方法、虚表slot、字段偏移、事件枚举、实际AB文件哈希及MonoScript唯一类型哈希。事件4为ON_SPELL_ON，5为ON_SPELL_END，6为ON_ATTACK_FINISH；不是命中次数。

| 当前计算绑定 | 计数事件 | 每次消耗 | 同一施法允许重复 | 说明 |
| --- | --- | --- | --- | --- |
| 凯尔希·思衡托S2 | SPELL_ON | 1 | 否 | 额外等待攻击周期标记不在本次时序实现内 |
| 机械师S1 | SPELL_ON | 1 | 否 | 一次计数对应一轮攻击，不按每次伤害扣弹 |
| 维什戴尔S3 | SPELL_ON | 1 | 否 | 同一计数器的恢复预算保持 |
| 新约能天使S1 | SPELL_ON | 1 | 是 | 主动倾泻需要独立事件排程，未开放 |
| 新约能天使S2 | SPELL_END | 1 | 否 | 两种朝向配置一致，但各自计数器独立 |
| 新约能天使S3 | SPELL_ON | 5 | 否 | 不足五发时仍记录整组消耗 |

六个技能对应八个实际组件实例。它们的old_type_hash与公共MonoScript的PropertiesHash均唯一匹配到原始AbilityEventCounter；不是依字段形状猜类名。能力和技能特殊派生类未推广使用。来源为0.54 selected-ammo-public-prefabs/selected-ammo-counter-config、0.55 first-batch-public-prefabs/first-batch-contract；原件与配置分别核对。

## 实现

`AmmoConsumption`组合既有AmmoCounter，只投影扣弹闸门及相关标记。显式事件可区分未到扣弹点、已经扣过一次、允许连续扣弹、免耗弹和忽略计数；免耗弹仍关闭一次性闸门。最大容量变化不清耗弹和恢复预算，也不提前制造事件。不同朝向/模式使用独立闸门。

`ammunition_rounds`对六种已核验配置使用完整普通施法的事件序列；一次正常施法的消耗与原计算一致。通用显式计数调用仍按原契约处理。S2补弹、机械师屏障、移动消耗、实际施法结束帧、同帧书轮询并未因此自动启用。

该投影刻意不设置readyToReset、不ResetCount、不运行特效/天赋通知或共享黑板。普通施法参考不宣称这些回调之间的绝对时间；AmmoCounter.ready_to_reset仍由原有明确输入管理。现有伤害、初动、回转、周期数值保持，不将新内核等同于新技能完整支持。

## 验证

15项新增方法含事件顺序、重复与允许重复、免耗弹闸门、忽略标记、拆离清理、攻击结束条件、多发超额消耗、补弹共享预算、施法中容量变化、双模式独立状态以及公开计数循环实际调用新入口。初始缺API产生的失败保存在red.log；最终60项相关检查全部通过。

完整CORE98组选择器：1223运行，1153通过，70历史跳过，零失败/错误，源码/测试/runner起止稳定。732完整0.66算例严格零差异无豁免，27项既有临时Qt通过；这些是回归，未冒称15项新增均为实机或新增UI覆盖。公开wheel全部Python及34参考资源核验通过。

## 后续缺口

P1仍需核验完整能力事件生产链、结束帧与阻回衔接、动态最大弹药的实际创建/删除时机、特殊屏障/移动/布子耗弹，以及实际书轮询和同帧先后。当前XLua热更新等价性仍未证明。本批消除的是默认计数事件到耗弹的调用缺口及其计算内核接入，不能将整类特殊弹药或全部P1销项。

本次补充SP/九头蛇检索没有获得新负值/倍率或成长脚本依据：原始rogue_6递归查找sp_recover仍只见已知六条来源，没有以新猜测改变数值。原研究结论继续有效，不重复修改它们。

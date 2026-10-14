# 机械师S2按来源汇总屏障与有序筛选链

新增能力是逐实例资格筛选、signed64原值汇总及两来源门，可直接替代逐包账本中的手填来源总量。它不是重复查询封装，也不采集战斗、自动建立屏障或写本局状态。

## 原件与读取范围

当前安装候选DLL SHA `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`、metadata SHA `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`，与266/267同一候选。重新归档15个方法/内部助手、1028条唯一指令，每条与物理文件字节复核；没有执行DLL、读取游戏进程或发送聊天。详见native-proof.json及绑定的rouge/data/shield-source-inventory-source.json。

65471 CalculateShieldValueByTarget：排除空实例、结束/禁用、来源不同及hasShield关闭项，累加CalculateShieldData tuple+8的FP值，不看tuple中的mask。来源两引用非null的普通路径比较身份；null/失效引用其它路径不靠字符串猜测。表中身份只是调用方声明。

两个内部助手0x180662420/0x180662260保持metadata index=null，未伪挂为方法65277/65279。其比较的klass+0x11c==0x77字段语义未证，接口分派及XLua未闭合；只有明确普通直接数据分支或独立getter返回快照才可引用值。普通直接分支BB对象缺失走throw/trap，不能作0；BB存在、numeric lookup明确失败才默认0。

FP.Add220464（同址FastAdd220466）0x184624db0只有LEA/RET：原值64位回绕相加，不经单精度、不clamp。LE(FP)220333及LessThan220482用于本模板阈值0，即signed total_raw严格小于42950。对应模板/IfConditions/ActionUtil仍绑定266原件：research/p2-mechanist-incoming-266/native-proof.json与research/p2-mechanist-s2-shared-barrier-current/buff-template-binding.json。

99029 FilterByShieldValue：target无效返回false；source无效按此模板passIfNoSource=true早返回，不读container；target/source有效而container缺失走throw/trap。caster条件false不调用recipient筛选；两种正常false都不阻断外部AlwaysNext，而异常/未证正常返回不能据此推后续节点。

## 独立算式与控制流

- 同来源21475+21474=42949，通过；21475+21475=42950，不通过。必须先求和，不逐盾LE后合取。
- 两块各raw2^62相加为signed −2^63，通过LE0；MIN_RAW再加−1回绕为MAX_RAW，不通过。负值不夹成0。
- 结构受击后声明caster来源20盾、自身来源0、第三方100盾：来源总20/0，双筛选false；20盾结束后总0/0，true。第三方不计，mask不匹配也不排除同来源盾。
- float32 signed读值：±1对应±Q；−2^31对应MIN_RAW；正2^31、NaN/Infinity及超出signed64的值保持未资格，不模拟异常转换结果。此域不扩展267的非负创建/吸收屏障域。
- 完整空库存为0；不完整空库存仍未知。已证分项允许负值/回绕，因此不是下界。
- 库存不完整也不能确认聚合正常返回：遗漏合格盾可能抛异常。已知合格异常仍保持false；正常getter已返回而raw未知只影响数值，不把它当控制流中断。

库存必须独立声明在BlockDamage之后两来源筛选的读取点，且两筛选间无变化；不沿用受击前库存。接入账本时来源库存与旧手填总量两模式互斥，受击角色必须匹配。本体两来源是同一身份。创建/结束请求不自动插入/删除库存或生成下一个实例。

## 审查发现与验收

首轮56项及中间58项均绿，但源码审查发现其未覆盖的依赖错误：①合格caster盾BB缺失时虽total未知，账本却仍给后续爆炸/补盾/结束true、耗弹1；②不完整库存仅已列节点正常也不证明聚合正常返回。已补正常返回三态、有序短路及完整性守卫。第一项是只读reviewer运行探针的记录，第二项为源码反例；原探针完整stdout和原源文件副本未封存，不冒称可重放原件。公开输入、报告的旧分项和当前输出另见verification/sections/268-review-findings.json。旧绿日志及首次窗口源哈希原样保留，不叠加为通过案例。

最终59项相关检查通过，新增20个方法覆盖资格、符号/回绕、阈值、异常/短路、完整性、账本接入和刷新保留；原查询全集23扩为24，没有删旧查询。Windows临时状态实际MainWindow显示四实例、20/0双来源、false双门、其他干员入口隐藏，刷新保留声明和结果。原项目正常更新并可见；三个既有私有JSON无变化。

## 仍未完成

这是原件及声明条件的计算。实际库存完整性/实例附着、创建时MAX_HP和黑板来源、回调、创建/移除/计数与结束时钟、当前舍入环境及热更新仍未知。完整游戏命中、生命损失、伤害与回转不由本工具闭合。275和最终280保持完整可用范围全量，原Windows历史及私有样本缺口不计通过。

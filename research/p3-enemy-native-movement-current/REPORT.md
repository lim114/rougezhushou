# 敌人移速符文写入层与条件合成移速

本候选对应P3“紧急3–6移速符文的原生目标、写入及叠加层”缺口。固定战斗预览和指定目标局外计算现在提供独立的移速条件分项，改变了此前只能读参数、无法合成的状态。它没有把条件分项当成完整有效移速，也没有计算出生、移动位置或入场时刻。

## 实际新增结果

只对原件SHA `2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296` 的 `ro6_e_3_6` 所列固定条目供给1.5乘法和0.5关卡移动倍率。其他关卡、来源变更、参数变更、敌人选择器、重复或非法黑板不借用该绑定。

12个本关卡敌人都进入实际固定预览；指定目标的run_resolution保留同一条件分项。以基准移速2为例：符文写入属性3，然后关卡倍率得到1.5格/秒。0输入或乘法0先触及属性下限约0.1，再乘0.5得到约0.05，不能先乘关卡倍率再夹限。数值经历FP乘法、Clamp、float字段写回、重新读取FP和后续关卡倍率；0.4的条件合成结果是float写回后的0.30000001192092896，不把整链换成一次Python double乘积。

普通界面新增“符文写入移速属性”和“无其他属性修正的条件移速”，同时保留“预计有效移速：未知”。技术界面分清参数、原基础×关卡倍率旧小计和新条件合成值。原 `stats.moveSpeed` 保留来源字段，避免把新分项静默作为实际动态属性。新结果不影响既有生命/攻击/防御/法抗或伤害数值，也不重置界面选择。

## 来源先于计算

当前基包文件只读，DLL SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`，基包版本26-09-13-15-28-10-30688348。没有加载DLL或读取进程内存。

- `RuneManager._RegisterRuneClasses` 在0x180ce730f将literal `enemy_attribute_mul` 与typed MethodSpec300044 `_Register<EAttribuesMul>` 关联。literal、MethodSpec、generic inst/type参数、方法定义和原调用字节单独绑定；不宣称恢复全局generic原生地址映射。
- BasicEnemyRune.PreprocessEnemy85350执行Verify85042后经虚槽20进入EAttribuesMul.DoPreprocessEnemy85363。metadata虚表绑定该槽。接收的是LevelData.EnemyData.attributes@0x28，随后调用ApplyChangesToAttributesMul85057。
- ApplyChangesToAttributes85054遍历fieldMetas，取得AttributeMeta枚举类型及范围，读取黑板数值；Blackboard._TryGetNumber30847调用System.String.Compare238819并显式ignoreCase=true。当前moveSpeed字段偏移0x8c，AttributeType.MOVE_SPEED=6；typed Enum2Str/FieldMeta列表的call-site usage也有绑定。实际缓存/选择器/热更新执行资格不由名称推断。
- 乘法delegate85073直接调用FP.op_Multiply220471；随后TSMath.Clamp220532，再经WriteAttributesField30792的FP.AsFloat到30791的ObscuredFloat写回分支。float→FP、FP乘法、FP→float的原生指令及两处2^32/2^-32字面量逐字节复核。
- metadata中moveSpeed的custom attribute完整解码为 `AttributeMeta(MOVE_SPEED=6, 0.10000000149011612f)`，ctor30777明确设置m_min与m_hasMin。GetRangeAsTVector2再转换到FP。解码方法复用既有Il2CppDumper v6.7.46的原始实现；MIT许可、解析器源及下载回执随包保留。当前metadata blob独立读取，与旧DLL回执不混用。
- BattleOptions.LoadOptions62946从LevelData.Options.moveMultiplier@0x24写静态MOVE_MULTIPLIER@0x0；Entity.get_moveSpeed66467先读取AttributeType6，再乘该静态值。属性写入与关卡移动倍率是分开的层。

## 已证规则与没有闭合的前提

上述ctor没有明确写m_hasMax；Selector构造器明确赋profession/buildable/side/height四个mask，却没有明确写筛选指针。不能仅凭C#常识把未写标志或指针当成false/null，也不借上一节仍未闭合的GC分配路径。

为继续独立可做的数值功能，本计算明确采用 [PRTS《游戏数据基础》移速章节的固定公开版本440563](https://prts.wiki/index.php?title=%E6%B8%B8%E6%88%8F%E6%95%B0%E6%8D%AE%E5%9F%BA%E7%A1%80&oldid=440563) 所列标准范围（下限0.1、无上限）与独立move_multiplier口径。它和当前ctor的下限参数、关卡倍率读取层交叉一致；公开标准无上限不是原生未写m_hasMax的分配字节证明。原响应SHA、修订号、时间和该章节原文保存在published-movement-source.json。

所有新数值都带条件：所列符文实际完成该字段写入、标准范围/无上限分支适用、没有额外属性修正或特殊控制器覆盖。实际选择器资格、当前范围覆盖、阶段/减速、运动控制器、实际生成与热更新均未证。因此 `rune_execution_verified`、完整有效移速、位置/到达时间始终false/None。没有给未支持的控制器或时间轴补默认数。

## 验收

99项必要检查通过，含15项新API/Qt检查、12个生产引用的预览与目标解析链、FP/float写回边界、两个层次顺序、零与下限、来源/参数/选择器/非法范围拒绝、原damage和历史float目标等级身份保留、源表不变与刷新选择保留。原第075节全部断言继续验证参数/小计/完整值未知；仅将技术说明从“写入层未核验”更新为“写入层已绑定但实际执行未知”。

本机静态原件复核为41方法、5003条唯一原生指令、289个metadata/字段/虚表/typed usage/字面量绑定跨度，其中39个普通方法codegen绑定与2个caller usage约束的generic helper。某些CFG含未知间接调用，只把明确观察到的层次用于条件计算，不冒充所有运行分支恢复。

初次相关检查只缺隔离目录中的公开原关卡fixtures；补齐68份去重公开原件后通过，失败回执在cache保留。期间元数据查询脚本曾因PowerShell扩展双美元字面值而找不到方法，改用方法索引/后缀再核对；未把脚本查询失败当机制证据。没新增私人游戏样本，没有游戏或聊天操作。临时Qt回执不替代父任务原测试窗口和第230节完整范围。

恢复条件：取得实际selector/max分配基线、当前XLua/运行属性覆盖或明确特殊控制器原件时，才升级完整有效移速和相应时间链。P3整体仍未完成。该统一功能未自行分配节数。

# 具体敌人预制体的次数门、冷却覆盖与启动失败成本

本组直接推进 P3 固定敌人控制器/技能资格缺口，不重新计数上一组共享技力公式。普通固定作战预览新增具体次数门及自动目标分项，局外机制查询新增受这些门约束的共享池启动预算，并区分“能力启动失败”和“尚未进入成本请求”。完整实际可用、施放次数、首发与所有时钟继续未知。

## 直接来源与适用条件

10个当前原机 `battle/enm_pfb_*.ab` 的尺寸、SHA256及 manifest MD5逐项相符。23个选定敌人预制体中26个精确 `Torappu.Battle.EnemySkill` 组件通过独立 properties hash绑定当前 MonoScript的namespace/class/assembly；控制字段、所属GameObject名及触发器引用从完整精确读取的对象取得。ABI类名匹配不是依据名称相似猜测子类。所选10包全部对象精确读取；另一个无选定对象的24号包存在非精确对象，未用于任何功能结论。

当前同身份 DLL `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`、metadata `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`的19方法、2173条去重指令、235个字段/方法/参数/vtable/确切调用者泛型跨度已对原文件核验。整个过程只读取源文件，无原生执行、游戏操作、进程内存或私人状态。

资源标识来自[固定原表a550f5e](https://github.com/Kengxxiao/ArknightsGameData/blob/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/levels/enemydata/enemy_database.json)中真实的 `prefabKey`，按已经核验的 defined字段规则及引用构造路径解析。定义false不覆盖；定义true的null仍为明确null，不用数据库ID填补。独立构造只用其明确覆盖，不借数据库；关卡alias不替换prefabKey。原生ResourceRouter和GatherEnemy读取 `LevelData.EnemyData.key`，基础前缀为 `battle/prefabs/enemies`。AB容器的 `dyn/…prefab` 路径和引擎加载/路由/附着仍是实际使用边界，不宣称已经观测到运行中的资源。

`Enemy.OnAwake`的确切泛型调用者是 `Component.GetComponentsInChildren<EnemySkill>(includeInactive=true)`，写入 `m_allSkills@0x450`；这不把非活动子节点标成实际开启。`_AssignSkill`两侧都调用当前culture的 `String.ToLower()`，不是ToLowerInvariant；本实现仅支持当前固定ASCII名且无大写I的稳定子集，其他名称保留未知。`EnemySkill.get_skillKey`经Unity Object.name接口，组件共享所属GameObject名的规则有[Unity官方API依据](https://docs.unity3d.com/cn/6000.0/ScriptReference/Object-name.html)。此为发布的引擎契约，不是实际GetName icall或实例未改名的执行证明。

## 计数及失败顺序

原生 `Init` 明确把 `m_triggerCnt@0x40`设0，不能把该初始化参考当本局实际次数。`get_isUsedUp`在 `_maxTriggerTime@0x2c <0`时不设该计数门，否则按有符号整数 `count>=max`判耗尽；max0在初始化点即不通过。WDRRL两预制体的AOEAttack是1，其余本组选定组件为-1。它与共享技力容量是不同的约束。

`CastToTarget`先确认所需能力，再在 `0x1806dd3e3`调用TryReduceSp；随后 `0x1806dd469`通过Ability虚表槽33调用能力启动，返回true才在 `0x1806dd494`增加计数。Ability槽33声明是abstract，具体实现未冒充已闭合。启动false分支清空关联回调/主能力并返回false，本函数没有立即退还先前成本请求，也不增加计数。后续脚本、其他SP来源、接受/取消或退款仍未知。预算仅在用户明确声明“其他门就绪、基础成本请求被接受、无其他影响”时核算这个即时分支。

原生NeverTrigger的Search返回false、target返回null，组件确实采用它时仅说明不提供自动目标；不意味着不能由其他能力或脚本调用。普通界面明确保留这个区别，不因首个技能冷却0或初池满而预测自动施放。

具体序列化 `_overwriteInitCooldown`纳入原生初始CD分支：非负覆盖包含0，用整数→float32→FP；负覆盖才选数据字段，再经基础period下限0。这里不再把已读到的覆盖说成“未读字段”，但实际正在使用哪个实例/覆盖/时钟仍未知。计数复位与初始CD都是基础初始化点参考，不是出生和首次发动时刻。

## 实际界面与预算入口

当前固定1087引用中22条已绑定所选具体预制体，共26条配置技能，包括全部22条正费用技能资料引用；剩余1065引用未闭合具体预制体。计数是覆盖范围，不是使用率、生成概率或真实敌人数量。

普通预览用中文招式序号、次数门及自动目标描述，标识/原对象/原型门放技术详情。局外机制查询可选择一种预算；与既有resource_plan同时提交会拒绝，避免两个同池账本被误认成一个流程：

```json
{"stage_id":"ro6_duel_1","enemy_id":"enemy_1320_wdrrl_2","level":0,
 "prefab_gate_plan":{"scope":"gated_baseline_skill_starts","requests":["AOEAttack"],
 "starting_counts":{"AOEAttack":1}}}
```

此声明在初池1/费用1的数值门通过时，因为已声明启动计数1且该门上限1而不启动，也不发出成本请求。另可把每项写为 `{"skill":"AOEAttack","ability_start_success":false}`：当此前门通过且正费用请求已接受，则该即时基础分支余技力0、计数仍0，实际施放与后续退款未知。字符串请求表示用户明确声明这项能力启动成功，不是默认实际成功。

共享池的float32→FP/精确GE来源复用229；零/负费不发出技力请求；不加入恢复或时刻；每个招式单独跟踪计数、共用一个技力池。声明计数溢出、未知/重复组件或名称culture、未知池/费用、非法范围等拒绝或保持未知。

## 验收、风险与恢复

117项相关API与临时Qt检查通过且没有排除；验证全部1087引用、具体有限门与技力充足的相互独立、成功计数/失败扣费、NeverTrigger不是绝对禁用、真实大小写映射、CD0覆盖/float32舍入、未定义/明确null/独立构造alias与未来等级、严格声明/溢出拒绝、缓存隔离、普通/技术固定预览与刷新保留。最终新增源复核检查一并计入必要验收回执。原项目可见窗口由root整合核对，临时Qt不冒充原窗口。

初次全包精确断言被无关24号包的对象阻断，改为分别记录全部读取状态并严格要求选定对象精确；没有放宽任何选定字段。初次vtable绑定发现Ability槽33是abstract空入口，已经保留abstract声明/具体实现未知，而非把槽当可执行方法。来源核验不能替代当前实例、热更新、完整相位和目标/模式门；只有取得对应直接来源才恢复这些缺口。

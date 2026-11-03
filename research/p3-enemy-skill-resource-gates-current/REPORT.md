# 固定敌人共享技力数值门与声明请求预算

本功能对应 P3 的固定敌人技能控制器与初始动作缺口，提供直接进入固定作战预览和离线机制查询的条件数值分项。它不把配置当成实际触发，不推算首发、回转、次数或完整技能伤害。

## 一手依据与原生边界

当前原机基包版本 `26-09-13-15-28-10-30688348`。DLL 身份为 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`；metadata 身份为 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。只读取文件，不执行 DLL，不读取进程内存、游戏画面、账户、本局记录或私人配置。

35 个源方法、2897 条去重指令、311 个元数据/普通代码指针/字段/参数/转换常量跨度与当前文件逐字节相符。`native-proof.json`、`selected-metadata.json`、`resource-binding.json` 保留完整审计关系，`verify_native.py` 可在具备同身份文件的原机重新复核。完整文件哈希及字节相符只证明这一基包的静态分支；当前 XLua/热更新等价性仍未知。

固定公开关卡/敌人原件继续使用现有 203/210/224 的已证基包继承与独立构造规则。原件来自 [固定游戏资料 commit a550f5e](https://github.com/Kengxxiao/ArknightsGameData/tree/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/levels)。没有额外使用攻略文字猜测共享池或时序。前置针对敌人技力/初始冷却的公开机制搜索未取得能替代当前原生分支的通用依据，因而未从攻略印象推导新规则。

## 新能力及数值原则

- 原生 `Enemy._AssignSkill` 经虚表槽 15 传入招式数据与同一敌人；`EnemySkill.AssignData` 把 `ESkillData.spCost:Int32@0x24` 写入 `m_spCost@0x3c`，持有 `owner@0x88`。具体预制体子类是否覆盖这个入口仍未知，因此以执行基础分支为前提。
- `Entity.Init` 将整数 `initSp` 和 `maxSp` 做有符号 `min(initSp,maxSp)`，然后整数转 float32，再转 FP，存入共享的 `m_sp@0x50`；本初始化点没有下限零钳制。后续基础 setter 的 `0..maxSp` 钳制另列，不倒灌到初始化。负初始技力保留；超过所支持 FP 范围或容量边界的 float32 舍入明确未知，不填零。
- `EnemySkill.CheckAvailable` 在其他可用门之后读取同一实体共享池，并经 `FP.op_GreaterThanOrEqual` 的 `cmp rcx,rdx;setge` 作有符号原值精确比较。它不使用生命比例比较的容差，技力差一个 FP 原单位也不能判作满足。这里单独报告技力数值门，整体可施放状态仍未知。
- `TryReduceSp` 仅在费用正数时发出负费用 `Modifier.NewSp` 请求，source/target 是同一敌人；零与负费用不发出请求，不推算负费用回技力。其他 modifier 处理、接受与变化均未知。
- 已知共享池与技能费用时，可显式声明 `scope=gated_baseline_sp_requests` 与有序 `requests`。仅核算“这些请求在数值门通过后按基础费用被接受”的条件账本；每项共用一个池，不各自重新分配池，不加入回复/动画/时间，也不把数值门通过次数当施放次数。默认不建立预算，不从真实战斗采集或干预任何行为。
- 初始冷却作为独立技术分项：构造函数明确写覆盖值 `-1`；实际预制体序列化覆盖未知。`Init` 的覆盖条件为 `>=0`，包括零，负覆盖才选原件 `initCooldown`。`PeriodicTimer.Reset` 将 period 下限钳到零，且该调用 `waitFirstPeriod=true`，remaining 初始为 period。原件初始冷却零不证明出生即发动；不推导具体首发/回转。冷却不能转换时保持此分项未知，不抹去独立已知的技力数值门。

## 覆盖、接口与显示

固定 1087 条关卡敌人引用中，1028 条提供共享池及配置技能数值门，43 条 `useDb=false` 独立构造只提供非空覆盖的初始化池，16 条构造池仍未知。43 条不借用数据库技能费用，16 条不把缺失指针当默认零池。配置招式引用总计 450，正费用引用 22；这些是资料覆盖计数，不是使用率、生成概率或敌人数。

普通预览使用“招式1”等中文序号、费用及初始化点数值门，保留完整可施放未知，英文招式标识放技术详情。离线机制页可提交下列公开声明，结果与编辑内容在采样/上下文刷新时保留：

```json
{"stage_id":"ro6_n_5_4","enemy_id":"enemy_10087_hlchgr_2","level":0,
 "resource_plan":{"scope":"gated_baseline_sp_requests",
 "requests":["ForeverEnhance","ForeverEnhance","ForeverEnhance","ForeverEnhance",
             "ForeverEnhance","ForeverEnhance","ForeverEnhance","ForeverEnhance"]}}
```

该原件初始池 7、费用 1，声明条件下前七次数值门通过、最后一次不足。实际次数保持未知；次数限制、完整冷却或具体预制体都可能先阻止施放。可选 `starting_sp` 按 float32→FP 转换；`starting_sp_raw` 接受明确有符号 64 位 FP 原值。二者不能同时提供，超过已绑定基础容量拒绝；不接受回复、时钟或未知技能 ID。

## 必要验证及剩余项目

必要相关 API/Qt 回归范围保留 `test_enemy_skill_resources`、`test_enemy_skills_042`、`test_enemy_sp_inheritance_reference`、`test_enemy_configuration`、`test_enemy_configuration_view`、`test_battle_planning_161_170`、`test_offline_tools_view`。检查 signed 上限而非零下限、整数→float32→FP 舍入、精确费用边界、零/负费用、同池顺序、声明格式/范围拒绝、未知与已证分项独立、全部 1087 引用、普通/技术固定预览、临时 Qt 查询与刷新状态。仅使用公开原件与临时状态，无游戏/聊天操作。

当前实际控制器、实体附着、使能/次数/目标/沉默/眩晕等其他门、预制体覆盖、额外技力、Modifier 接受以及恢复/动作时钟仍未闭合，不能标记完整敌人技能控制器或 P3 完成。重新启动条件是取得这些对应入口的直接来源，而非借相邻机制猜测。

首次 API 检查误用了现有 `enemy_preview` 的调用签名，测试已改为实际三参数入口；随后相关全范围初次缺隔离目录里的公开原件及既有源回执，已从当前公共资料复制并无排除重跑通过。任何准备失败均未影响 root 或更改模型规则。当前原窗口由 root 整合后核对，隔离临时 Qt 可见性不冒充原项目运行验收。

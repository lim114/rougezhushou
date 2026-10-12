# 关卡独立敌人构造、资源别名与局外目标计算

本节闭合固定来源的 `EnemyDataDbReference.useDb` 构造分支，并将它实际用于敌人预览、环境修正和干员对指定目标的局外计算。数据库中没有同名同级条目，不等于这个关卡敌人不可构造；必须先看原引用的构造模式。当前热更新、实际生成和运行中的面板仍未核验。

## 新能力与覆盖

固定公开版本 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 共105关、1087个敌人引用：1028个 `useDb=true`，59个 `useDb=false`。此前缺少精确DB条目的58个引用全部属于后一类。另1个独立构造引用恰有精确DB条目，也必须忽略DB，不能因为它存在就借用。

- 59个独立引用均有覆盖对象。只应用构造器明确赋值和本引用的明确覆盖，不继承DB。
- 原58个缺DB引用中，56个已具备生命、攻击、防御和法抗，可接入原有保密等级/关卡修正和伤害计算，所选目标覆盖残留手动防御/法抗。
- 另2个 `enemy_1303_mhshep_2b` 引用（普通/紧急 `ro6_*_3_2`）防御无明确赋值。构造器法抗明确为0，但防御仍未知。预览可以展示已证环境分项，完整目标计算继续拒绝，不能填零。
- 59个独立引用中43个有非null `spData` 明确整记录覆盖，因此固定配置和已证显式初始化参考可用；另外16个构造指针基线未闭合，SP默认、初动和周期保持未知。
- 59个独立引用的技能与天赋合并基线均仍未知，保留原覆盖作为参考，不借用DB、不声称完整技能伤害或回转。
- 独立资源 `key` 与关卡 `alias` 分开。58个引用的已证别名写入可供技术资料和固定目标身份核对；原型资源不会替换派生敌人的属性。1个引用id等于key，未写alias；其分配默认值不推定为null。

## 原生分支与实际调用入口

读取文件而不加载或执行DLL。基包 `26-09-13-15-28-10-30688348` 的DLL SHA256为 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata SHA256为 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。

`TryGet` 27733@`0x18200bb60` 的参数类型是 `Torappu.LevelData+EnemyDataDbReference`：useDb+0x10、id+0x18、level+0x20、overwrittenData+0x28。27732是另一个DB标识/等级重载，不能用它替代有模式参数的入口。

| 原输入 | 已证基包路径 | 缺口处理 |
| --- | --- | --- |
| useDb=true | GetComputedEnemyData要求精确等级；随后ApplyDefinedData覆盖 | 缺精确等级返回false，不借低级条目或独立构造 |
| useDb=false且overwrittenData非null | new LevelData.EnemyData → ApplyDefinedData | 只采用明确构造赋值与覆盖 |
| useDb=false且overwrittenData=null | 返回false，输出对象不可用 | 不以默认面板或别名补出结果 |
| useDb缺失/非布尔 | 来源格式未闭合 | 不猜true/false |

实际基包调用者不是字符串或bytepattern猜测：Scheduler.Init 72069@`0x1809135c0` 读取 `LevelData.enemyDbRefs`，两处调用该typed TryGet（`0x180913903`/`0x180913b47`），随后取 `get_keyInLevel` 并创建/存放敌人项目。额外NPC引用路径也绑定。SpawnEnemyNpc 72120的CFG保留供核对。metadata方法参数、类型字段、codegen指针与当前文件字节逐项核对。

父任务初始线索里的“比较name、写prefabKey”前提不正确。实际输出 `Torappu.LevelData+EnemyData` 是 name+0x10、description+0x18、**key+0x20、alias+0x48**。非空ref.id与computed.key不同则写alias=ref.id，key保留；31515@`0x182417c00` 的get_keyInLevel按alias是否为空选alias/key。System.String.IsNullOrEmpty238878与op_Inequality238843来自精确core codegen映射，不靠方法名猜地址。

## 默认字段与未知边界

AttributesData.ctor30793@`0x18231b650` 和 EnemyData.ctor31518@`0x182417a60` 证明22项明确赋值。`constructor-default-bindings.json` 逐项绑定metadata字段偏移、赋值指令、typed ObscuredInt/Float转换调用；1和100两个浮点字面量另有文件字节绑定。

明确值包括生命100、法抗0、费用/阻挡/移速/基础攻击间隔1、攻速100、再部署60、生命回复0、技力回复1、部署上限1、嘲讽/重量/基础力度0、元素两抗0、两类命中率1、元素爆发回复速度1，以及扣血1、范围/视野−1。它们是已证构造字段参考；没有据此推断隐藏事件、实际命中/扣血/治疗/技力时钟。

攻击和防御的ObscuredInt结构未在所选构造器明确赋值。免疫布尔、指针列表和未写alias同样没有闭合分配基线。对object-new/allocator做了定向检查，但分支取决于类flag及flag语义，当前没有闭合全部路径和实际类flag。因此不能以C#常识或“通常分配清零”证明所有零/null，不把探索线索用作默认规则。该点仍待新证据，当前候选不依赖它。

已有第203/210节ApplyDefinedData、SP整记录和招式/黑板合并原生回执被复用。38方法中6个旧generic/helper记录保留原回执绑定，没有虚构新的普通metadata方法索引；全部4108条唯一原生指令仍重新和当前文件比较。新/复用普通定义及字段/codegen/浮点字面量共303个字节绑定跨度。当前XLua分支、实际控制器、资源加载、生成时刻和完整技能时序仍未知。

## 验收、失败与适用范围

129项变更相关检查通过，包括14项新测试、所有1087引用分支/原覆盖保留、56个目标实际调用伤害引擎、2个未知防御拒绝、43/16 SP边界、独立构造的精确DB隔离、别名/资源区分、已证环境分项与源表不变性。面板预览参数严格接受布尔值，场景内容不能绕过完整目标校验；已知非法/非有限属性同样拒绝。现有临时offscreen界面检查验证预览文本和MainWindow残留结果清理/比较禁用，没有冒充原项目可见窗口验收。

此次必要选择没有运行一项无关识别页面测试，因为它需要私人游戏样本，且未改识别。未修改或删除该测试，也没有缩减父任务定期全量的范围。父任务应在集成后验证原项目窗口，并在原定第230节执行完整范围。

初次隔离检查暴露了旧“所有缺DB都不可构造”断言、构造器明确默认项、raw投影/有效面板区别与隔离缺少公开历史fixtures。按新原生证据修正旧断言，同时保留所有原字段对照、全部引用数量、真实未知防御拒绝和动态总量未知；缺少的仅公开fixtures补齐。新源封装曾遇到旧generic method_index=None，改为保留旧绑定加新字节核对，不造索引。失败回执仍保留在cache，最终公开必要验收为实际通过结果。

逐字段复核器另发现元素爆发回复字段的说明绑定误指向相邻字段，已按metadata偏移0x2c8改为真正赋值/转换地址；两者的字面数值均为1，数值模型没有因该更正变化。patch初次因原compact JSON没有文件末尾换行而检查失败，已加标准无末尾换行标记，重新检查可直接应用；仍未应用root。generation-receipt中的0.42.0是既有生成器标签，不能当作当前应用版本。

原生复核命令：`python research/p3-enemy-default-alias-current/verify_native.py --game-dir <本机安装目录> --output <临时回执>`。Linux可不传game-dir做公开artifact一致性检查，此时不得称本机文件复核通过。

只修改隔离候选源码/公开回执；未操作游戏、发送聊天、读取私人状态、覆盖本局记忆或修改root tracked文件。本节是一项统一的构造与目标适用功能，未自行增加节数，也不声称P3整体完成。

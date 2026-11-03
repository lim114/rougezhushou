# 梅 MAR-X 当前静态条件伤害链

本组接续第73节的参数参考，新增默认关闭的实际计算选项。已满足 MAR-X 精二40级及以上、1–3阶的梅可手动选择此规则，再在现有局外情景 JSON 声明 `mei_target_motion`：`fly` 表示此时目标满足当前原生 `FLY_ONLY` 条件，`not_fly` 表示不满足，`unknown`/留空保留两种单包候选。基础敌人飞行分类、名字、重量、浮空参数和本局资源不会提供这一声明。

选择后，常态普攻、麻痹弹的单次物理伤害、S2期间普通物理攻击按防御前 `atkScale × 1.1` 计算，并进入现有伤害分项、单次参考、报告与声明伤害预算。技能自身倍率、天赋/模组属性攻击加成已在原输出攻击中结算，本组不重复乘它们。固定条件次数小计沿用原出手预览的次数；实际窗口、完整施放和周期伤害仍为 `None`。取消选择恢复原默认数值；不写培养、本局或私人记录。

## 来源与版本

原参数来自固定 GameData `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的 `character_table.char_133_mm`、`uniequip_table.equipDict.uniequip_002_mm` 及对应三阶 `battle_equip_table` TRAIT 候选。当前只读客户端基准 manifest 为 `26-09-13-15-28-10-30688348`。当前 GameAssembly SHA256 为 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata 为 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`；MonoScript 来源 gmassets SHA256 为 `02266c5aff4a6d7b6e08db5b70acd76cbaf8dc14818bdeaa0c94af04a25efcce`。

52个精确声明类型/方法索引的原生窗口，7514条唯一物理指令均重新匹配只读 DLL 字节，CFG `limits=[]`。4个 AB（equips、char_133_mm、skills、buff_template_holder）的 SHA、长度和当前 manifest MD5 重新核验；gmassets物理 SHA重新核验。没有执行 DLL、读取进程、操作游戏或访问私人状态。

[PRTS梅](https://prts.wiki/w/May)、[PRTS浮空资料](https://prts.wiki/w/异常效果图鉴/浮空)和[May公开条目](https://arknights.wiki.gg/wiki/May)用于定向资料对照，分别支持模组110%及浮空的空中描述。精确附着、目标条件和组合层使用当前原件证明；公开描述不代替当前运行态核验。

## 附着与黑板

三阶 `mm_equip_1_1_p1`、`mm_equip_1_2_p1`、`mm_equip_1_3_p1` 各只有一项 `PassiveBuffAbility`，其 `mm_e_t_10` buff使用 `airforce_enhance` 模板，黑板为空、不strip源黑板。它是 TRAIT特性能力路径，不能套用机械师隐藏 TALENT根的附着路径，也不引入技能索引/地图限制。

`BattleDataConverter._ConvertInternal` 方法77906在 `0x180abdc18..0x180abdc3c` 将 `BattleCharacterData.traitData+0x118` 作为引用传给 `AddEquipTraitData89574`，按装备和培养条件选中模组 TraitData。`Character._AssignData76054` 在 `0x180a34256..0x180a34263` 将同一字段交给 `_AssignTrait76064`；TraitData.blackboard+0x20构造Blackboard并进入特性Ability.SetData。当前梅资源图未带 UnitDataFlowConfig；天赋被动模板只提供已建模的攻击/攻速属性。本组没有为未知的别源黑板覆盖编造语义。

能力创建链为 `_PreprocessEquip76060 → _EquipProcessTrait76067 → AddTraitPrefab89575 → _DoAddTrait89576 → BattleFactory.AttachEquipIfNot71630`。当前 metadata 的最后一个函数返回类型确为 `Torappu.Battle.Ability`；资源图中只有一个对应被动能力。`_EquipProcessTrait` 把返回的有效能力写入 `m_traitAbility+0x4d8`。`_AssignTrait` 对它SetData；`OnBorn76027` 在 `0x180a2d511/545/55b` 读取同一字段并执行 `Ability.Attach(owner)`。通用资源池/组件辅助函数没有被赋予猜测的符号；成功创建当前资源的能力且伤害来源仍有效是明确参考前提，实际创建成功/附着未知。

## 目标条件与物理包

当前模板 `ON_CALCULATE_DAMAGE=14` 顺序是 `IfTarget(TARGET, FLY_ONLY)` 后 `AtkScaleUp(atk_scale, default1, overwritefalse)`。首节点不另检查目标存活/自由/阵营，只要求可取当前目标对象并读取 `get_changeableMotionMode`。ActionUtil按检查结果门控下一节点；倍率乘入AttackInfo.atkScale，在GetFinalAtk及物理防御/最低伤害之前。已有支持的最终受伤修正再于减防之后应用。

`IfTarget99327` 精确类型是 `Torappu.Battle.Action.Nodes+IfTarget`，避免嵌套同名误绑定。MotionMode.FLY=1、MotionMask.FLY_ONLY=2。`Entity.get_changeableMotionMode66374` 可由levitate/groundBound和presence sequence覆盖原始行动方式；这些序号不是秒数/时钟。本实现直接接受“当前条件是否成立”的局外声明，不模拟这些真实状态的产生、退出或顺序。

梅normal mode0的对象 `-1074202291831238505`、S1 replacement对象 `6997003709392759035`、S2 mode1对象 `1461104044418732183` 都是MeleeAttack，并不是按干员职业推测的RangedAttack。MeleeAttack.get_damageType90348读+0x210，当前资产为物理1。`AbstractBasicAttack.DoSetData90309` 的主包 `vslot112/offset0x840 → get_damageType`，再 `vslot106/offset0x7e0 → CreateDamageNode91791`，其wrapper通过 `vslot107/offset0x7f0 → NewDamageNode91792 → ApplyDamage`。这三个slot/offset映射与精确vtable互相核对，虚拟方法对基址为0x140。事件14、有效来源及减防链复用同版已证通用方法，本组重新匹配每条保留的字节。

## 验收与保留缺口

必要检查共71个唯一父测试通过：15个新API、2个真实MainWindow类的临时公开状态窗口用例、54个原梅参数/S1、所选模组来源及机械师相关检查。后续补齐主包wrapper/getter来源后，只复验有变更的15个新API，全部通过。没有降低全量范围；原项目可见窗口仍需root集成后核对。

首次39项中38通过、1旧报告断言失败：它要求“组合层尚未核验”。本组据新原件改成静态已证/实际未知两项独立断言；默认110%不套用、实际空中条件/条件伤害未知、timing不完整及其它第73节约束均保留。跨例首次67项有1个隔离环境缺receipt错误，复制精确公开依赖到base和work后67通过；首次4窗口检查有1个测试字段名account错误，改为现有account_cache.records后4通过。首次记录单独保留，不覆盖。

`runtime_binding_verified=False`、`current_hotfix_equivalence_verified=False`。实际目标行动方式、levitate/groundBound、能力附着、来源有效性、攻击取样/实际命中、S1获取结束、S2时钟和完整技能/窗口/周期均未知。沿用现有十进制参数算术，未宣称逐位复刻单精度转FP/最终取整。新热更新、精确原生回调/相位或已授权实机证据出现时才重启这些缺口；不重复无新lead的查询。

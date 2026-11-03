# 古米与黍GUA-X：独立生命条件及复合治疗

本候选对应P2其余条件模组/多来源直接治疗缺口。它新增两名守护者各技能的实际计算能力，而非仅新增资料查询：合格模组下，用户显式声明固定受疗者生命比例，古米S1/S2、黍S1/S2/S3的已建模直接治疗分项在各自基包条件符合时乘1.15一次，再沿已有受疗因子组合。未声明时保留未含增强的已证小计，受影响非零完整总量/周期HPS未知。原本未知的S1获取、阈值触发、多充能和结束时钟保持未知。自然回复、播种地块回复、物理攻击、生命/防御/技力参数不受本组治疗倍率影响。

## 不能共用描述推断比较门

固定原表a550f5e048bb94e7cdefc6eb97a4091f0c4c7add的两个GUA-X都描述低于50%时治疗提高15%，但当前实际来源不同。新读取char_196_sunbr.ab、char_2025_shu.ab、[uc]equips.ab及buff_template_holder.ab，尺寸、SHA256及manifest MD5均吻合；prefab类型通过当前globalgamemanagers/assets中的唯一MonoScript properties hash绑定。

- 古米：三阶段sunbr_equip_1_*_p1都是PassiveBuffAbility，buffKey=sunbr_e_trait，template=set_heal_scale_by_hpratio。ON_OUTPUT_MODIFIER事件8：IsHeal→IfElse(FilterByTargetHpRatio, MODIFIER_TARGET, LT, useSourceHpRatio=false)；成功分支ModifierScaleUp，失败无节点。
- 黍：三阶段shu_equip_1_*_p1都是PassiveBuffAbility，buffKey=shu_e_002_tr，template=heal_scale_up[hpratio][LE]。同事件8：IsHeal→FilterByTargetHpRatio(MODIFIER_TARGET, LE, useSourceHpRatio=false)→ModifierScaleUp。

共用闭合路径来自215苏苏洛来源的40个当前方法，但本组重新核对原件字节并绑定两名干员自己的原表、ResKey及prefab；没有从苏苏洛复制古米的比较结论。当前比较FP32.32，ONE=4294967296，EPS=42950原始单位。MathUtil.LT method220332使用a < b −EPS，而LE method220333使用a < b +EPS。GetCompareFuncFP0返回s_ltFunc+0x10，1返回s_leFunc+0x18；MathUtil.cctor的编码0x6006b959/0x6006b95b分别绑定两方法。

| 条件原值 | 古米LT | 黍LE |
| --- | --- | --- |
| 0.5 | 不符合 | 符合 |
| 0.499995 | 不符合 | 符合 |
| 0.49998 | 符合 | 符合 |
| 0.500005 | 不符合 | 符合 |

古米最后通过2147440697、首次不通过2147440698；黍最后通过2147526597、首次不通过2147526598。显式十进制比例用native double→FP的乘2^32向零截断，仅是声明参考；实际get_hpRatio的HP/maxHP除法及Clamp01不从游戏显示百分比复原。

追加6个原生方法包括IfElse.Execute99307、LT220332、Heal.NewHealNode91042、RangedHeal.NewHealNode91067及其Event/ProjectileActions；IfElse的_conditionNode+0x10、_succeedNodes+0x18、_failNodes+0x20与分支吻合。古米RangedHeal._useCachedAtkOnly=0（字段+0x208）创建节点分支调用Heal.NewHealNode；两类NewHealNode在真实metadata vtable slot112独立绑定。它们创建ApplyHeal节点的事实不证明投射物碰撞、时间或攻击快照的实际使用。GetProjectileActions中的slot66是PreprocessActionsForProjectile，不能误写成直接调用NewHealNode；本组没有推断它的实际项目调度。

46方法、5532唯一指令、268metadata/字段/vtable/方法指针/比较编码跨度全部重新匹配当前原件。源端module output factor与198已证的三花受疗层分别作用一次。Gummy平底锅天赋更新沿原来的同身份替换，不重复乘原天赋；黍播种层没有进入本组直接治疗。

## 界面和预算

新增guardian_healing_target_hp_ratio字段，以“指定参考”加0–1数值表示；默认未指定，仅合格古米/黍各自GUA-X及本演员已实现技能显示。本字段与苏苏洛healing_target_hp_ratio隔离，不读取自身current_hp_ratio、敌人HP或missing_hp，其他演员/无模组/未达门槛忽略旧字段。古米E2 Lv40、黍E2 Lv60采用各自原始门槛，不通用Lv40。

新比例直接作用现有components及治疗预算单次来源。预算仍使用打开时声明的固定条件，不根据预算友方HP自动重新判断，声明HP、事件也不证明真实友方资格/血量轨迹。未知比例的单次分项为未加增强的参考小计，不冒充完整治疗。

## 验证和集成

15新检查（13API及2真实MainWindow临时公开状态/offscreen）和115现有相关检查，共130全部通过。覆盖两模式、全部5技能、三阶段/潜能、LT/LE原始边界、未知与已知0、跨演员/门槛/非法输入、三花复合及自然回复分层、预算独立条件、报告与专属控件。未读写私人配置/本局状态，未操作游戏、未发聊天。

初始失败保存在receipt：新测试误访问不存在estimate.relics字段；纠正为实际base_stats比较，原有时间/回复断言保留。首次相关runner引用不存在test_condition_cultivation_096，纠正实际test_condition_cultivation后130通过。只读native核验独立通过（5532/268以及4bundle/2MonoScript原件）。

root：`guardian-healing.patch`只含7代码/测试局部文件。先应用小hunk，勿覆盖draft旧整文件；`public/`全部文件复制至`research/p2-guardian-healing-gates-current/`，此路径与EVIDENCE一致。已执行git apply --ignore-space-change --check，不应用root。root持有编号、索引、窗口验证、commit/push和定期全量职责。此稿不计已完节数。

[古米PRTS](https://prts.wiki/w/Gummy)与[黍PRTS](https://prts.wiki/w/%E9%BB%8D)用于描述/模组背景；数值和比较根据各自原表、实际prefab/模板及原生方法。没有依赖论坛推断时钟或把相同文字当作相同代码。

仍未知：实际受疗者获取、当前HP轨迹/存活/范围/治疗时钟，投射物碰撞、技能快照/结束/多充能链，当前XLua热更新，以及本白名单之外的任意多来源叠加。本组不宣布P2完成。

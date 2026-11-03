# 第52节方案预审（只读，待patch）

授权scope：仅 `char_002_amiya`、S1、continuous、敌向普通 interval 参数来源。postcast lifetime>0 或 nonempty target_windows => 旧参数单独留 conditional reference，actual伤害/recharge/cycle未知；empty target_windows=[] 独立数学空源为0。保留独立初动原约定。

推荐实现边界：

- 使用专用classifier/helper；调用点位于 `Combat.plan` 现有 first_damage/伤害modifier处理之后、return之前（大致1242），只分类本scope的regular来源。不要修改共享AttackTimeline、regular、instant或annotate_result的全局行为。full/shown/normal均经过plan，因而一致带pending标记。
- classifier优先级为scope不符 => untouched；life0或range[] => empty；life>0或显式非空range => unbound；其它 =>旧无约束控制。life读取已验证数值，需float转换：现有AttackTimeline验证不会归一化raw options，'0'等数值字符串不能误归未知/跳过零源。
- 每个plan的正/零context由该plan的实际window/duration判断。scenario.window0只对应shown，不对应full30秒。短正窗口即使参考floor hit0也必须actual_total=None；不调用 `preserve_unplaced_sources` 的hit>0判据。零life/[]优先于同时声明非空range/positive life的未绑定判据。
- 在marker之前深拷贝保存已完成modifier后的每击/次数/总量/合成时间参数；marker后合成 times_seconds 不再承担actual事件意义。存储reference须防别名：删actual的合成times或改actual标记不能同步修改reference/input/future calls。

计算与传播顺序：

1. 沿旧算法先完成full/shown、mixed-SP14、normal14秒与cycle44/43000等条件参数计算。不要提前将recharge置None，提前清空会令normal plan不生成，失去旧完整参考。
2. 捕获旧条件参数：初动是动态旧first，不硬编码7；还需留cost/init/natural rate、名义duration。不同rank/培养/潜能/加成都保留其原计算结果。
3. 仅本scope触发已有 `mask_pending_damage(result,full,shown,normal,duration,old_cycle)`。它能识别actual_total=None并清伤害aggregate/hit_counts，同时令complete false；无需改公共helper。
4. 独立清实际recharge/cycle及依赖周期量/率。pending damage helper不会处理SP，也不会因描述性metadata自动清周期；单加note不够。若cycle之后变None，`known_damage_subtotals.cycle_damage/cycle_dps`也需变None，防止报告冒出已计周期0。保留独立healing0等来源量，周期分母未知仍令cycle_hps未知。
5. 本scope设置phase_clock_unbound、resource_and_damage_shared_clock=false及明确未证明的获取/释放/回转原因。不宣称30Hz共享/native时钟。

空源与初动陷阱：

- postcast `target_windows=[]` 和 `target_disappears_seconds=0` 的敌向cast与normal均可0，后续自然-only参考沿已完成life0契约。
- 不能把postcast[]套到precast first从7改15；initial_target_windows是另一个现有前置参数约定，不在52修复。保留旧first对所有rank/培养/潜能/自然倍率的动态值。
- positive-life/native结束未知时，natural30只作独立条件参数，不作为实际recharge补值。
- window0在positive-source情景只说明观察0伤；full cast/后续回转依然未知。非空range即使参考未击中也不推出actual0。

预期patch测试覆盖：positive life .1/1；range[[0,1]]；短正window referencehit0；window0但full未知；life0+nonempty range；life>0+[]；[]；default/no constraint unchanged；frames、S2/S3、医疗/战术阿米娅、friendly与instant隔离；不同培养/rank/potential/自然SP效果保持initial原动态值及参数reference；modifier后的逐击/合计reference；reference/input/future-call隔离；实际report unknown与conditional数值显示。

未修改tracked或draft。本文件只是方案预审，待parent提供patch后再审实际实现。

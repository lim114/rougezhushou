# 有限供靶下的弹药完整施放判定（Source 候选，未应用/未执行）

本候选修复一个完整功能：机械师 S1、凯尔希 S2 因有限正供靶/正敌人生命周期/尾部中断未耗完弹药时，不再把最后一次已有出手当作技能结束；保留当前观察内实际排程输出，非零完整总伤/潜在治疗和完整周期保持未知。不是调整113节观察分母，也不推导新的原生结束时钟。

## 已有依据与可达路径

- `rouge/data/catalog.json` 原技能文字明确机械师 S1 装3发弹药、打完后结束；凯尔希 S2 装10发弹药，手动停止另有实际时刻未知，当前计算未声明停止。
- `calculate_damage` -> `_evaluate_damage_once` -> `_skill_damage` -> `_skill_damage_base`，legacy 两技能都进入底部弹药分支。`AttackTimeline.attacks` 只有选择到目标才出手，`limit=shots` 是上限而非保证。有限正 `target_windows`、`target_disappears_seconds`、尾部 `interrupt_windows` 可返回非空但不满 `shots` 的流。
- `damage.py` 旧判定只检查流非空，便把最后一次已出手 + 原有连击间隔 + 1帧记为 `execution_seconds`。`estimate.py` 随后将此标量当作完整持续，输出完整技能总量并构造周期。
- `operator_engine.py` 同类有限弹药分支已有 `len(primary['release_frames'])>=ammo_rounds` 才给持续，其余返回None。候选对齐已有模型，不宣称游戏客户端实际耗弹/手动停止结束已核实。

## 两处成组修改

1. `damage.py` 完整持续的前提改成实际release数达到既有 `shots`，保留原有足够出手时的末连击 + 1帧公式、粒子与弹道、窗口裁剪。默认完整弹药旧值不变。
2. `estimate.py` 针对明确有限弹药且持续None：非零 full damage/healing 改None，恒零保持0；当前指定观察 window_damage/window_healing仍来自既有计算。没有duration就没有完整phase/cycle。屏障手动持续分支排除；不编造不存在的耗尽/停止事件，也不改变已知瞬时缺靶0输出。

## 独立手算（不是实际PASS）

全用精2等级1、R7、信赖0潜1、无模组藏品、手动基础攻击1000、DEF/RES0、逐帧、明确前后摇0，观察10秒。

- 机械师 S1：基础间隔1.2 + 技能1.3 =2.5秒/75帧。3次出手应0、75、150；每次5粒子，原表落地延迟39帧、粒子间隔6帧；每粒1100。供靶[0,3)只出手0、75，10个锁定粒子在1.3–4.6秒落地，观察11000；旧完整持续错误为(75+24+1)/30=100/30秒，完整总量错误为11000。候选持续/非零完整总量/完整周期None，观察11000不变。敌人3秒消失取消第二次所有粒子，观察5500；同样未耗完3发不能形成完整施放。
- 凯尔希 S2：R7攻击2250，真实伤害单元7875，单目标潜在治疗3825。2.85秒间隔半上取整86帧，10次完整出手0..774，原完整持续775/30秒。供靶[0,3)只有0、86两次，观察15750；声明2位满额受疗目标则观察治疗15300。旧持续错误87/30秒。候选持续/非零完整总伤/治疗/周期None，窗口量与10秒分母保留。受疗0时治疗0仍保持已知。
- 完整控制：机械师单次16500，持续175/30秒；凯尔希单次78750，持续775/30秒，观察10秒4次伤害31500。
- 100秒额外弹道控制：完整release齐全所以完整施放仍可使用旧持续及总量；观察/阶段未落地输出0。不能用未落地的命中数判断是否耗完弹药。
- 连续模式无本次生命周期支持扩展，完整默认旧值/明确缺靶0保持；本候选不发明连续正供靶时钟。

## Root 必须实际验证

封存9个公开API回归方法建议与11项case表。Root先在绑定original运行同cases并保留完整Graph/三个formatter，再应用两处严格替换、新test到tracked，重跑候选Linux/Wine、相关弹药/补弹/时序/治疗/目标范围回归，以及真实窗口。需要核对 Source 的 `event_amounts`/多粒子、受疗0/2、延迟落地、所有默认完整弹药旧图、已知0与其他UNKNOWN。公开报告应显示完整未知及当前观察量；不是完整原生实机PASS。

本agent仅std文件/AST/compile-noexec/散列，没有项目import/API/test/Qt/Wine/helper/native/gzip/Git、没有tracked/private写入。candidate/、transport、public-inputs与test都是待Root复核提案。


## Source v2 更正记录

独立Source审查发现v1的kaltsit-empty_control案例同时声明受疗2，会触发友方fallback、足够出手10发，不能作为“完全无目标”的未知结束控制。v2将此负例受疗设0；新增友方受疗2完整控制，完整潜在治疗76500，frames窗口治疗30600/continuous22950且持续仍已知。v1保留，production两块候选字节完全相同。新9方法测试含此控制。

本次对当前观察量的保留承诺限定**显式window_seconds**。没有显式window且供靶不完整时，既有未知duration路径默认window_seconds=0，window_damage=phase_damage=None；顶层已有排程量保留但不称完整单次技能，不额外推导默认窗口。今后若要新的默认窗口UI/API规则，另需明确语义；不能把本Source修改描述成已经实现该项。

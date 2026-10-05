# 0.70 酒神 S1 普通动作派发链

静态磁盘读取安装 GameAssembly.dll / metadata；未执行游戏 DLL、读进程、操作游戏、读私态或发送聊天。3份完整 CFG，8方法1330条指令由 verify_sources.py 逐条核对源字节。实际 skchr_phatm2_1.prefab 的 _splitDamage=0 复用0.69固定资源原件。

OnSpellStart先取 event=4 的MeleeAttack.GetEventActions，再走DoCastOnTargets，对合法目标调用OnCastOnTarget；后者调用MultiMeleeAttack.DoApplyActionsOnTarget。实际未分割伤害分支直接进入AbilityStandard.DoApplyActionsOnTarget，使用generalActions与mode=2调用ActionUtil.RunActions。

RunActions先取上下文快照，再同步迭代动作表，核对mode及CheckExecute后调用动作Execute。该工具层没有新增协程等待，也没有额外段间帧。实际CreateDamageNode、元素节点/天赋数据流由phatm2-damage-070独立核验，不能仅由工具同步派发推断未查的所有动作都即时产生伤害。

此链不证明当前热更新等价、绝对首伤帧、技能完整结束或技力观察相位。不得从列表顺序、展示顺序或ON_SPELL_END名字推猜其它事件机制。

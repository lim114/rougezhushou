# 遥 BLS-Y 的当前静态治疗人数链

新增能力为明确选择的潜在普通治疗人数组合，已接入实际技能计算、原有受疗人数控件、治疗分项及报告。默认关闭，旧第049节的两名已计/第三名独立未知来源路径继续保留。

原参数固定为 a550f5e048bb94e7cdefc6eb97a4091f0c4c7add。当前 DLL SHA256 583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5，metadata SHA256 d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f，AB manifest 26-09-13-15-28-10-30688348。46 个当前方法的 7999 条独立指令、3 个 AB 和 globalgamemanagers.assets 已以物理原字节/manifest 重新核验，仅只读，不运行 DLL，不读取游戏进程。

三阶模组均 TRAIT_DATA_ONLY，resKey 为 null，并不存在可借用其他干员原件的模组被动能力。转换后的 trait data 通过 prefabKey -1 进入当前 Character 的 trait talent。当前 metadata 的确切调用参数、Dictionary<string,TalentData>.TryGetValue / set_Item 的 MethodInfo、helper CFG 和三项泛型实参互相符合；不是从未知 helper 地址猜符号。静态泛型 ContainsItem<int> 的 classInst 为 -1，methodInst 为82；首次拒绝 classInst>=0 假设的回执保留。

当前 char UnitDataFlowConfig 的第2项限制 mainSkillIndex=1，formula THREE / type ADDITION 读取 TALENT -1 的 attack@max_target_heal 和 SKILL 的 attack@max_target_heal_add，再覆盖 SKILL 的同名增加键。原生 _ModifyBlackboard 在 0x180ac00ff..0x180ac0109 加两个明确源值，在 0x180ac00bc 写回；不会再加旧 target 值。公共 rank1–6：2+0=2，rank7–10：2+1=3。

_AssignSkill 的 GetDelta → BasicSkill.AssignData 的 Blackboard.Union（第二源覆盖第一源）→ attack@ prefix → mode2 的技能 attack blackboard → Character 最后合入 skill → UnitMode.OnInit → selectable / parallel groups → AdvancedSelector.SetData，形成完整的当前静态传递路径。S2 selector 精确键为 max_target_heal_add；S1/S3 直接读 max_target_heal。selector 直接覆盖其 m_maxTargetNum，默认1名不是额外加数。OnPostFilter 将该上限传给过滤器，不证明实际获取到了上限数量。当前同对象 UpdateHealScaleByTraitData 从 Character.traitBlackboard 读取 heal_scale=.75，OnCastStart 应用缓存值；此绑定不证明回调已经发生。

可选路径将三名潜在受疗者放入同一“护佑者普通治疗”分项；观察窗口与出手数沿用已有局外预览。例：1000攻击、S2 rank7、三名声明、10秒既有帧预览，普通治疗条件小计为 750×18=13500；已覆盖20%治疗倍率后为 900×18=16200，倍率只使用一次。S2 派生伤害按现有每名受疗者邻接当前敌人的条件列小计，不能从受疗人数推断邻接；敌方零生命周期不会取消独立友方治疗。浮泡破裂及浮空保持独立来源和未知时钟，不按普通治疗人数再倍乘。

当前静态绑定和组合已证；runtime_binding_verified、热更新等价均为 false。实际当前 trait 成功使用、可受疗友方集合、健康过滤、获取/回调/攻击快照及完整施放/观察/周期治疗总量均为 None。原有时间列表明确为出手预览，不改成客户端事件。没有新战斗事件输入或实时站位分析，战斗触发藏品未恢复数值化。

公开布局只用于 MethodSpec 三个 int32、MetadataRegistration 和 GenericInst 的结构核对：[Il2CppDumper 原件](https://raw.githubusercontent.com/Perfare/Il2CppDumper/master/Il2CppDumper/Il2Cpp/Il2CppClass.cs)。该内容已读取；GitHub API 提交查询断连、web API 入口不可用，精确上游提交为 null，失败保留，不把公开布局来源当业务机制证据。当前业务绑定依据上述本地固定资源和原字节。

新15项测试与旧67项遥相关测试通过；新增源入口修改后的27项必要跟进也通过，其中13项旧模组资料约束未删除。首次测试的非法模组等级/错误窗口键样例和报告对象路径错误均保留原失败，按现有接口修订样例后通过；没有改变原有约束以迎合新功能。真实项目窗口由 root 合入后按批次安排核验；隔离临时 MainWindow 的两项新增检查已经通过且账户/本局记录保持不变。

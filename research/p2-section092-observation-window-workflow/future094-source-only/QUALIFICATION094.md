# 94 候选：既有离线情景输入的刷新完整性

这是一份实际第91节 `59961ec3d633ac91b01014fb06b357d45e5979f7` 的静态资格审查，不是第94节完成或运行结果。只读取固定 Git 原件和当前匹配源码；项目 import/API、Qt、Wine、tests、network 和 tracked 写入均为 0。文件只在 `.continuation`。待根代理提供真正完成的第93节 Git 对象、重新确认相关源支持后再准备代码，不能把92未执行候选或93负证当完成基线。

已确认一个可以共同实施验收的完整组：13 个可编辑、已经在 calculate 中读取并被现有消费者使用的情景控件，只有缺失自身刷新信号这一共同问题。

| 输入组 | 原控件 | 现有读取字段 | 当前信号事实 |
| --- | --- | --- | --- |
| 培养/目标情景 | deployment_elapsed, healing_targets, defense, resistance | deployment_elapsed_seconds, healing_targets, enemy_defense, enemy_resistance | 4 个都没有自身 valueChanged 刷新连接 |
| 银灰 S3 情景 | cooperative, fragile | cooperative, preexisting_fragile | 2 个都没有自身 toggled 刷新连接 |
| 机械师 S3 情景 | charge_count | charge_count | 没有自身 valueChanged 刷新连接 |
| 机械师 S2 情景 | shield_breaks, shield_duration_known, shield_duration | shield_break_count；后两者共同决定 skill_duration_seconds 是否包含及数值 | breaks/duration 无重算连接；known 唯一 toggled 仅 setEnabled |
| 银灰 S2 情景 | activation_count, companion_attack, stacks | activation_count, companion_attack, deployment_stacks | 3 个都没有自身 valueChanged 刷新连接 |

共 10 个数值控件和 3 个布尔控件，逐个创建、范围/默认值、已有身份条件、读取和信号证据见 control-matrix094.json 与固定源码摘录。number() 仅创建、设置范围/小数位/默认值并返回，没有通用信号供应商。OPTIONS 循环只连接它创建的新控件，并显式跳过 healing_targets；其中浮游单元的另一个 deployment_elapsed_seconds 控件也不是 self.deployment_elapsed，不能把同名字段当同一 widget。没有 foundChildren/eventFilter/on_* 或 connectSlotsByName 等另一套这些输入的公共重算机制。

合同要准确限定：手动“计算属性与技能预估”按钮原本可重新读取所有这些字段，源码并不证明应用曾承诺每个输入自动刷新。第91实际 grouped design 明确将 continuous_attacks 的缺信号列为“输入改变后旧结果可能仍显示”，采用已有 OPTIONS 的自动刷新模式并已完成真实窗口验收；这提供同类离线预览流程改进的正合同依据。当前审查证明 13 个相同生产者缺连接，不冒充已运行 GUI stale-result 复现，不声称原按钮设计错误或数值机制错误。实际信号、调用数和结果仍需根代理的 focused MainWindow 验收。

最小完整改进只给现有 10 个 valueChanged、3 个 toggled 增加当前 calculate 回调。应在所有原默认设置、范围和必要输出控件构造完成后统一连接；不得调整数学、当前培养/模组选择、输入默认、上下界、显示、reset、持久化、资源观察或后台事件。shield_duration_known 原有 setEnabled 连接必须保留，unchecked 时既有 calculate 明确不提供 skill_duration_seconds；无已知时长时自然结束未知继续保留。新回调不能把声明冲锋/破屏/部署事件视为真实事件绑定。

需要联合保护的边界：

- 更新技能时 healing_targets.setMaximum 已 blockSignals；保留该阻断并依靠原 update_skill_options 末尾刷新，不能叠加任意假定的调用次数。默认 fragile=True、其余现有 count/default 不变。
- 这些控件现有可见性仅表示可编辑情景范围，隐藏值继续保存于原 widget。固定关卡敌人让手动 defense/resistance 隐藏和 disabled；现有 enemy_environment 覆盖情景的防御/法抗。返回手动目标保留原值，不因自动回调清空/复制它们。
- None 干员、未实现档案、无所选技能仍走 calculate 现有早返回和清 damage_result；calculate 开头已同步动作/个人强化，不能声称全路径零 helper。异常仍清结果并显示原信息，特别是已有零窗口声明正冲锋计数错误；修正输入应通过同一现有路径恢复。
- 只有预览控件改变，不调用 run.apply/reset/save、采样、游戏连接或聊天。calculate 的 RunState 资源/库存/历史投影是读取，预览缓存和报告会变；不据此宣称整个启动无副作用。RunState.__init__ 的原记录修复可保存、正式 main() 会开启自动采样，必须继续用临时空状态、构造 actual MainWindow 而非正式 main。

已排除的负证：elite/trust/potential/module/rank 是 QLabel；可编辑 level 和 skill 经原信号→update_skill_options→calculate，培养来源和观测→update_operator 已刷新；固定关卡/敌人也已经刷新。第91 continuous 回调和第92 window/limit 回调与 report 长度候选排除在此组外，不能再次算完成工作。

未来验证计划见 acceptance-plan094.json。它仅描述原生当前输入/来源分项/状态/错误/文本的验收关系，不提供未经源证明的新数学预期。真实第93源核对和独立审查之前没有候选代码、API 探针、formatter、tests 或窗口执行。现有045测试只读取培养/目标刷新与模拟选择保存的合同，未重跑；已有91 PASS属于91的完成记录，不是本包验证。

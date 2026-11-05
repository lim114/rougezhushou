# 维护：技力条件扫描去重与单次状态包装内联

periodic_charge_seconds复用同一次attack_sp求和结果判断条件相关性和生成事件；Combat自然充能路径只扫描一次attack_sp是否存在，不再在active回调和后续条件各扫一次。先核对calculate_damage的准备入口：relics.prepare重新构造并写入_relic_rules，内部计算消费已生成的规则。本次未添加坏规则兜底；直接向内部函数注入损坏私有规则时的错误先后不作兼容承诺。公开入口31情景完整结果/错误一致，包含21成功和10条相同的continuous_attacks文本拒绝。

移除在用源码/脚本/测试中没有调用者的calculate_extended包装；历史归档不改。阿米娅source_state仅供preserve_plan调用，先把状态转成字符串再解析；现直接在唯一消费处判断，保留原数字零、空范围、正生命周期和无约束语义。没有加新辅助函数或保护。

54项定向检查全部通过，原输入不变；raise/try节点、Combat其它方法和阿米娅attach_result AST保持一致。D102登记attach_result与唯一调用方的重复存在检查，尚未删除。charge_reference完整阅读并核对生产者与消费者，域条件与非负伤害算式不是异常兜底；该模块三条源码审查完成，不代表碰撞机制新增实机证据。其余大模块只记所列路径。

原测试窗口正常关闭重开，工具条可见且响应；原始输出和截图仅.local。未跑全量、不操作游戏、不发送聊天。本批为维护，继续审查尚未覆盖的计算、资料与运行模块。

[进度](PROGRESS.md) · [待审核清单](../../../../docs/reviews/pending-defenses.md)

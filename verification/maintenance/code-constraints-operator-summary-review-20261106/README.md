# 维护：干员摘要与资料契约

operator_summary完整回顾：cultivation参数从未使用，删参数并删除app唯一传入处的training_conditions构造；training_conditions仍被实际计算调用，未删函数。已知trust_display分支直接读取，不再次走value的缺字段判断；invalid_skill_ranks在遍历前读取一次。value服务多字段，保留。缺字段、未知技能与未公开模组属于实际识别状态，保留。

drone_traits/public_event_samples/player_exchange_sources全文已读；前者仍有培养条件重复读取，未把普通规则标完成。三个资料资格/错误处理D315—317待审。app仅阅读摘要分支及training_conditions，不认证全app。_eligible、_values和_node_description实际有多次调用，不乱内联。

7项定向通过0.034秒，16组旧新摘要文字一致，源码/测试16个格式化调用均只传一个位置参数，app编译通过。未执行全量，未重跑未改模块的旧产品验收。测试窗口更新并确认可见/响应，截图本机保存。

覆盖完整63、部分203、仅异常40、结构252，共558；待审280组D38—D317。

# 第 88 节冻结产品提案

固定第 87 节 HEAD `1ce970fd30aa3b42d8ef787cde02513f05682b66`。已有来源复现 16 公共请求及 48 显式格式请求保持原件，不重复。生产范围只处理 `continuous_attacks` 实际消费者的文本条件：有效 str 在既有 core 计算、finishers、完整报告和 83–86 guards 成功之后明确报错；bool 及其他旧非字符串真值、inactive 字段和旧错误顺序保留。

新增叶模块 `rouge/condition_inputs.py`：一个 `ContextVar` 保存 `None/False/True`，无共享可变 collector。读取 helper 返回原始 get 值，不写用户 scenario、public result 或 catalog。私有 core 由 decorator 建立独立上下文，在返回之后检查收集到的有效文本，`finally` reset；嵌套、线程及 phase/deployment 的每次 core 调用隔离。单独使用原计算 helpers 没有 collector，继续原行为。

12 处旧读取逐处替换，保留短路和原数学表达式。engine 自然回复普通 owner 的语法 get 仅当真实 attack-SP rules 存在才记录；谓词只对 scoped str 延迟计算。event-SP 的 get 仅 native_attack>0 记录；incoming-only 或零 outgoing 不据语法 get 扩资格。periodic timing 的 incoming_interval 优先支路保持，outgoing 分支仅有效增量>0 记录。其他读取位于原 Attack-SP、阿米娅自然回复或实际 restricted reference 分支。末端 wait_next_attack 的旧真值仍原样，不自行推断原生时钟、友方攻击资格或新增游戏机制。

运输只新增叶模块、一个新测试文件及五个消费模块的 import/读取替换，加 damage import/decorator。所有原文件按 CRLF 保留；静态逆变换必须恢复固定原字节。只冻结维护中的 rouge py/json 与必要 tests 支撑，不复制缺失历史缓存或庞大 research。

预算：一个事先固定的 **60 个唯一 public 输入对 / 120 次 old+draft 公共请求**；每个成功结果保存编码前完整 native tree、完整 JSON 和 estimate/user/technical 三个显式文本请求，caller/catalog 严格隔离。保存复比 0 新调用。另 **8 个有意义新测试方法**，最多 32 次显式公共请求、最多 32 次显式 context/helper 请求，使用 function-entry instrumentation 给出实际数量；不虚构测试内部总调用数。没有旧成功测试、full、Qt、Wine 或随机补例。范围包括 legacy/extended、frames/continuous、E0/E1 阿米娅受限参考、natural hidden/inactive、实际 attack-SP、periodic/incoming/event/zero outgoing、非字符串别名、旧错误及 83–86 先行、私有上下文隔离。

这份提案是产品执行前冻结。输入计划将在任何公共请求之前保存，预留预算不增加；准备错误保留。根负责 tracked 集成、fresh related/selected 和第 90 节全量。

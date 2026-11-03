# 第 88 节独立来源准备

此包只读源码、AST 与已经保存的来源 16 请求。没有新 calculate_damage、Combat、charge、timing helper、formatter、测试、网络、Spine reader、Qt、Wine 或 tracked 修改。所有第 87 节原件保持。

当前基线为第 87 节 `1ce970fd30aa3b42d8ef787cde02513f05682b66`，相关七个 producer/core/consumer 文件与第 86 节来源包所绑 bytes/hash 相同。独立保存复核验证来源包 24 件及原封清单/hash、gzip 解压绑定、16 项 caller/catalog 类型树隔离、完整原生树/JSON/三文本。三个 active 控制和一个 inactive 控制成立。这是旧来源保存复核，不是本节 fresh API 验证，也没有重新运行来源 16 请求。

五个消费模块的 12 个 literal get 逐项与旧完整 AST 清点相符。Qt producer 是 rouge/app.py 的 QCheckBox、默认 True、isChecked bool；其只在攻击回复时显示并不能定义自然回复、事件回复或报告元资料的 API 资格。

实际资格须分开核验：

- legacy estimate 只在原攻击回复分支、对应帧回转分支和攻击回复 normal-count 分支使用该值；纯自然回复 silverash S3 来源控制完整不变。
- extended natural Amiya 分支用于额外攻击技力、参考 notes/时钟。E0/E1 尚未取得某天赋数值不自动取消该实际分支。受限 continuous Amiya S1 attach_result 还把原真值写入 attack_sp_enabled_in_reference；最终 actual cycle 未知不抹去参数来源或这个公开消费。
- extended generic natural 分支 get 在 any(attack_sp rule) 前面，不能仅因 getter 被执行就校验所有自然回复 owner；有效 attack-SP 来源才限定此处。原短路及数值表达式应保持。
- attack-SP 分支、frames recharge、continuous deployment-rule recharge 和有可用 cycle 的 normal gate 均有原条件；调用发生过与最终有完整时钟需要区分。
- periodic_charge_seconds 的 incoming_interval is not None 分支优先，包括 0；该分支不读 outgoing continuous 条件。后续 wait_next_attack 只在已建的攻击槽里选择，不以此字段选 readiness。有效增量资格应只收集真正 outgoing credit 分支，不概括为所有 periodic/incoming。
- event charge 的 native_attack 汇总包括原生攻击回复、传入 attack_sp 和已解析 attack-SP rules。native_attack>0 才使此字段控制 outgoing credit。仅有 event-SP/received-SP rules、native_attack==0 且 wait_next_attack=False 的普通 incoming-only 请求不是这项消费。
- 另有真实 event 尾端消费：ready is not None 且 wait_next_attack=True 时，原 raw attacks 决定 ready 是合法下一攻击槽还是 None，即使 native_attack==0。Gummy/Shu/Mizuki/Gnosis S1 的原表为自然回复且计划分支 mode next_attack，来源层面不能把所有 native0 使用都称 inactive。作者/root 已接受同节补充 observer：首 get 仍限定 positive outgoing，尾端仅实际到达时观察已有 raw 值，不增加 get、不把 readyNone/early return 提前校验。此补充待最终 draft/fresh 风险用例独审，不能由本准备包宣称实现通过。

当前读取的 condition_inputs.py 仅为作者尚未冻结的 preview，未执行、未纳入 final 结论。应在正式冻结后核验：不可变 ContextVar(None/False/True)，无 mutable collector/用户输入 marker；读取返回原始值；standalone helper 没有 scope 时保留旧 truthiness/返回和错误；core 成功且旧 finishers/report/83–86 guards 结束后才拒绝有效 str；所有路径 finally reset(token)，嵌套请求复原原 token，而非全局 clear。context/helper 请求和 API 请求必须各自真实计数。

旧错误合同以 `_prepare_damage` 的 skill/rank/培养/解锁/旧文本与 count 校验、prepare_run/relic/rune、raw timing 验证，再到 Combat/legacy estimate、annotation/finishers/report 和 83–86 guards 为依据。该设计只承诺本次 core 的既有错误先行；phase/deployment 外围和多次 core 的跨阶段错误不能无证据概括为所有 outer 错误先后。等待作者保存 exact old errors 与独立 fresh 风险结果，source-only 不冒充数值验收。

原生时钟、附着、友方获取/阈值、多充能链、真实回转/阻回和热更新均仍未知。本节是输入类型合同，不添加 SP 数学或 game clock。第 87 节 Back/reader/render/EOF/原失败根因与本节无关。

来源 16 的格式 ledger 只计 48 个显式三文本请求，未 instrument 实际内部 entries。本次准备是零 formatter；未来正式 fresh 结果须保存 native before JSON、完整 JSON 与三文本，明确显式请求和实际函数 entries，不能借用第 87 节或旧来源 16 数字当作新的验证。

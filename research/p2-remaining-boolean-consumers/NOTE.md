# 第 86 节剩余布尔条件输入草案

根基线为 `9ef5a469673502754db3be320a8eece9a7fd18d4`，完整维护源码 723 件由固定 Git 对象冻结。原 28 件来源预备和 17 件独立来源审查保持原字节，本轮未重跑旧 36 次调用、240 个技能等级或 12 个模组来源审计。此包仅为外部草案，根代理独占 tracked 应用/提交。

在既有计算、finisher、报告及 83–85 节类型保护之后，仅拒绝实际生效的 12 个字段的字符串。非字符串维持既有 truthiness；闲置 owner/技能字段继续忽略。水月采用实际选中“反移情”，强击瓶采用实际选中天赋，梓兰 S1 附加箭和四处 SP 消费保持原参数。没有新倍率、计时、概率、附着规则或输入文本解析。

祥子 ranged 条件采用本次 `Combat` 的局部属性，`calculate` 入口重置，实际 normal 赋值后记录。既有 module/颂乐音符 max_cnt>10 的技能覆写与实际 normal 执行决定资格，不读用户 `_internal`、不把信号写入 scenario/public/caller/catalog。原 `calculate_extended` 包装保持原内容。S1 无绑定音符来源在 normal 之前就把 duration/recharge 置空；S2 switch 不建立周期；S3 还受 continuous gates 控制。保存矩阵第 263 行部署酒类+continuous=False 有最终 cycle=150 但 normal 不执行，证明不能从最终 cycle 倒推资格。保存案例没有证明 S3 实际 normal 已执行后最终 cycle 变空，不宣称这种案例已测。

作者相关检查：baseline 114 项通过；draft 首轮 122 项中既有 114 项及新增 7 项通过，另 1 项错误地预期 S1 normal 会执行。原测试/日志/诊断保留，产品没有为此改变；修正后仅定向运行这一项并通过。最终 8 个方法的证据由未变 AST 的 7 项和定向 1 项绑定；不称重新运行了完整 8 项。Unittest runner 未采集 API 数，旧诊断中的 183 是源码推算而非 instrumentation；不得用作实测调用总数。

当前基线与草案的有界矩阵有 268 对独特输入，各 268 次 public 调用，共 536 次明确编号调用：71 个合资格字符串变为准确 ValueError，181 个接受结果的完整预编码类型树、完整 JSON 和三个报告逐项一致，16 个旧错误类型/文字完全一致。所有调用者与目录对象保持隔离；非有限 float 输入保留原类型和 float hex，仅其原输入 JSON 表示使用明确标注的非有限值对象。格式化器共 1299 次，目录隔离 cache 读取共 538 次，分别计数。

另有 8 对隔离内部 core 记录：显式 prepare helper 共 8 次、core helper 共 16 次，public 调用为 0，格式化器 42 次、目录 cache 读取 18 次。6 对完整接受结果/三个报告一致，2 对合资格字符串拒绝；prepared clone 的旧有修改也逐类型一致。phase 参数 0/7 仅证明内部隔离 core 兼容，不代表公开非部署相位 envelope、实际 Wine/原生 Windows 或游戏 tick 验证。

gzip 结果保留压缩/解压字节、SHA 与完整保存结果，比较本身新增 API/helper 均为零。两处产品文件保持 CRLF，新测试 LF。根注册模块建议 `tests.test_remaining_boolean_condition_text_input`。作者 patch 已对根基线 apply-check 通过；独立产品审查未完成前此包不是可应用最终交接。

旧错误优先结论限定为 source order 以及实际检查的培养/技能/数值/timing/旧类型错误和保存案例，不推断所有可能外层错误路径。完整 clocks、原生附着及未覆盖规则保持未知。本节未执行 Qt/Wine/游戏/聊天或修改根仓库。

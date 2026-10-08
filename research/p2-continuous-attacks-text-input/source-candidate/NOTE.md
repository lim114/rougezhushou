# 第 88 节候选来源审计

推荐实际产品问题：共享 `continuous_attacks` 条件没有文本类型校验，字符串 `"false"` 会在既有消费者中按真值计算。不是新增游戏机制，也不根据 UI 的显示范围扩大 API 校验资格。

当前进度、工作断点和 checkpoint 的原件已保存。审计开始时固定 Git HEAD 为第 85 节全量后的 `9ef5a469673502754db3be320a8eece9a7fd18d4`，调用使用已批准的第 86 节工作树产品字节；84 个生产 Python 文件和两个 catalog/profile 文件在 16 次调用前后 hash/bytes 完全相同。第 86 节的独审 39 件和后续 test migration 补包均未改。

完整当前 AST 清点为 **12** 个 literal `.get('continuous_attacks', ...)`，非初估的 13：extended engine 6、legacy estimate 3、periodic timing 1、event SP 1、阿米娅连续参考 metadata 1。`QCheckBox` 默认勾选并输出 bool，UI 只在 attack-SP 显示该行；自然回复阿米娅、自然技能带 attack-SP 来源、event charge 等 API 路径仍可能消费此字段。training、scenario preparation 和 timing 数值验证没有现成的该字段 str guard。

根授权的 16 个来源复现请求只执行一次，四个领域各取 `False/True/'false'/''`，全部成功，无补充随机病例、重试、测试或产品草稿。前三组（legacy 机械师 S1、合资格模组祥子 S3、自然回复阿米娅 E2 S1 continuous）False/True 整份原生结果不同，文本 `'false'` 的完整原生树、JSON 和三文本准确等同 True，空文本准确等同 False。无事件/attack-SP 来源的 legacy 银灰 S3 四值全部相同，是一个实测 inactive 控制。

机械师 S1 False 的初动/回转/周期均未知，文本 `'false'` 却分别得到 8.433333333333334 / 8.433333333333334 / 16.766666666666666 秒；祥子 S3 False 同样全未知，文本分别得到 8.566666666666666 / 44.833333333333336 / 69.83333333333334 秒。阿米娅 E2 S1 的现有算法参考为 False 15/30/60 与 True或文本 6.000000000000002/11.2/41.2。这些是当前软件来源复现结果，不证明原生游戏时钟。所有 caller 原生类型树及 catalog 缓存原生 hash 保持。公共输出在编码前保存完整类型树，并经独立保存 decode/reencode 绑定 JSON。

格式 ledger：16 公共调用，16 成功，每项 estimate/user/technical 三个**显式请求**共 48 个（16 format_estimate、32 format_report）；未 instrument 内部委派/总函数 entries，不把推导数量冒充实测。隔离验证显式 catalog 缓存读取 17 个另列；无显式 prepare/core/selected_talents helper、Qt、Wine 或 tracked 修改。

最小产品范围必须保留 contextual 资格与原错误：attack-SP 的原初动/回转/normal；阿米娅自然回复和受限连续参考；真正参与自然 attack-SP 合成或 event charge outgoing credits 的来源。`sp_events.charge` 中 native_attack>0 才使本字段影响 outgoing credits；仅有 event-SP 规则、incoming-only 或 0 outgoing credit 不能自动视为 active。`periodic_charge_seconds` 的 incoming_interval 分支会先于 continuous outgoing 分支。原语法 get、UI 隐藏、最终周期 None 都不足以证明全局资格或无效性。

下一步由根授权产品作者查完整 actual-consumer union 后制作一个连贯修复：保留全部原训练/数值/时序/报告以及 83–86 guards 的错误先后，在真实 active 条件消费者对 str 明确拒绝；合法 bool、已有非字符串别名、实际 inactive 字段和 unknown 时钟均保持。产品验证还需有界覆盖 E0/E1 阿米娅受限参考、periodic/received-SP/incoming-only 分支、旧错误优先与 caller/catalog 隔离。这 16 项不声称已经覆盖上述分支或所有 owner/skill，也不代表第 88 节产品完成。

其他候选：SP倍率/负值来源子审没有确认新 bug，现 6 个 active SP 规则均为正值，原倍率/负值 native 组合仍未知；只封阴性，不计产品节。魂灵之影培养来源第 74 节明确只覆盖两本体路线、covers_all_routes=False，不能用未解锁这两条推出不存在其它附着后强行 gate。真言 S1 同击已有当前未知保护，未确认缺失 guard。87 Back 恢复和 090 UI 不重复；crew_count False 的潜在完整列表误判另交独立 89 来源线索，不混本节。

只读猜错路径的准备诊断、初版 source count 纠正、已成功执行的原静态脚本均保留。最终 v1 manifest 每件含显式路径/长度/hash，自身不自列；保存比较没有重新调用项目。

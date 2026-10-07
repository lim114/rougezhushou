# 第67节：堕梦次数 metadata 与整数查询保持一致

固定基线为 clean `0d446fc3523fd09452c84f65c133d23f33b31696`。只读审计及原1620次公开调用完整 JSON/错误保存在 `prior-readonly-audit/`，原始目录 `/workspace/.continuation/p2-incoming-count-report-audit-067` 也完整保留；其 `patch_written: false` 表示历史只读阶段，不是本修复最终状态。

酒神三个技能都先使用 `Combat.option(enemy_attack_count, 0, maximum=10000, integer=True)`，支持有限、范围内、整数数值的十进制/科学计数文字，并在实际查询处拒绝 raw bool。pending gate 已正确使用解析数值。之前创建 `neural_incoming_reference.attacks_requested` 时却重新 `int(raw)`，导致合法正文字 `1.0`、`1e0` 等在有 pending source 时抛出 ValueError，阻断整份公开报告。

仅将这个已成立的 metadata gate 内的转换改为 `int(self.option('enemy_attack_count',0,maximum=10000,integer=True))`。已有 parsed incoming 仅是 `plan()` 局部变量，在后处理方法无法直接访问；复用同界限 option 查询避免增加 plan 返回字段或全局策略。没有修改 pending gate、全局 validator、数值伤害、phase/scope、None、神经事件或原 native 未知字段。bait 与 Wisdel 后处理分别归其它小节。

通过 fresh 1620次 draft 公开调用与 source-pinned 完整原结果配对：180个合法正别名原 bareint 错误恢复，每个完整输出都精确等同其原有整数控制；1440个完整旧结果或错误完全不变（其中520个原错误继续保留）；528个整数别名 pair 修复后完整相同。包括 S1/S2/S3 × frames/continuous、默认/零/短/10秒窗口、target life0、空target_windows、免疫、River、E1未解锁及4种其它owner inactive。所有 caller输入保持不变。`paired-full-outcomes.json.gz` 保存每个 scenario 的 before 与 after 的完整 JSON/错误类型及原文；没有以 hash 摘要代替结果。

8项新增公共tests及81项既有相关tests全部通过，共89项。合法零文字 `0`、`0.0`、`0e0` 仍整份等同数值0和省略字段，不能因为 raw truthiness 新建 pending source。零观察窗仍保持原实际0和 cast pending；立即消失/免疫/E1资格仍沿用旧metadata gate，raw bool仍在早先实际整数查询处报原错误。S2更早的 bait 查询错误顺序也保留。其它owner继续忽略未查询字段。没有将非法小数、越界、非有限值归一为次数。

空target_windows 的声明次数仍不含目标普通攻击时刻，旧 incoming pending 和实际未知保持。frames 的已知window subtotal为0；continuous S2/S3原已知window subtotal分别25000/40500，按原mode完整保留。首轮新test错误地把frames供靶语义套用所有mode，只修正该测试断言，未再次修改production行；原未审patch/source/log保留在 `unreviewed-test-scope-v1/`，最终测试和矩阵以当前冻结版本为准。

原始资料固定于 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`；character/skill raw SHA fresh核验、完整talent/S3 selectors与既有研究receipt均在source-receipt。堕梦E2/level1只证明范围内普通攻击每次积累70神经损伤，不提供时刻/间隔/排序；S3首跳、附着、刷新、叠加、退场与当前热修等价性仍未知。恢复输入格式不能恢复实际总伤或伪造事件clock。报告仍为同等合法整数情景的原始未知程度。

不修改根代理tracked文件。git apply --check在冻结基线通过；696个原始源文件哈希核验且仅production目标一行改变。独立review结果由复用review_shu60另存。云端Linux公开计算验证仅证明上述scope；实际Qt/Wine及每5节全量由根代理负责，真实Windows/游戏native验证未进行。

独立审查已通过：复用review_shu60 fresh102pairs/204calls验证18合法别名恢复、70旧完整结果不变、14旧错误不变；8项新tests再次全过，并严格复比保存的1620pairs/528aliases。S2更早bait rawbool与E1 S3更早培养资格错误顺序均保留。无blocker。独立REVIEW/handoff及全部公开probe/output已按原字节拷入independent-review，最终patch仍为 `a8bae03fe3b1a7ab34da2b26fce646352c02f80decf0b4819cd2dda41407848b`。

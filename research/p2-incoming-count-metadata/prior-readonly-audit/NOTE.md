# 第67节只读审计：酒神目标普通攻击次数的报告转换

固定代码为 clean `0d446fc3523fd09452c84f65c133d23f33b31696` 的 rouge/tests/scripts，先生成独立冻结副本，再只通过公开 `calculate_damage` 验证。只读审计不修改 tracked 文件或冻结源，也没有新增实际伤害或时钟模型。`validation.json` 重新验证了冻结源 manifest 的全部哈希。

`Combat.option(enemy_attack_count, maximum=10000, integer=True)` 已先把有限、范围内、整数数值的输入归一为 float，并在实际查询处拒绝 raw bool。酒神的 incoming pending 条件也使用这个解析值；但生成 `neural_incoming_reference.attacks_requested` 时重新执行 `int(raw)`，因而合法 `1.0`、`1e0` 等正文字在 pending 分支发生 ValueError。此路径实际影响 S1/S2/S3，两个 timing mode 都可复现。

1620 次公开调用保留了完整 JSON 或原始错误类型及文字；其中 920 个成功结果、700 个既有错误。528 对整数别名中仅180对有差异：正数小数/科学计数文字触发后处理 bare int 错误。合法零文字 `0`、`0.0`、`0e0` 全输出等同数字0及省略字段，不存在 bait 的 raw truthiness 零绕过。数字 float1 与普通文字1 控制全输出不变。216个其它 owner 的 inactive 字段结果逐项等同省略。

保留旧 scope：零观察窗的数字1仍保持实际0但 cast pending，目标立即消失或免疫则不生成 incoming reference；空 target_windows 并不证明目标普通攻击时钟不存在，数字1仍保留 incoming pending 和实际未知。未解锁 E1 天赋也仍会先查询整数选项，因此 raw bool 继续在实际查询处报原错误，而不是被资格静默忽略。81项相关既有测试全部通过。

原件由固定游戏 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的 fresh local SHA、直接 Wine talent/S3 selectors 及既有研究 receipt 闭合。堕梦 PHASE_2/level1 的说明只证明范围内目标普通攻击每次积累70神经损伤；次数不提供首个攻击时刻、间隔或事件排序。S3 首跳、附着、刷新、叠加、退场仍未知。本次输入格式缺陷不提供任何新时钟依据。

候选是仅在已经实际成立的 incoming reference gate 中，复用同界限 integer 查询的解析数值作为 metadata 次数。不会改变 pending gate、全局 validator、数字伤害、phase/scope 或任何未知字段。bait/Wisdel 后处理问题分别归第65/66节，不纳入本节。原始065 initial-public-cases 中 enemy_attack_count 直接案例数量为0，它只是同类后处理线索，不能当作此前已有直接复现。

根代理后续授权的修复另存为 external draft；此目录保持原始只读审计断点。真实Windows、游戏/native验证未进行，Wine兼容验证由根代理统一安排。

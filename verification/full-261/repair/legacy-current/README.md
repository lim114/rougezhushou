# 261：历史047 / 060 的当前验证用途继任

只新增两份测试：`tests/test_readable_battle_047_successor.py`（3项）、`tests/test_river_reporting_060_successor.py`（13项）。未改应用代码、全局runner/索引/文档、旧历史模块及原失败回执。

首次必要验证：项目 `.venv/bin/python -m unittest -v tests.test_readable_battle_047_successor tests.test_river_reporting_060_successor`，16项全部通过，真实退出0。原始日志和回执为 `necessary-first.log`、`necessary-first.json`。没有新生成的计算输出golden；完整来源、原11记录和新输入逐项映射见 `source-and-case-map.json`。

047的真实0.47批后16函数AST保护继续由现有 current_guard 执行。3项行为保护覆盖合法扩展的函数：enemy_preview 的原字段/独立构造和完整渲染保留；enemy_skill_reference 的0/null/空/引用等级/未来等级/预算互斥及copy-safe；movement_reference 的名义速度、FP→float写回重读、条件分项与未知实际时钟分离。不是重建缺失 pre047 原件。

060新十类明确使用**新公开control输入**。旧全文JSON缺失，原完整scenario一个也未恢复；不把case名称相同说成原输入相同。四未持有、六持有，机械师/桃金娘/真言/酒神、无供给和另一藏品组合均有独立测试。逐例比较普通展示与仅在测试边界屏蔽river_reference_sections的完整当前计算：仅准确五个已验证报告块允许变化，所有其它结构、时钟、警告、原数值逐叶相等，不做广泛归一化或字段删除。

独立固定声明算术控制另外验证真言法伤+瞬时爆发+附带元素小计12200、另一来源组合19550、酒神法伤3000与总伤unknown、原两段动作时刻、零供给0、禁进入RiverInstance模拟器、copy-safe及完整四元素指标/面向用户的边界文案。参数依据已存在公开神经/束缚控制及固定原件。Git30f631f1中的river_effects.py完整SHA054acea…95acff43a恰好命中FINAL_0.60，测试严格核验该真实批后代码原件后独立读取literal contract；它不是66e5输出JSON，也不证明当前游戏热更新或实际 nativeFP 时钟。

定向公开恢复核查：FINAL0.60列出的11个river公开归档叶均缺；路径没有Git历史对象；164个已跟踪公开gzip JSON矩阵和5397个≤5MiB公开研究文本无原件字节/原scenario命中。原060只能取得完整原JSON并匹配66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326后恢复，原047前件也仍需对应完整SHA preimage。所有原11失败/缺件旗标保留，本轮只补实质可执行的当前同目的保护，不宣称历史原11已复验通过。

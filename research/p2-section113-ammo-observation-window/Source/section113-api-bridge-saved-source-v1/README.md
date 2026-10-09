# 第113节 API Saved 审计及115窄范围准入资料生成（Source）

作者仅做 stdlib Source读取、AST、哈希及compile-no-execute。未执行项目/API/Qt/Wine/测试/Git、未执行native helper或解码任何gzip/pickle/native090记录，未改tracked文件。Root导出的普通JSON只用于读取输入身份/字段名；其中native标签保持原样，没有解码。这里不存在实际PASS或候选数字。

Root先完整阅读与核对本包SHA，再独自运行audit_bridge113.py。参数均必需：--root、--guard（当前113候选完整Source/CORE）、--original、--candidate（Root真实probe-v2目录）、--original-exit、--candidate-exit、--out（全新offrepo目录）。

每阶段固定22个完整公开情景、88次真实调用（数值及三份完整格式化器）、110份原生记录。原始返回码必须为0，Source/CORE前后完整一致，探针和22输入已固定SHA。每条记录以f040检查压缩及解码哈希/长度、协议4及无全局对象，再精确核对类型、字典顺序、浮点位及完整图内部双向别名；所有调用前后完整图纯度、全部原版/候选完整调用者相同、完整格式化器输入与数值结果相同、三份当前实际文本均完整保存。跨独立捕获不宣称共享身份。

22个完整结果只允许113明示的 window_seconds、存在的window_dps/window_hps、存在的known-subtotal平均值，以及damage/healing报告对应metric.value变化。全部数值要求按当前实际分子/请求窗口严格复现类型与浮点位，没有容差。键存在性不变、None未知值与类型不变、报告段/metric顺序数量不变；仅恢复这些已验证叶子后完整结果严格等同，包含完整施放、阶段、周期、SP事件、分项、时序、培养、来源及报告其余内容。未变化情景还要求三份完整文本与原版精确相同。

准入固定十个历史字面行：[18,19,20,21,38,39,40,41,44,45]。原 projection090 和 native090 的AST须与冻结115字面Source精确相同；old实际完整投影必须通过native090树和原字面投影的类型/顺序/浮点位比较，不假装原Source字面能证明运行时别名。原版/候选完整投影内部图纯度另由f040严格核验。所有短历史输入字段必须与完整真实调用者精确相同，完整长调用者独立记录有序native090哈希且前后相等。

逐行逐叶记录旧/新presence、类型、数值、float.hex及实际changed。只允许实际变化的window_seconds和window_dps恢复到旧字面值；window_hps完全不允许变化，legacy机械师原先不存在的DPS/HPS键保持不存在，坐标轰炸None保持None，绝不插入键或未知变已知。候选窗口必须精确等于历史请求输入。恢复允许叶后完整候选投影与实测old严格一致。

只有220份真实原生证据和全部检查完成后，脚本才创建out，写receipt.json及expected-map115.json并生成恰好七份公开证明：original-primary.exit-code、candidate-primary.exit-code、original-receipt.json、candidate-receipt.json、original-guard.json、candidate-guard.json、pair-audit.json，全部位于proofs/，仅复制已验证的实际公开字节，每份写明长度/SHA。pair-audit为Root实际生成的普通JSON，绑定十行身份、完整投影/长调用者哈希及叶子映射哈希；map绑定它与六份实际0/收据/guard证明。未来115 guard仍NULL，由115最终guard指向map哈希避免循环。

脚本只是取得115比较桥所需的实际窄范围准入，不能替代115全量执行、窗口Saved审计/图片观看、准确性算例或Windows实机。最终认证措辞仍为42个历史投影不变、10个投影具有明确且经过113实际证明的窗口叶子例外。Root须保存原版/候选原生记录及失败历史，不能只有布尔摘要。

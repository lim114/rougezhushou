# HP原值、native分商与独立后置受疗门诊断

此候选对应P2“条件模组、数值精度与实际受疗资格缺口”。新增能力是接受整数HP或FP32.32整数原值及独立证据，按保存的原生除法计算精确分商、比较严格LT/LE门、求同一最大HP的末个符合/首个不符合值，并形成多观察行的门变化见证。它不是已有固定比例控件的包装：该控件只将一个double比例截断为FP原值；本候选实现的是HP/maxHP的native正数除法路径，舍入结果可以不同，并直接改变门条件参考。

## 完整闭合的原件与算法

复用当前216/215保存的同版原件，DLL SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`，基包 `26-09-13-15-28-10-30688348`。精确资料入口为 `research/p2-guardian-healing-gates-current` 与 `research/p2-susuro-healing-composition-current`。完整FP.op_Division method220475共125条保存指令；integer→FP method220503为3条，并明确左移32。

正数除法先将分母低端零nibble逐次剥离，保留33位求商预算，按分子前导零容量左移并逐段进行unsigned div，累积分商，最后 `0x1866fd861 lea rax,[r15+1]` 与 `0x1866fd865 shr rax,1` 折回32位。因此在限定正数域中，中点向上，不能用直接截断或最近偶数代替。本候选仅接入 `0≤numeratorRaw≤positive denominatorRaw≤signed64Max`；异常、负数、零分母及饱和路径不补猜。

独立整数oracle为 `((numeratorRaw * 2**33 // denominatorRaw) + 1) // 2`，与生产候选中的按原件数值分支模拟实现独立。138个边界及固定seed向量作为必要测试，另一个先行5000向量探查也全匹配。125条除法及3条整数转换记录逐条与同版原件对照，14个实际数值/get_hpRatio指令锚点独立核对。所有检查只读保存的原件；本云端没有重新取得安装DLL做新的物理字节核验。

## 精确保留的Clamp01缺口

`Entity.get_hpRatio` method66438在 `0x180704ccc` 调上述除法，随后在 `0x180704cf8` 尾调用 `Torappu.MathUtil.Clamp01`（`0x1866e3f00`）。后者方法体没有保存在当前证据中。

三次带具体线索的查证已完成：检查guardian/susuro完整方法包；按精确地址与类名检索全部保存research/work原件；公开定向查询 `Torappu.MathUtil Clamp01` 与 `Arknights Clamp01 FP`。均未取得同版方法体，第三次无搜索结果。原件仅证明有此调用，不由方法名称补出内部行为。

因此结果明确分离：

1. native除法阶段分商及其严格门参考，不能代表实际get_hpRatio或实际受疗资格。
2. 调用方独立明示的post-clamp ratio raw值，按已经闭合的三个模组LT/LE门计算资格参数；留空时保持None，绝不复制除法结果进去。
3. 实际HP原值、get_hpRatio、Clamp01、原生观察路径、模块附着、实际受疗资格及完整治疗始终未知。

重启条件为同版Clamp01方法体及适用路径，或独立明确的后置原值资料。声明来源、包括“游戏面板声明”，都不自动认证为内部精确原值；整数面板可能省略内部小数。

## 完整用户使用流程

`RecipientNativeRatioPanel`载入三个干员的公开FP原值参考。用户可直接填写整数HP/最大HP，选择整数HP或FP原值单位，填写原值证据并追加观察。另有默认关闭的独立后置比例原值输入，用户必须明确打开并填写，才能给下游资格参考提供值。JSON编辑器可调整培养/对应模组及各观察；非法整数、NaN、来源缺失、重复标签、跨干员模组及作用域不符直接拒绝。

观察行同时显示native分商、有理数截断分商、原值差、除法阶段门、独立后置门、对应直接治疗条件参数、严格边界相邻HP值，以及相对前行的变化。观察顺序只是声明顺序，不提供游戏事件时钟、存活/复活或治疗链。情景刷新只调整选择提示，保留用户编辑的HP及证据，不写入本局、账号或现有模型。

实际数值见证：古米LT严格边界为2147440698。声明 `hp_raw=4294881395`、`max_hp_raw=8589934592`时，native分商为2147440698，除法阶段门False；精确有理数截断为2147440697，门True。独立另填后置原值2147440697时，只将该后置声明的条件参数列为1.15；未宣称Clamp01实际产生了这一变化。黍与苏苏洛LE边界2147526598有对应见证。整数HP49998/100000的末个符合值为49998，首个不符合为49999。

## 验收、文件与目标接入

15项新必要检查一次通过，包括3个真实QWidget/offscreen完整输入和独立后置声明使用流。公开候选窗口已show、计算、绘制并保存 `candidate-public-qt.png`，图已实际查看；这不是原生Windows或游戏窗口。没有读写私人状态、运行游戏或发聊天；没有提交、计节、写生产或更新全局进度。

候选代码全部位于 `work/p2-recipient-native-ratio/candidate/`，目标路径为：

- `rouge/recipient_native_ratio.py`
- `rouge/recipient_native_ratio_view.py`
- `rouge/data/recipient-native-ratio-source.json`
- `tests/test_recipient_native_ratio.py`

API为 `recipient_native_ratio_diagnostic(payload)`，独立Qt面板为 `RecipientNativeRatioPanel`。source-audit、validation、public-reference-vectors、manifest及本报告由root集成到新的 `research/p2-recipient-native-ratio/`。root拥有真实节号、MainWindow入口、集成验证、索引、提交与推送职责。本次资料归档不单独作为功能节。

复现候选检查：`QT_QPA_PLATFORM=offscreen .venv/bin/python work/p2-recipient-native-ratio/run_candidate_tests.py`。该runner只在测试进程中载入work候选，未替换生产文件。

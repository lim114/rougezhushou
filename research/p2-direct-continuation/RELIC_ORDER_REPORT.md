# 六件固定藏品的声明处理顺序精度诊断

本功能推进P2固定同类承伤参数的精度和顺序条件计算。新模块按明确的来源身份、处理顺序或先后约束，复现同组逐次单精度合并，列出全部可接受排列的离散结果、范围及当前十进制模型差。没有改变默认伤害引擎。处理顺序不称为实际获取顺序；原件没有闭合OnStack或实时获取到预处理列表的绑定。

## 原件链与适用范围

固定参数表提交为 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，对应六件 `rogue_6_relic_legacy_5` 至 `_10`。每件原表仅含一个 `global_buff_stack_base_one`；5/6/7的key是 `enemy_damage_scale[phy]`，8/9/10是 `enemy_damage_scale[mag]`。实际预制体分别附着仅筛选PHYSICAL或MAGICAL的DamageScale模板，不把两族相加或连乘为一个总倍率。

复用214已保存的完整原件，DLL SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`、metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`、基包 `26-09-13-15-28-10-30688348`。本云端核对保存文件哈希、完整CFG及16条具体指令锚点，没有重新拿到安装DLL做本次物理字节比对，不能声称新的原生实机核验。

- `RoguelikeBattleManager.PreprocessGlobalBuff` method85522按列表索引递增，调用实际预处理槽。
- `GBuffStackBaseOne.Preprocess` method85907按完整prefabKey查找；首次不存在时复制blackboard，不能从隐含的1开始先做一次加减；已有时将旧board和新board交给method30846。
- `Blackboard.AddBlackboardBaseOneStrictly` method30846在 `0x18231d663` 读取single，`0x18231d668`执行addss，`0x18231d671`执行subss，`0x18231d67c`回存single。相减常量的已存RIP字节 `0000803f` 为1.0。

由此得到限定模型 `f32(f32(old + incoming) - f32(1))`。本功能使用IEEE754单精度最近偶数算术作为参考约定，分别取整每次加和减；实际运行的FP控制模式、最终FP转换和伤害包取整保持未知。来源包由新builder从封存原件派生，并在消费者加载时检查确定SHA256；缺失或改变时，数值、范围、逐步结果保持None，不按1或0填入。

## 用户可得到的实际计算

- 选择1–6件固定来源，留空处理顺序时枚举全部不同排列；最多720种。
- 用ID二元数组明确声明“先于”约束，完整枚举其允许顺序。循环、重复约束及与明确顺序冲突直接拒绝。
- 明确顺序逐步显示每件输入single值和bits、旧同组值、加后的single、减1后的single以及精确十进制差。不同伤害族各有自己的carry。
- 每族列离散bit结果、min/max、各结果对应的枚举数量及现有 `source_factor` 数值差；联合结果保留族间由约束产生的关系。计数不是概率。
- Qt面板可以查看某个枚举排列而不写入声明；只有明确点击写入按钮才更新处理顺序。当前情景更新只改提示，不覆盖编辑中的清单、约束或结果。

实际数值例：法术三件六种顺序的最终结果只有 `0x3ff33332`（1.8999998569488525，4种）与 `0x3ff33334`（1.9000000953674316，2种）。将最后十进制1.9仅转换一次得到 `0x3ff33333`，不是这六种逐次合并的结果。最小与最大之间的bit不能自动当作候选。

全部六件720种顺序，物理族最终始终1.75；两个联合bit结果分别对应480/240种排列。明确规定物理内部5→6→7及法术内部8→9→10时剩20种族间交错，法术结果固定为 `0x3ff33334`。这些都是声明源组从空组开始、无隐藏同key背景的参数参考，不能据此判定实际库存、获取顺序或最终伤害。

## 验收与接入

16项新API/来源/真实QWidget offscreen检查和11项现有组合检查，共27项通过。验证完整720排列、离散bit间隙、逐步两次single取整、首件复制、双族隔离、约束缩小范围、未知来源包、非法ID/重复身份/NaN/循环冲突、编辑与查看隔离、当前情景刷新保留。初次测试fixture方括号SyntaxError在任何用例开始前发生，已保留准备失败记录；修复后一次27项全过。后续仅将报告None显示为“未知”，单独报告检查通过。

新文件：`rouge/relic_order_precision.py`、`rouge/relic_order_precision_view.py`、`rouge/data/relic-order-precision-source.json`、`scripts/build_relic_order_precision_source.py`、`tests/test_relic_order_precision.py`。API为 `diagnose_relic_processing_order(payload)`，面板为 `RelicOrderPrecisionPanel`。root串行接入参考工具入口，验证MainWindow和必要实际可见窗口，再统一索引、节数与commit/push；作者没有提交或计节。

仍未知：实际获取/处理列表关系、OnStack、实际附着与隐藏背景、当前XLua/热更新、FP控制模式、最终FP包/取整、实际承伤与实机面板。原件缺证的酒神和屏障路径不由本功能关闭。

# 第102节 Source 资格边界补充（冻结v1原件保留）

本说明限定section102-inventory-flag-consumption-source-v1中的“partial/read-missing不能升级”：
**只有缺少有效当前或完整历史证据的部分/未读取观察，不能凭异常flag升级确认。**
原RunState也支持同局有效历史全bar在后续难度或持有卡片补证时重新解析；reconcile_relic_icons
可生成memory_replay，原完整槽producer仍能设bool True。这个原行为必须保留，不能将它误判
为“partial不应确认”而改产品或删断言。旧full bar的来源、完整性与当前矛盾校验仍按既有逻辑。

候选只改1helper+3flag消费，memory_replay、full/removal谓词和bool生产赋值未动；
15个新拟议方法中的partial/unread用例没有有效历史icon memory，所以它们的预期False范围
是正确的。已冻结v1 Source/manifest没有重写。该补充不是执行证据，也不增加完成编号。

Root实际检查应包括原test_relic_grade_sync_032中的late_grade_resolves_saved_bar等场景，
并加异常raw flag但具有有效同局历史bar的健康对照：后续合法难度/卡片补证仍可通过原producer
恢复True；同时新工具、改变计数或外来slot使历史bar失效时不得升级。保留全部旧math和三份
文本行为对照，不能只用没有history的异常flag用例推定全部覆盖。

其它numeric确认flag只是最小兼容保留而非生产来源证明；本候选不创造任意新schema，
也不宣称所有确认字段或numeric输入都已验真。全部项目/API/tests/helper/Wine/Git执行为0。

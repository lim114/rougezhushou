# D318 商店超大整数时间入口

用户明确答复：“批准，两处入口拒绝超大时间值”。

适用范围：player_shop_memory.remember、recorded_shops。极大整数会使时间差/浮点有限数检查溢出；在入口拒绝超出浮点范围的整数，保留原两秒新鲜度、同局、非负和有限数条件，不增加重试。发生率未知。

已实施，两处入口的范围条件避免溢出；原始复现仅本机，验收见verification/maintenance/code-constraints-shop-time-review-20261106/summary.json。此授权不扩展到其它入口。

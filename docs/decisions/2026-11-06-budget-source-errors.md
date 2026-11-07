# D329、D330 · 单次伤害和治疗来源

用户分别批准收窄 damage_sources 和 healing_sources 中分项与旧格式各两处捕获。仅 AmountInputError 表示该来源的数值无效；保留同次计算的有效来源与零值。内部普通 ValueError 继续上报。

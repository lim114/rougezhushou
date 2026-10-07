# 第74节：魂灵之影两条原始本体召唤途径的培养资料

精确基线为已提交70节 `552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9`，121 package +191 test 公共文件从固定git blob导出。未复制工作树或用户state，未运行Wine或声称当前native验证。

固定原始角色表给第二天赋“死魂灵的余息”唯一候选的 tokenKey=`token_10035_wisdel_wward`，E2 level1、potentialRank0、prefab2；原文为部署后立刻在攻击范围内召唤一个魂灵之影并在其周围获得迷彩。角色S3条目 overrideTokenKey 同一token，unlock同为E2 level1；十个技能等级原文一致说明在攻击范围内召唤、最多存在3个、结束后保留。以上是精确原表途径和培养门槛资料，不是实际召唤/在场/施放证明，也不宣称囊括所有模组/藏品附着途径。

既有 ghost_count/ghost_casts 是窗口来源声明；未建立排除独立来源的契约，因此本稿**不拒绝、不归零、不重新解释精零/精一的合法声明，也不推断声明归本体或外部来源**。token条件面板仍由本profile培养求值，此既有算值不证明实际来源归属。所有数学、实际unknown、旧66 parsed-count合同、61 boolguard、空窗口正施放错误、控件均保持。

新增一个result来源资料键 `wisdel_summon_qualification_reference` 和报告节 `wisdel_summon_qualification`。第二天赋原tokenKey来自新增固定原selector数据，因为旧catalog的talent目录没有保留tokenKey，不冒充当前catalog自动解析。S1/S2不把当前rank借给未选S3；仅显示十级共通原文fragment，省略动态数量。只有实际选中S3才引用自身rank对应完整原文/BB。培养资格与是否当前选S3分开显示，实际来源/存在/施放时钟仍未核验。

fixed patch `section74.patch` SHA256 `f575adbd072df964ef65a61c0b66d7d9e6ae52250a3cf36601a36c9e07c805dc`，21639 B。engine仅在旧Wisdel块中追加资料调用，report仅增加资料节，另含隔离读取helper、固定selector数据和8新测试。engine CRLF、report/newhelper/newtest LF保持。

作者 source closure重新核对既有character/skill原字节hash，没有新下载；192培养/潜能/模组selected-talent记录、十个S3rank identity/BB/description与共通fragment一致。原source/gamecommit为 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，没有native/script时钟绑定新证据。

作者矩阵2238 cases，2130实际public calculate每侧，4260 paired calls：1314接受cases只新增来源信息，918 exacterror cases、6其他owner cases保持。仅剥离明确新增result键及report节后，旧**完整JSON**（所有数值与metadata）、默认report、technical report、estimate文本逐字相同。unique每侧1266接受/864错误；case和实际call计数有108重复明确区分。来源JSON/cache、catalog与调用参数未漂移。

作者58方法全通过（8新+50旧）、无skip/fail/error；原始whole-outcomes gzip保留可解压原JSON与raw/gzip双hash。独立review从独立冻结baseline应用固定patch，其sealed receipt附最终交接。

恢复后已确认旧pending未创建进程、最终封存文件原先缺失；仅核对作者312 public source/test与5个patch文件、两gzip/raw哈希及原日志，不重跑2238/1190矩阵或58/61测试。独审sealed receipt SHA256 `94707671c8b607f90cfdb7a02c6bae6f495156cd3139b72fc0403560f368fd12`，1190pairs/2380calls、824仅新增资料、366全同、61tests全过。双方posttest来源一致，无漂移。

固定pyproject的 `rouge*` 与 `data/*.json` 已覆盖新增helper和顶层JSON，无需改打包配置；此为只读配置检查，不声称新包或native/Wine已验证。root后续fresh integration及五节全量验证单独记录。

# 106候选v2 · 最终非作者Source独审

结论：v1测试时间前提阻断已在fresh v2解除；本次未发现五局部产品运输或23测试Source的新阻断。仅Source检查，不是候选测试/数值/GUI/产品PASS。future Root实际105完成基线及registry运输仍pending/NULL，不能由本报告代替绑定，也不能在Root105全量关闭和发布前应用106。

审阅仅执行自己的标准库文本/JSON/hash/AST/内存compile及drytransport；没有执行或import项目、测试、helper、native codec、Qt、Wine或Git，没有tracked写入。Root原API观察JSON只读取既有文件，不执行其生产脚本，不解码任何native记录。

## 冻结版本及独立核验

- tests：15174字节，SHA256 `6cd75f91e466daa6b231a6e318b44795f596a2b8d292c0fd6939329117521a8e`。
- exact-local-transports：7008字节，`028063cf676eee596c07046fd009b18cf48b2bc71ed2665ac12fc477988e9624`。
- README：7290字节，`d98618544283774d1ad91d9aca32c46da0227694ff8c90d2912f4b9fc26ffd53`。
- AUTHOR_SOURCE_CHECK：4332字节，`00a5c8efacff90c3815a10617cfb8b41634ee3fae7c1ef9678cc0c0eef373701`。
- v1-to-v2-test.diff：726字节，`3bcfa57963856949cd4a3a1fc56b733cbd13c7b8f9047f75514ff7eb00d9b41c`。

v1 e661e4…测试和c6c17e…transport原件hash独立重核未改；其既有Source审阅 `section106-environment-candidate-source-v1/INDEPENDENT_SOURCE_REVIEW.md` 6492字节/efa2dc28…保留，不把错误历史覆盖为PASS。v2是该审阅范围的精确修订，不扩大游戏机制或数值模型。

工具395229/0独立完成：全部pins、两版本23方法名同、所有64个assert/assert*调用AST顺序同、唯一新增可执行statement、测试module其余AST同；五产品current/forward/inverse/afterSHA、compile-only、全部其它FunctionDef和整个module除指定body外AST同；Root原JSON字节/hash及33/284/350结构匹配。8e291d/0只读原JSON核原错误/安全控制。ac855a/0确认相关回归文件实际存在。没有exec编译对象。

## 唯一测试变化真正修复时间前提

唯一变动函数是 `test_invalid_incoming_mode_does_not_replace_valid_saved_difficulty`。在RunState构造前新增真实 `path.write_text(json.dumps(fixture({}), ensure_ascii=False), encoding='utf-8')`；fixture完整含operators/relics dict、config difficulty空dict、started_at1000及同局ID。没有mock时钟、改产品时钟或放宽apply保护。

因此构造加载真实公开JSON，state.started_at1000，默认last_readNone；实际apply首门max(1000,0)允许1001合法初次观察，随后last_read1001，1002坏mode观察到达资格判断。原v1对absent路径构造用真实当前started_at，却apply1001的确定阻断不再存在。所有原断言完整保留：初次value0成功、后来MONTH_TEAM不能替换合法difficulty、caller不变、真正保存重载保value0。其余22方法AST相同；整个测试module除这一body外AST同。

## 五产品变化精确保持v1及当前103/104成果

各transport path/before/after/newline/beforeSHA/afterSHA/changed_methods与v1完全相同，metadata只绑定Root原实际receipt、纠正app全函数计数及保留future guard/registry pending。五个before在当前Source里均唯一一次，current hash与manifest相同，candidate after唯一、hash相同，inverse精确复原原bytes；CRLF/LF按原文件保留。

| 文件 | candidate SHA256 | 唯一变化 | 其余FunctionDef AST相同 |
|---|---|---|---:|
| rouge/run_config.py | 3c96897dd6b5c692489b9e55ac57f570adb352f1589038b7a52b3e9a8a891b70 | difficulty_value | 4 |
| rouge/enemy_environment.py | d55a1ad900b4dd33b030114de5f5ee5bb6f2ca2f48ddea67e686dadc7f83dd4a | resolve_enemy | 3 |
| rouge/reporting.py | 0f77990bfed4d962080da5876f79de5da1a1663d57e52890823d07c1ee5d6bc1 | build_report | 14 |
| rouge/app.py | f3577a3e1e40d19b4d302e2c8e5abe498fbec635497df40f81603f0dcd7dfebf | MainWindow.sync_run_config | 64 |
| rouge/run_state.py | ee46af93155e210a47a3cd8dcbb4dfcecd0c7b2596c2e0f32e2bd9d4c5f6a9a9 | RunState.summary | 24 |

计数明确是全部ast.walk FunctionDef（包含嵌套节点）。app共65个，仅sync_run_config变，其余64含三个不同nested work；v1按name去重的62已透明更正。独立将每个指定body清空后，整个module AST精确相同，进一步保证imports/constants/classes/decorators及全部其它语句不变。不是凭作者计数猜其它方法保持。

## 原实际依据与兼容合同

独立只读Root原观察 `section106-original-environment-actual-linux-v1/observations.json`，604831字节，SHA256 `c09e542f3d1cee720c31daa638663a133bd1894268eb7bb20abc062ccfb92b25`与v2绑定一致：33rows、284calls、350native索引，elapsed3.453493556秒，observation_onlyTrue、product_passFalse、observation_completeTrue、Source/CORE unchanged；22cached fresh_apply_result均exactTrue且restart flagsTrue。实际原进程raw0由Root工具74262/0提供，本审阅没有运行进程或单独读取native作再认证。

原JSON明确两active bool level的calculate返回成功，而对应preview为ValueError；两个float对应数值成功、preview仍ValueError。mode MONTH_TEAM/None/list的cached_confirmed_config含difficulty而原calculate ValueError；五显式非文本source的cached calculate为TypeError，trace包含build_report，不能把坏source说成原公共数值API返回成功。原总错误为19ValueError、5TypeError；错误观察不是产品通过。README/metadata准确区分原观察完成与候选未运行、第105全量仍pending。

五产品合同沿用v1完整Source核对：difficulty_value按两alias的既有NORMAL资格、strict int0–15，不加入source字符串grade门；confirmed_config/apply同helper统一复用/新观察资格，raw缓存保留、坏incoming不覆盖合法值，合法fresh可恢复。prepare_run原unsupportedmode ValueError及优先次序没有改；未知squad.effect_verified原raw复用、103的修复和104持久化防护不变。

active bool敌人等级只在合法stage/preview后、原唯一匹配前拒绝；原错误文本沿用，旧float0.0/1.0、top-levelFalse/{} inactive、原坏stage先报、其它无唯一引用错误保持。enemy_preview原strict技能门未改。

来源只在build_report原字符串拼接处使用待核label；raw源None/list/int/map/bool/其它JSON数值不被清空或强转确认，缺键default、空串、文字空白精确保留。数值因已有明确grade继续原参考合同；source未知不是新增已确认来源。summary与sync_run_config只按grade资格展示；合法0通过is not None处理，失格grade/mode提示原记录保留、分析preset可用。真实calculate及BattlePreview仍用raw run.state.config，preset没有替代本局或悄悄绕过原数值错误。

23方法覆盖10资格/恢复、6身份、7source合同；全16等级、alias冲突、原错误次序、unused门、原盘/tmp纯读、真实fresh/save/RunState重载、来源两明确presentation leaves以外完整结果同condition比较及raw类型都有Source。普通unittest equality不能证明alias/floatbits/原Gold完整结果；这由Root独立native pair与窗口验收补足，README如实保留。具体Source无新增未证游戏机制，不销P2 timing/summon/environment原生未知。

## Root实际回归与剩余验收

已在当前repo确认以下回归文件存在，可作为相关selector基础：`tests/test_run_config.py`、`tests/test_run_config_validation.py`、`tests/test_run_modifiers.py`、`tests/test_enemy_environment.py`、`tests/test_enemy_skills_042.py`、`tests/test_cache_recovery_103.py`、`tests/test_run_persistence_099.py`、`tests/test_inventory_confirmation_102.py`。当前准确敌人技能文件名是test_enemy_skills_042.py；不存在的简写test_enemy_skills.py不能作为已确认selector。新tests/test_environment_input_106.py目前仅off-repo包存在，需Root实际运输后才运行/登记。

完整验收仍待Root：105全量实际收口和发布、106精确guard/登记/应用、23新测试及相关/精选回归、原integer与float各自完整nativeGold pair、真实MainWindow健康Gold/候选与三全文、坏模式初始保护错误/来源待核、合法后续观察恢复、close/实际RunState重载、4实际PNG及Saved审计。Source独审不能替代这些检查，也不能借原实现probe raw0或旧全量PASS计106完成。

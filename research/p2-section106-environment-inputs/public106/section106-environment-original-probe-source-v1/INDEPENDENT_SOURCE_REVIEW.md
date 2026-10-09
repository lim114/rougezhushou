# 第106节原实现环境API观察探针 · 非作者Source独审

结论：对本包声明的原API观察范围，未发现阻止Root运行冻结探针的Source问题。此结论仅来自只读源码、公开JSON、字节/hash、AST和内存compile；没有执行探针、项目、helper、codec、Qt、Wine、测试或Git，没有修改tracked文件。不是第106节产品通过，也不是第105节Runtime全量通过。

## 本次精确版本与真实Source基线

- `probe_environment106.py`：13403字节，SHA256 `63450e33dbfd68c07477fc9a9e7169cd16eb1d177685632ef1ad9615013b8999`。
- `fixture-manifest.json`：8682字节，`2e8f3e9b74a84cb9d4ef7cee49df8bc8510c6b2bc3e09afd74b94d6af32ce217`。
- `native_evidence.py`：6468字节，`f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a`；独立按字节与此前100 smoke helper比较完全相同，仅读Source，未执行它。
- 本次读取的更新README：5410字节，`70cc767afcd4916d7ccc9960bc045660c2b89c04f567ceac20392f0fb4789d3a`，替代最初5247字节/a1a0…版本；runner、manifest、helper未改。
- `AUTHOR_SOURCE_CHECK.json`：428字节，`76c3a0afd46e72cac394964154eacd4c4492d981f0b4cee24a2fb33a27dbd15c`。它是作者Source记录，不是实跑证据。
- Root实际提供的 `full105-source-suite-guard-v1.json`：82712字节，`773a912df815a8cb0f39f497de1c8851d5c9c9e7914020ea5f5487a2feb1707b`；748份Source，实际CORE SHA256 `a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89`。

独立使用标准库遍历rouge/tests/scripts的.py/.json、排除__pycache__、拒symlink并逐hash，与上述748映射完全相同；实际CORE一致。manifest九个固定消费Source pin与guard及当前对应文件全部一致。没有调用helper.source_map。Root必须实际再次执行runner的前/后守护；本次只读匹配不替代实际运行期间的绑定。README准确说明105 Source已实际绑定而105 Runtime全量仍pending；探针顶端“completed105”描述应按该Source基线理解，不能借此宣布105验收完成。

独立工具记录：2e58a4/0核版本、22文件字节/hash/JSON容器、九Source与guard及公开健康条件；4e9915/0核全部748+CORE、两py AST及compile-only、helper旧版逐字节、两个preview与skill绑定。没有exec任何编译对象。

## 公开输入确实到达所审消费门

22缓存文件与manifest集合完全一致，33个cached/direct ID唯一。缓存均是JSON可载入dict，显式mandatory operators/relics为dict，config与difficulty为dict并有value；空成员、藏品、资源、地图不会触发其他历史修复。始于1000，缓存captured_at1001，fresh捕获1002；额外last_capture_at是可保留的opaque字段，不冒充last_read。初始构造真实恢复notice/defaults，观察记录保存实际加载状态，原盘字节另行严格比较。

8模式、8来源、6value分组与README一致：模式alias缺省/NORMAL/月度/None/list；来源缺键/字符串/空串/None/list/int/map/bool；value合法0及原严格门拒绝的bool/float/text/None/list。saved validator只对difficulty要求dict及非空含value，所列leaf不会因虚构schema先被拦截。Root实际constructor接收仍需以记录确认；runner若意外拒收，assert会阻止把下游观察伪作完成。

健康base是公开机械师S3、E2等级90、rank10、信赖100、潜能1、无模组、10秒、frames、charge_count0。直接读取公开operator-profiles/catalog并按catalog覆盖合并：机械师阶段上限[50,80,90]，3技能、S3有10档且unlock_elite2。因此不存在用超过上限的健康base掩盖原问题的Source缺口。没有藏品、酒类或未定义命中次数进入此fixture。

公开catalog/previews中两个目标分别唯一匹配：ro6_n_1_2/enemy_1093_ccsbr/0、ro6_n_3_1/enemy_2001_duckmi/1；同时battle-previews与enemy-skill-references存在相应精确公开绑定。这里只核固定档案引用，不证明实际出怪。

## 三条原行为的具体调用链与错误边界

1. `RunState.summary`、`recognition_context`、`confirmed_config`、`difficulty_value`、`calculate_damage`分别真实调用。difficulty_value当前仅检查modeDifficulty和strict builtin int；prepare_run同时拒绝非NORMAL的mode/modeDifficulty。合法缓存mode MONTH_TEAM/None/list仍可在前者被复用而原数值入口报受保护的ValueError。探针保存每个原返回与完整trace，不预先断言其健康，不洗掉缓存来让数值成功。两alias NORMAL、缺省和合法0是真实健康/安全控制。
2. direct数值与preview分别观察。`calculate_damage→_prepare_damage→prepare_run→resolve_enemy`的引用等级相等筛选会使False/True匹配0/1，原0.0/1.0也按相等匹配；文本/null/list无法唯一匹配。顶层False/{}在原not target门短路，不被迫当非法启用目标。`enemy_preview`早期虽相等匹配，随后`enemy_skill_reference`已明确拒bool及所有非int；本包不会把preview说成也接受bool，也不能把既有float数值接受合同扩大成全strictint修复。
3. `calculate_damage→_evaluate_damage_once→build_report`实际在公共数值调用内部构建报告。`finish_run`保留difficulty来源原leaf，build_report在reporting.py:1011拼接字符串和difficulty.get('source',default)：显式None/list/int/map/bool会到达TypeError。不是因为探针未单独调用format_report而漏掉该原异常门。缺键使用原default，空串与正常文字保留旧安全行为。本探针不另外验证format_estimate/readable/technical三全文的最终展示；未来产品窗口验收需独立补足三全文和Qt行为。

这些均是Source可达性解释。实际是否返回、异常类型/trace、健康数值和后续恢复由Root运行产生；source review没有提前填入任何Runtime PASS。

## 异常隔离、native图与磁盘范围

observe先freeze同一组合图 `(args, run.state, disks)`，从而caller run_config与state共用dict的alias同在比较域；后按原args/原state/真实文件重新取图。catch Exception只捕获产品调用，将真实type/message/trace和result写入native后，才比较纯消费前后。unexpected mutation或native基础设施失败会终止本probe并保存fatal记录，不归类为新的产品失败，也不吞掉它。错误结果不会因为外层raw0转成产品通过。

helper Source只接受exact builtin None/bool/int/float/str/bytes/dict/list/tuple，保dict顺序、float bits和双向容器alias；JSON fixtures及所读API结果属于此域。save_native使用len(native_rows)+1，第一次sequence1满足write_record正整数合同；文件xb，不覆盖既有证据。这里未运行pickle/gzip或任何codec。NaN等不在公开fixture中；观察receipt allow_nan=False若遇未预定非有限结果会作为基础设施失败，不能假称数值正常。

每个cached case在独立fresh公共目录写固定JSON原字节和既有run.tmp sentinel；真正constructor后assert两文件原bytes/exists不变。每次纯消费比较caller、完整state和run.json/run.tmp真实bytes，含成功与异常调用；无模拟IO。初始缓存没有需要合法修复写盘的历史，constructor意外写盘会被严格断言拒绝。路径不指向真实用户run/settings，没有Desktop/Qt/ScreenReader/OCR或网络访问。

fresh观察由manifest公开JSON复制，真正run.apply单独作为authorized-apply-save-phase。caller before/after单独严格不变，state和文件前后完整保留；允许真实保存替换原run.tmp，不将这个合法变化误说成原盘始终不写。apply异常仍记录，若返回非True不生成虚假的fresh/restart成功。observation_complete只代表脚本完成预定遍历；Root仍需检查每个fresh结果、错误和缺少的后续phase，不能用该bool代替恢复成功。

成功保存后真实UTF8读取JSON生成persisted_JSON oracle，再真正RunState(path)并native严格比较restarted.state与实际JSON图；没有跨JSON要求原live图的aliases保留。所列fresh条件中notice仍是恢复notice，完整state保存含默认键，restart使用同默认键顺序再update；本组fixture没有额外历史修复，故Source没有明显的伪alias/notice断言问题。另按真实已保存盘和tmp比较重载前后，保存state、persistedJSON、restarted图的区别不会被模糊处理。

## Source守护、deadline及Root后续审计

所有guard、CORE、九消费pin、fixturehash和helperhash先于项目导入。sys.dont_write_bytecode在helper/项目导入前设置。所有写入限fresh out与自身公开fixture路径；maintained Source无写入。receipt恒observation_only=True、product_pass=False、Qt/nativeWindows/OCR/private等均False。Source及CORE在finally重新hash，实际变化或基础设施异常会导致非零并保留结果；Root审计必须同时要求真实raw0与source_and_CORE_unchanged，而不只看observation_complete。

120秒watchdog只对本脚本os._exit124，不杀其他Wine/会话；timeout保存当前case/phase。被硬终止可能只有已落盘native及timeout，完整observations receipt未必形成，Root不得把它当完整观察。当前Source没有假计时/额外时钟机制证据。

Root可在该冻结runner与实际105748/CORE前提下执行原API观察；原问题确认、候选应用、相关测试、真正MainWindow健康Gold/候选对照、三全文、4实际PNG、保存/重载和Git均另由Root实际完成。本独审不销掉P2 timing/summon/environment未证游戏机制，不宣称模式来源自然产生，不扩squadlevel或未知flag schema，不把未知改为确认。

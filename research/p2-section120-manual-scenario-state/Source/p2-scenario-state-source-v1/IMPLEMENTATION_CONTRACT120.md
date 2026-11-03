# 第120节候选：双情景编辑框隔离及明确JSON输入（仅Source）

实际功能成果是完整的一组手动预览完整性改善；资料、测试及全量是附加，不独立计节。尚未应用到tracked，不含任何项目/API/Qt/Wine/helper/native/gzip/Git执行。未来120实际HEAD、guard、Source数量、计数与PASS全部待Root取得。

## 已读Source中的两个问题

`rouge/app.py`的calculate原1079–1091在总览无干员、仅有档案尚未实现的干员、无可用技能时提前返回；两编辑框的`timing_preview_key`保存/恢复却在原1147–1157的try内部。从已实现A切到芙蓉或Lancet-2后，编辑框仍保留A文本且可编辑；返回A时key还是A，因此临时编辑覆盖原A情景。Root须先用原窗口实际确认此路径，再运行候选，不能将Source推演写成已测用户发生。

原1202/1211用默认json.loads解析手动藏品/时序JSON。重复字段只保留最后值，`{"target_windows":[],"target_windows":[[0,5]]}`及相反次序可静默颠倒供靶选择；NaN/Infinity扩展还会进入解析后值。数学消费者对活跃非有限值有既有门，但嵌套/闲置扩展不能被描述为合法JSON。此候选只调整两手动编辑框的输入规则，不改dict方式public API、RunState、AccountCache或数学/游戏机制。

## 官方资料与规则归属

已实际下载HTTP200并封存：Python3.12 json官方文档107891B SHA `1a5e4ba18342b32f5f174d129f9c226a21a9445a89384f13a3f33ec327c2b68f`；RFC8259文本28360B SHA `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7`。实际URL、北京时间、ETag/Last-Modified在public-sources下载ledger。该文档当前页为3.12.15；Root实际运行Python版本需自行观测，不将网页版本当作Wine runtime版本。

- Python文档明确默认NaN/Infinity扩展、重复名last-value-wins；object_pairs_hook提供原顺序pairs并可改变重复名处理，parse_constant可拒绝三个非有限字面值，parse_float可限制float转换。
- RFC8259第4节是names SHOULD be unique；未规定重复字段必须如何拒绝。此app选择重复字段显式报错是本应用规则，不是RFC强制规则。
- RFC第6节明确Infinity/NaN不符合JSON数值语法；`1e309`却是语法合法JSON。候选拒绝其float溢出是app有限数值输入政策，不能称RFC禁止该合法数字文本。
- 顶层对象要求也是原app编辑框规则；RFC允许其它JSON顶层类型。

## 精确改动

新增`rouge/manual_scenario.py`中的parse_preview_object只消费临时编辑框文本。递归object_pairs_hook拒绝同一对象重复解码键（含Unicode转义后的同名），不同对象可各自有同名。parse_constant拒绝NaN/Infinity/-Infinity，parse_float仅拒绝转为非有限浮点。正常int/float/bool/null/文本/容器、顺序、±0.0、有限数值舍入与未知键不改。引号中的"NaN"继续是字符串，微小浮点下溢仍保留原json.loads的0.0。原语法错误、非对象错误文本保持。

app新增sync_scenario_previews，把原双字典/双编辑框记忆提前到calculate的所有早返回之前。仅已实现operator+非None skill为有效key；离开有效key先按原字节字符串保存两个文本，进入无效选择清空且禁用两编辑框，回来恢复原缓存并启用。有效owner间、不同skill间仍保存各自文本及错误文本，不清空字典、不写本局/账号文件；blockSignals恢复进入前状态，避免递归重算。原animation和target-buff预览方法不动。

两编辑框仍在原适用门下解析：时序只有非空文本解析；藏品只有needed非空且文本非空才解析，未知/不适用条件继续按原needed过滤。隐藏而未消费的藏品坏JSON保持原忽略行为。空时序仍不产生timing键，空藏品仍采用run.calculation_resources已确认记录。不改变招募/强化metadata、培养fallback、默认字段、计数应用或游戏事件。

local-transports.json含6个app精确局部增量，原app为100115B SHA `fa77caff7b133a42d651f25166327982f37487a57ddb84f3461fc13bed1e03c8`，候选100029B SHA `19ddbe647157316e07301c5b4d383cad2d8f622257457a52a57429f20fe5e7b4`。仅原MainWindow.calculate方法AST改变、新增sync_scenario_previews，其余方法AST保持；Source逆向恢复完整原app字节已核对。CRLF保留。cloud selector只局部插入新12方法测试，不整份覆盖未来维护的verify_cloud。

## Root应用与实际验证

Root须在119实际完成并推送后，以真实Source重查局部old anchors并重新组合，不整份覆盖本包旧app/cloud。任何未来变化需要局部逆向核对及新Source审阅；不要预填未来HEAD/guard/count。独立Source审阅、12方法相关Linux/Wine、原件/候选API配对、实际可见窗口与Saved/PNG按Root现有严格工具完成。

1. 原/候选对相同合法手动JSON形成的完整numeric result/caller、estimate/default/technical文本、输入纯度与公共run/account文件比对。例子包括明确空/非空供靶、独立token供靶、带零计数藏品；有效JSON应数学完全不变，切换回错误JSON仍明确不可用，不回退上次数字。
2. 原窗口测A→芙蓉/Lancet-2/空总览→A的实际双编辑框文本/key/enabled与公开调用。候选保存A两字符串、无效选择清空禁用、返回A恢复。无技能分支可通过真实QComboBox无current项的公开UI状态验证，不伪造游戏精英锁定规则。
3. A→B→A、A技能1→技能3→技能1合法预览、无效JSON离开/回来、支持owner里的空JSON/只空白，应保留原记忆、错误和省略语义。所有状态实际操作控件，不能直接改timing_preview_key或用monkeypatch替代数值结果。
4. 重复目标区间及nested unit、重复parts_count、裸非有限及合法指数溢出：错误应来自当前编辑框，damage_result为None且原文本不被重写；恢复合法值后重新计算。隐藏needed空的坏藏品文本不阻断无关计算。raw/technical切换在错误时不展示旧成功数字。
5. Root保存实际当前Source/CORE、完整调用与格式文本、两编辑框/字典状态、文件原字节与未采样未发聊门、至少实际窗口图像及独立Saved读回。source-only公计划不能作为PASS或native gold。12个新测试是解析边界，独立实际窗口是scope/state修复验证。
6. 120之后执行当批全量/精选/依赖及有界窗口，统计从真实receipt读回，与115旧证据分开。本节commit+普通push和五节报告后继续121；95/109defer、原生Windows/game/chat不可验证边界继续保留。

这组修改不重复112的reset采样视图、不重复114的public数值bool、不重复115的报告分项。run/account消费检查发现的其它问题只有新完整Source证据后才另提，不以猜测游戏事件延长本节。

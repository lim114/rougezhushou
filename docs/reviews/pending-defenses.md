# 需要用户确认的防御项

当前已列D38—D317共280组，用户于2026-11-06全部作出决定；D318已另获明确授权并实施，D319/D320仍待答复。

- [14项决定与原条目快照](../decisions/2026-11-06-defense-review-approval.md)
- [编号与授权边界登记](../decisions/2026-11-06-defense-review-approval.json)

D317、D298、D312、D313、D69、D72、D68、D70、D74、D71、D73、D75、D76、D78、D79、D94、D90、D87、D97、D89、D92、D88、D91、D98、D99、D102、D103、D106、D109、D111、D112、D113、D114、D115、D116、D117、D126、D132、D133、D131、D124、D136、D137、D145、D147、D150、D152、D159、D154、D158、D155、D156、D153、D160、D162、D161、D163、D164、D165、D168、D169、D170、D173、D174、D175、D178、D179、D180、D183、D184、D185、D167、D172、D177、D186、D191、D188、D189、D190、D194、D195、D196、D197、D198、D208、D209、D205、D206、D207、D203、D210、D211、D212、D214、D215、D216、D219、D221、D222、D223、D228、D200、D224、D213、D217、D241、D236、D246、D255、D256、D252、D250、D243、D262、D266、D267、D268、D271、D272、D273、D274、D279、D290、D285、D295、D294、D288、D283、D280、D284、D300、D304、D301、D302、D303、D308、D309、D310、D314、D134、D135、D138、D144、D108、D128、D129、D299、D281、D287、D292、D293、D316、D45、D47、D48、D50、D51、D56、D57、D297、D39、D40、D38、D43、D44、D86、D85、D122、D118、D52、D53、D55、D139、D140、D143、D259、D260、D261、D263、D264、D265、D257、D270、D230、D232、D233、D276、D277、D240、D237、D238、D245、D249、D254、D234、D235、D251、D253、D120、D239、D242、D244、D247、D248、D220、D58、D65、D62、D77、D101、D49、D59、D60、D46、D201、D202、D269、D66、D67、D123、D127、D84、D289、D41、D218、D93、D95、D96、D42、D63、D64、D61、D104、D141、D146、D148、D149、D151、D176、D182、D157、D166、D171、D142、D181、D187、D192、D193、D204、D225、D226、D227、D229、D231、D121、D125、D275、D278、D282、D296、D305、D311、D199、D130、D315、D286、D291、D82、D83、D105、D258、D80、D100、D119已按决定实施并复核，其余6组待实施或复核，不能当作280组整改完成。实施前提未获证据支持时重新登记具体缺口；未发现代码不在本次授权内。D01—D37沿用原授权。

D318已另获授权并完成两处商店时间范围整改；决定见 `docs/decisions/2026-11-06-shop-time-range-approval.md`。

## D319 · 待用户审核（2026-11-06）

位置：current_reward_origins_view.open_event 的 named347 分支。D153后内部创建只返回窗口或抛出错误，None分支不可达。此前D159决定保留工厂None保护，建议仅删除具名分支的该检查；关键奖励分支仍保留。替代：保留现状。尚未获答复，不删除，不视为已批准。

## D320 · 待用户审核（2026-11-06）

位置：current_reward_origins_view.open_event 的critical349工厂返回None检查。传入本次已核验快照后不会返回None，建议删除此调用后的分支；独立工厂来源无效时仍返回None，实际子面板失效清理仍保留。替代保留现状。此前D159批准保留，故本批先询问不删。

## D307补充 · 缺字段策略待确认

`original_reference`当前跳过原记录已不存在的字段。建议缺少参考要求字段时也拒绝匹配；影响为不完整资料不再沿用持有条件，替代为维持原规则。等待用户答复，同次原件读取复用已完成，不改缺字段行为。

2026-11-07 实测：六条原选择的目录投影均含 title、description、lockedCoverDesc、type、nextSceneId、isHiddenChoice，原始 id 位于目录键。去掉其中一条的 lockedCoverDesc 仍会通过。已提请确认六个字段必须存在、原始 ID 匹配，以及其他共有字段继续逐项比对。

## D321 · 浮游单元等级默认值待确认

`drone_traits.selected_drone_trait` 用 `scenario.get("level") or max_level`，使0、False、空字符串等都按满级处理。建议调用已有 `catalog.resolve_cultivation`，仅缺省/None默认满级，其余非法等级报错；保留模组来源与适用性条件。不在此前列明的培养默认值六项授权内，已提问，未修改。替代：维持现状。

## D322 · 事件配图类型异常捕获待确认

`player_map_reference.event_picture`捕获 `_event` 的ValueError及TypeError后返回无配图。`node_catalog._text`用ValueError拒绝无效事件名；TypeError会来自内部类型或资料缺陷。建议删除TypeError捕获，保留ValueError未知事件处理；代价是内部缺陷将直接上报，不再显示无图。替代保留现状。发生率无统计，不在原280组内，已提问且未修改。

## D323 · 历史节点时间范围待确认

`player_recorded_scene.recorded_context`对history记录的at执行math.isfinite，10**1000会抛OverflowError，隔离输入已复现。建议先拒绝超出浮点范围的时间，保留同时间/标题/位置及唯一归属要求；不改原件、不重试。替代维持现状。实际发生率未知，D318仅授权商店入口，不覆盖这里；已提问且未改。

## D81补充 · 连线缺端点展示待确认

PreviewMapView.paintEvent跳过端点不在当前节点集合中的连线。存档入口只校验连线是两个字符串，未校验成员关系，故并非已证明的重复检查。建议保留局部跳过，其余节点继续显示；替代为预览入口拒绝整张坏图并提示结构错误。实际发生率未知，已询问，等待答复，未改。

2026-11-07 已提请确认只在地图预览装入当前图时选出两端有效的连线，后续重绘直接使用；缺端点的原始存档保留。

## D324 · 四处旧首领文献异常出口待审核

`boss_phase_reference._packet`、`boss_cycle_reference._packet`、`boss_hunt_reference._packet`、`gold_boss_reference._packet`仍将KeyError/TypeError/AttributeError等内部缺陷转成资料不可用。建议逐处核实异常契约，将捕获仅限实际文件读取、JSON解析与路径拒绝；内部结构错误直接上报。范围未包含于原280组明确授权，已统一询问，未改。替代保留原捕获；发生率无统计。

## D326 · 事件条件页的超大时间值

临时 RunState 存档的 last_read 为 10**1000，重新读档后该数值保留。observed_event_context 调用 _time 的 math.isfinite 时抛出 OverflowError，事件条件读取中断。建议仅在 _time 拒绝超过浮点范围的整数，使用既有时间不可用分支。替代为保留现状。D318 只批准商店入口。D326 已询问，等候审核。

## D327 · 悬停卡构建节点资料

player_map_hover.py 绘制卡片时把 ValueError、TypeError、KeyError 全部视作无节点资料。建议仅处理 NodeQueryError、文件读取和文本/JSON 解析错误，其他条目照常显示，内部缺陷直接上报。已询问，等待决定；此处未改。D82 只覆盖卡片条目跳转入口。

## D333 · 可计算技能遇到未核验培养字段

固定资料的32名可计算干员均未使用本次发现的费用或阻挡模组字段。若未来其资料出现未支持字段，需要决定保留可独立证明的技能分项，还是暂缓整项技能计算。已询问。此次仅实施属性读取和展示，不新增技能级拦截。

## D336 · 具名选项物品的异常出口

documented_choice_items._validated_packet 把资料读取、JSON 解析和内部结构异常均转成不可用。建议仅保留文件/解析错误与原有身份、清单核验失败的提示，内部缺陷直接上报。已询问，未改捕获范围。

## D337 · 具名奖励资料的异常出口

named_reward_items._verified_packet 捕获普通 ValueError、TypeError、KeyError、AttributeError、IndexError、StopIteration 和 RecursionError 等。建议保留实际非法公开路径、读取或解析失败以及有定义的来源不匹配；内部缺陷上报。已询问，未改捕获范围。

## D338 · 聊天设置分步保存

MainWindow.save_settings 捕获所有异常。凭据写入成功后，配置写入失败也会显示相同提示。建议仅在各自保存入口处理已知的输入、凭据及文件错误，明确已完成的步骤，界面错误直接上报。已询问，等待决定。

## D339 · 藏品来源卡的异常节点关联

来源卡直接读取每行对象；公开索引允许节点关联中出现非对象行，地图导航会跳过这些行。是否让来源卡也保留其余有效行，等待用户决定。

## D340 · 来源更新时间的解析与展示

ItemSourceIndex.describe_pool 对解析、时区换算及文字展示合并捕获 ValueError、TypeError、AttributeError。建议仅在来源字段无效或缺时区时显示时间未知；其余内部错误上报。已询问，等待决定。

## D341 · 公开频率超大整数

public_archive.members 收到 occurrenceRate=10**1000 时，math.isfinite 抛出 OverflowError。隔离样例已复现；本次公开数据逐池比对均可完成。建议在该频率入口先拒绝范围外数值，保留原始次数、分母和其他成员。已询问，待决定。

## D342 · 交换资料读取错误出口

related_exchanges 将 ValueError、KeyError、TypeError、AttributeError 同时当作无交换记录。建议先核实来源错误契约，将其与已验证资料上的内部异常分开；D317 已批准的来源身份要求继续保留。等待用户决定。

## D343 · 完整资料页的来源时区

ArchivePanel.render_members 将没有时区的时间按本机时区换算；悬停卡显示来源时间未知。建议两处仅对带明确时区的有效时间换算，其他显示待确认。已询问；D340 的异常捕获范围另行确认。

## D344 · 旧版图鉴补充资料错误出口

public_compendium.complete 对补充文件读取、解析、来源字段及内部错误一并回退到基础目录。建议保留可核实的来源失败行为，仅收窄异常范围。等待用户决定。

## D345 · 整份替代图对照文件缺失

relic_display_records 在等价图对照或补充清单缺失时返回剩余映射并缓存。原图及文字仍可用。是否对整份文件缺失给出资料状态提示，区别于单张图未取得，等待决定。

## D346 · 作战包读取出口

current_battle_reference.packet 对文件读取、来源解析和内部结构错误统一返回资料不可用。建议核实输入和上游版本包的错误契约后收窄捕获，保留既有路径及来源身份检查。已询问，等待决定。

## D347 · 敌人声明字段与损坏字段

当前已定义的行动／免疫字段若缺值或类型错误，读取器会跳过该次写入，保留此前的有效声明。缺失和显式未定义仍是正常状态。是否保留对损坏字段的现有处理已询问。

## D348 · 敌人环境分项错误出口

preview_environment 沿用原 enemy_preview 的 ValueError、KeyError 捕获，生成本局环境无法确认提示。建议先区分实际条件/来源失败与内部错误，再收窄。已询问，等待决定。

## D349 · 培养入口的信赖错误类型

旧公共入口用 math.isfinite(trust) 读取信赖，文字或空值产生 TypeError，浮点范围外的整数产生 OverflowError。D110 已将培养步骤与后续计算拆开，内部普通 ValueError、KeyError、IndexError 直接上报。是否在数值转换处将两种非法信赖异常归为 CultivationInputError，待用户决定；涉及直接调用者的异常类型。

## D350 · 分队效果列表输入错误

已确认分队合并效果时，effects 为 null 会在 list 转换处产生 TypeError。建议仅在转换点归为 RunConditionError，以取消实验对整段设置的 TypeError 捕获。直接调用者的异常类型会变化；已询问，待决定。

## D354 · 藏品文字框坐标解析

held_cards._bounds 捕获坐标元素读取或 float 转换时的 TypeError、ValueError、IndexError。错误文字框返回 None，调用者跳过该行；错误的页脚框使本页无法确认持有。建议保留这一解析出口；替代为让错误直接上报。实机触发率未知，等候决定。

## D355 · 藏品文字行置信度解析

held_cards._observed_lines 捕获 float 转换的 TypeError、ValueError，随后跳过该行。建议保留，使其他行仍可参与识别；替代为上报本次识别失败。实机触发率未知，等候决定。

## D356 · 藏品页脚置信度解析

held_cards.held_card_regions 捕获“收起”按钮置信度转换的 TypeError、ValueError，返回空卡片列表。建议保留这一入口处理；替代为上报本次识别失败。实机触发率未知，等候决定。

## D357 · 页面控件图缺少校验摘要

PageFeatureRouter 初始化时仅在 patch_sha256 有值时校验控件图。当前五组资料共20个控件均有摘要，三份构建脚本也均写入摘要。在隔离副本删除其中一项后，五组资料仍全部加载。建议缺失时报告资料错误并使用已有整帧识别；代价是缺少摘要的旧包无法再用于快速定位。替代为保留兼容。实机发生率未知，待决定。

## D358 · 动态 OCR 局部区域解析失败

dynamic_ocr.normalize_regions 将坐标解析的 ValueError、TypeError、OverflowError 转成 None，取消该组区域限制。已复现含不可解析字符串坐标时返回 None。建议保留此解析出口，识别器继续使用当前整帧范围；代价是调用方传错参数时可能只表现为识别变慢。替代为上报参数错误。实机触发率未知，待用户决定。

## D359 · 纯视觉整帧缓存标识的异常范围

VisualReader.read 的 TypeError、ValueError、AttributeError 捕获目前覆盖上下文取值、confirmed_config、ORB 设置与 JSON 序列化。隔离样本在额外记录含集合时连续两帧都跳过整帧缓存。建议仅处理 JSON 序列化的 TypeError/ValueError，配置提取或设置读取错误正常上报。替代为保留原范围。实机触发率未知，尚未改动这处异常处理。

## D365 · 地图选中回调与节点目录的构造顺序

MainWindow 先建地图页并连接选中信号，之后才创建 node_catalog。map_node_selected 每次用 hasattr 跳过目录尚未创建的情形。建议在目录就绪后连接相关选中回调，再直接访问目录；替代为保留现状。启动阶段发生率未知，待决定。

## D366 · 相邻节点文字报告的缺端点提示

连接信息查不到相邻端点时显示一行“连接端点位置未确认”，继续列出其他邻居。建议保留；替代为只略去该行。普通及历史报告保留原语义，已在隔离图复现，真实频率未知。D81 是画线出口，授权分别记录。

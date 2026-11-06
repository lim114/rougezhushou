# 低概率防御统一待审核清单

用户要求统一汇总后审核。以下只登记，未获得新授权、不修改去留；D01—D37既有决定继续有效。清单仍在补充，不是全程序穷尽清单。普通重复校验和单次抽取问题继续独立整改。

| 编号 | 位置与触发条件 | 影响 | 建议与替代 |
| --- | --- | --- | --- |
| D38 | `player_enemy_search.py`：matches：非字典敌人/非字符串查询返回False；资料片段非字符串被忽略 | 坏数据静默当作不匹配，可能隐藏内部类型错误 | 核对当前读取入口契约后删除内部坏类型兜底，或保留并注明过滤范围 |
| D39 | `credentials.py`：read_key捕获所有pywintypes.error并返回空密钥 | 系统访问失败与没有保存密钥混在一起 | 建议仅已确认的“未找到凭据”返回空，其它系统错误上报；具体系统错误码待核对 |
| D40 | `player_file_messages.py`：file_issue未知非中文错误使用“原件和当前编辑均保留”通用提示 | 该函数本身无法证明调用者是否已经写入 | 建议保留中文提示但改为不声称保存状态的文案；替代为原样显示错误 |
| D41 | `player_source_map.py`：targets对缺索引/池/坏行返回空；companion通过hasattr/getattr查找可选宿主 | 避免在没有对应资料或宿主时导航，但可能静默吞掉内部类型/属性契约破坏 | 需分别保留正常缺资料状态、核准可选宿主协议后删除多余坏结构兜底 |
| D42 | `observed_map_symbols.py`：mapping_for文件读取失败、摘要/版本/关卡对照不符返回None | 避免错误地图标记；公开数据损坏或版本漂移时不显示补充点位 | 建议保留来源绑定；不能仅因字节摘要存在就删版本检查，代码版本也可能变化 |
| D43 | `manual_scenario.py`：parse_preview_object拒绝重复JSON字段和非有限数值 | 避免编辑器接受歧义字段/无限数值；这些输入不能用于临时计算 | 建议保留；普通JSON语法/对象入口与框架解析回调不当作单次包装删除 |
| D44 | `tomimi_reference.py`：target缺资料/无对应level或名称不符返回None | 避免跳错关卡；不同版本无法对应时网页入口不可用 | 建议保留身份对照，替代为允许仅按level匹配或暴露缺项 |
| D45 | `node_statistics_source.py`：构造捕获OSError/ValueError/KeyError/TypeError后静默使用空索引 | 缓存/默认数据失败不阻止启动，也可能吞掉索引内部缺陷 | 建议把捕获收窄到读取/输入解析，内部构造缺陷暴露；model.load与FrequencyIndex重复验证已独立整改，捕获保持原样 |
| D46 | `reference_image.py`：set_data缺图/PNG解析失败显示替代文字，_fit在无图时跳过 | 图片缺失时保持可读界面；不能把解码成功路径的检查与空窗口resize回调机械合并 | 建议保留缺图/解码失败展示；无图resize是正常生命周期状态 |
| D47 | `player_map_reference.default_frequencies`：读取默认统计或构造索引发生ValueError/KeyError/TypeError/OSError时返回空索引 | 不阻止地图打开，也可能掩盖内部索引缺陷 | 建议仅保留读取/格式错误提示并暴露内部缺陷；替代为保持静默空索引。去留未批准，原捕获未改 |
| D48 | `player_map_reference.historical_rows`：查询索引发生ValueError/KeyError/TypeError/OSError时返回空行 | 查询失败与确实无统计混为一类；可能吞掉内部错误 | 先明确无覆盖位置的正常返回，再收窄输入错误范围；替代为保持现状。去留未批准，原捕获未改 |
| D49 | `rouge/player_context.py`：recent_content对非字符串title返回空文字 | 坏记录显示为没有最近内容，避免Qt收到错误类型 | 建议在本局记录入口统一校验后删除内部类型兜底；首次未读的正常空值路径保留。需先核对所有记录入口 |
| D50 | `rouge/player_action_menu.py`：expose_original_controls以getattr默认False容忍diagnostic_controls_exposed尚不存在 | 重复调用恢复按钮时不重复迁移控件，但缺属性由默认值隐藏 | 建议构造时初始化False并直接读取，保留重复展示的正常幂等分支 |
| D51 | `rouge/player_action_menu.py`：诊断恢复按钮前，菜单不在父布局时抛ValueError | 避免按负索引插入，暴露布局被外部改动 | 建议保留该调用时布局检查；替代是让Qt处理无效位置。未证实实际触发率 |
| D52 | `rouge/player_spawn_filters.py`：group_key队列类型/分组整数无效返回None；action_rows未知focus返回空 | 拒绝把坏分组或未知筛选扩成全部出怪条目 | 建议分别保留有效筛选入口校验，核对上游资料契约后处理内部结构兜底；本批只删除调用方对同条记录的重复group_key |
| D53 | `rouge/player_tile_information.py`：格子/地块类型及行列不合格返回提示，非文字或未收录标签显示未知 | 避免坏位置被显示成有效地形；新增游戏标签不会被猜成既有标签 | 建议保留未知标签展示；结构验证能否只留上游入口待逐调用确认，当前不删 |
| D54 | `rouge/player_recorded_scene.py`：content_context及recorded_context对坏类型、空标题、无效索引/时间/身份字段返回None或跳过 | 异常历史记录不会导航到资料，内部损坏也会静默被过滤 | 建议核对历史加载契约后区分入口拒绝与内部重复检查；现在不把所有空值路径当作冗余删除 |
| D55 | `rouge/player_recorded_scene.py`：确认记录须same_frame_selected_node来源；旧记录按时间/标题/位置匹配，仅一个唯一内容才返回 | 防止历史条目关联到另一节点或把歧义记录当唯一内容 | 建议保留来源及唯一身份对照；替代为允许选择候选，涉及产品行为，未授权 |
| D56 | `rouge/player_resource_history.py`：numeric_read遇到巨大整数转换为浮点溢出时捕获OverflowError返回False；count调用方同样沿用此结果 | 避免异常资源读数使列表构建中断，但坏数值按未读显示 | 建议保留入口的有限非负数规则；溢出捕获是否保留单独确认，暂不改变 |
| D57 | `rouge/player_resource_history.py`：ResourceHistoryPage.refresh通过getattr默认None读取未初始化的run_id | 首次刷新允许属性缺失，后续换局会清除旧选择 | 建议在构造时初始化run_id并直接访问；保留换局重置选择的正常行为，尚未授权 |
| D58 | `rouge/player_resource_history.py`：resource_rows遇到非字典历史记录或非字符串resource时跳过 | 损坏历史记录不会阻断剩余列表，但内部类型错误被静默隐藏 | 建议核对历史加载入口契约后决定保留入口过滤或暴露内部错误；本批未改 |
| D59 | `rouge/record_flags.py`：record_flag缺字段沿用True，已存在但不是精确bool则返回None | 保留旧格式语义，同时拒绝把文字/数字当作当前持有或在队 | 建议保留旧格式与三态区分；替代是要求全部记录显式迁移。涉及私人状态，未经批准不改 |
| D60 | `rouge/record_flags.py`：metadata_mask无效名单屏蔽全部本局元信息；projected_run_metadata对坏qualified_char_buff_ids改为空投影 | 原件不写回；坏元数据不被当成已确认招募或强化事实 | 建议保留只读未知投影，核对入口后再决定内部重复校验；不自动修复私人记录 |
| D61 | `rouge/relic_quantities.py`：confirmed_bar_counts与kettle_copies要求完整明确图标栏、唯一非水壶ID、数量及持有身份一致 | 不从大数字或部分图标推算重复水壶份数；缺证据返回None | 建议保留数量证据对照；与概况重复读取标记的跨调用优化仍待核对，不削弱这些条件 |
| D62 | `rouge/relic_quantities.py`：kettle_copies在任一合并记录不是dict时直接返回None | 坏历史条目不会在数量判断中触发类型错误，整组水壶数量暂时未知 | 建议在记录读取边界统一处理后再决定此内部整表检查去留；本批保持原样 |
| D63 | `rouge/run_metadata_view.py`：format_run_buff_status遇到未收录的强化ID时显示无法识别提示，不继续显示为已确认强化 | 避免给未知ID补名称或使混合名单看似完整；原始ID仍保留供计算入口拒绝 | 建议保留未知ID提示；若调整为只显示已知分项需明确展示口径。原分支未改 |
| D64 | `rouge/player_team.py`：qualified_fields在只读副本中移除非整数、超范围、无对应模组或模组阶段矛盾的字段 | 坏保存/读取数据不作为有效培养展示；原记录不写回 | 建议保留范围条件；先确认是否可由上游入口保证结构，再决定内部类型过滤去留。重复invalid_fields读取已独立精简 |
| D65 | `rouge/player_team.py`：crew_rows遇到非字典干员记录时跳过 | 损坏单条不会阻断整队展示，但内部错误被隐藏 | 建议在记录加载边界处理后再决定内部跳过是否保留；账号范围/已离队过滤是正常功能条件，不在本条删除范围 |
| D66 | `rouge/player_personal_statistics.py`：unique_archives跳过坏记录/非字典state/空或非文字对局ID | 坏档案不混入统计；正常同局多版本去重另属功能规则 | 建议核对store入口后确定内部坏结构过滤是否还需保留；不删同局去重 |
| D67 | `rouge/player_personal_statistics.py`：nonnegative_integer拒绝超过浮点显示上限的整数；complete_inventory拒绝坏集合、坏记录、未知持有身份或数量不符 | 不把不可核对归档放进完整清单分母 | 保留正常分母定义；巨大整数/内部坏结构检查需要单独确认。重复record_flag读取已移除，返回规则未改 |
| D68 | `rouge/player_personal_statistics.py`：refresh捕获store.records的OSError/ValueError/TypeError/RecursionError，清空旧统计并提示 | 历史读取失败不展示旧结果，也可能吞内部类型/递归缺陷 | 建议保留真实文件/格式失败出口，并在store契约核对后收窄内部错误；目前原捕获不变 |
| D69 | `rouge/player_personal_statistics.py`：statistics返回前深拷贝已新建的结果字典 | 现有正常资料中结果只含新建容器与标量，拷贝不增加隔离效果；可能为异常共享目录值保留隔离 | 建议删除这次拷贝；先作为既有保护登记，等待确认，不扩展到sample_rows中的原始字段复制 |
| D70 | `rouge/player_statistics_samples.py`：numeric_value捕获AttributeError/TypeError，将坏嵌套资源结构当未读 | 坏记录不进入数值样本，内部结构错误也被隐藏 | 建议由档案入口统一处理结构，再决定这层捕获；本批未改 |
| D71 | `rouge/player_statistics_samples.py`：sample_binding拒绝非字典/非文字ID/不满足64位十六进制的摘要 | 无可核对身份时不开放归档跳转 | 建议保留身份绑定，不以仅有对局ID替代；后续可只在明确入口解析一次 |
| D72 | `rouge/player_statistics_cohorts.py`：select_cohort收到非法难度或分队类型返回空列表 | 错误筛选不会退化成全部归档，但可能显示成无样本 | 建议保留入口参数规则并决定是否改为明确错误；目前原分支不变 |
| D73 | `rouge/player_floor_resources.py`：snapshots跳过坏事件、错来源、未知区域和不可核对数值/容量 | 历史层资源不借用当前值或猜测坏记录 | 来源/同帧规则为正常功能约束；坏结构容错建议待入口契约核对后决定，当前不删 |
| D74 | `rouge/player_floor_resources.py`：FloorResourcesPage.refresh通过getattr默认None容忍未初始化identity | 首次刷新以缺属性代表未加载 | 建议构造时初始化identity并直接读取，正常未选条目判断保留；尚未授权 |
| D75 | `rouge/player_shop_memory.py`：qualified对坏快照/坏商品行、名称身份不匹配、重复商品返回None | 防止不可靠记录作为已读商品；一个坏行使整个快照不用于展示 | 建议保留身份标准，核对入口后区分重复验证与坏结构兜底；本批未改 |
| D76 | `rouge/player_shop_memory.py`：remember拒绝不同局、非数值时间或超过2秒的请求 | 旧悬停结果不会写进另一局；不重试也不修改原记录 | 建议保留写入归属和新鲜度边界；其阈值不因精简放宽 |
| D77 | `rouge/player_shop_memory.py`：recorded_shops跳过坏历史事件/非有限或负时间，资料缺失时返回空 | 无法核对的商店记录不用于对比；不替原件补数据 | 建议保留缺资料状态并核对历史入口是否已覆盖类型过滤；当前不改 |
| D78 | `rouge/player_shop_memory.py:ShopMemoryPanel.open_source`：先调用refresh（会reload_sources），随后无对话框或异步等待又reload_sources | 第二次文件状态检查可读到恰在两次调用间变化的公开资料；通常重复stat，资料变更时可能重读。未证明是有意防御，按用户要求先保留待审 | 建议删第二次调用，采用本次refresh取得的来源；外部资料若恰在调用间改变，下次操作再更新。不改reload_sources内的错误处理，不新增缓存或重试 |
| D79 | `rouge/player_map_find.py:NodeFinder.__init__`：原rows中的非字典content/非文字title忽略逻辑原样迁入；仅登记异常内容结构的过滤 | 坏内容不会成为搜索标题，但也会隐藏历史结构缺陷；正常未读取内容和same_frame_selected_node归属要求另属功能规则 | 建议保留同帧绑定规则，异常结构过滤待历史入口契约核对后决定。当前只移动原表达式，未删校验或新增恢复 |
| D80 | `rouge/player_map.py:node_sprite`：已声明图标的sprite缺失时返回空图；alpha裁剪无有效像素时沿用原图 | 缺素材仍能画未知节点，坏图可能被静默隐藏；不含正常未知类型 | 建议区分未知类型和已声明素材损坏；本批未改原分支，待确认是否保留静默处理 |
| D81 | `rouge/player_map.py:PreviewMapView.paintEvent`：连线任一端不在节点坐标表时跳过该连线 | 不因坏边中断绘制，也可能漏显结构错误 | 建议核对地图入口契约后决定；当前原样保留，不补边或猜坐标 |
| D82 | `rouge/player_map.py:MapPanel.open_hover_entry`：node_dossier的ValueError/KeyError/TypeError直接返回False | 坏资料阻止跳转且保留查询，内部类型或键错误也被吞掉 | 建议把真实资料失败与内部缺陷分开后收窄；本批不改捕获范围 |
| D83 | `rouge/player_map.py:MapPanel.selected`：node_dossier的ValueError/KeyError/TypeError变成节点资料错误提示 | 本次不继续展示资料，也可能掩盖内部缺陷 | 建议只保留资料入口已定义的失败；先核对下游错误类型，当前保持 |
| D84 | `rouge/player_map.py:MapPanel.remember_entry_reading`：reading_key元素不是非空文字或根分组标签不是文字时跳过保存 | 坏身份不写入阅读记忆；也可能让内部初始化问题表现为阅读状态丢失 | 正常未选节点分支保留；异常类型保护待确认，当前不变 |
| D85 | `rouge/player_map.py:MapPanel.check_reference`：getattr默认None读取node_reference_binding/panel，hasattr容忍无refresh_reference方法 | 兼容不同资料窗口接口；也可能掩盖漏初始化的属性 | 建议逐类核对窗口契约后统一接口；不在本批擅自删除可选读取 |
| D86 | `rouge/player_map.py:MapPanel.open_entry`：make_reader没有返回精确浮窗时转到原完整目录并激活主窗口 | 仍能查资料，但会改变打开位置且可能掩盖缺少精确入口 | 建议明确哪些类型仍需该备用路径后决定保留范围；本批未触发或改变它 |
| D87 | `rouge/player_map_reader.py:readable`：dialog为None时不应用主题、直接返回None | 兼容未构造成功的可选窗口；也可能掩盖调用者漏创建窗口 | 建议先逐个核对调用方是否确实会传None，再决定保留范围。当前原函数未修改，prepare_reference_window等多调用入口仍保留 |
| D88 | `rouge/player_map_reader.py:make_reader`：record非字典或id/title非文字时返回None | 不让坏资料进入事件/作战构造；调用方可能把坏输入当作无精确入口 | 建议与上游资料入口契约合并核对后决定；当前类型检查不动。正常未支持类型、资料暂不可用与这一坏输入保护分开 |
| D89 | `rouge/current_event_directory_view.py:make_event_dialog`：target或target.event不是字典时直接返回None | 拒绝错误类型进入资料构造，但把错误调用表现为无法打开资料 | 建议核对model.resolve与外部调用契约后决定是否保留此入口保护；本批不动。真实来源身份、场景和选项对应核对另属资料准确性条件，不据此一并删除 |
| D90 | `rouge/current_event_directory_view.py:CurrentEventDirectoryPanel._close_event`：hasattr(panel, clear_reference)为否时跳过清理，仅关闭窗口 | 兼容缺少清理方法的面板，也可能掩盖不完整接口并保留旧资料 | 建议逐类确认21个面板契约后改为直接清理；本批保留，等待审核 |
| D91 | `current_event_directory._file`：拒绝非规范路径、链接、目录外路径及链接父目录 | 约束公开资料读取位置；主动使用链接迁移资料也会被拒绝 | 建议保留路径归属保护，核对类型校验先后；本批整个函数不变 |
| D92 | `current_event_directory.packet`：捕获OSError/ValueError/KeyError/TypeError/AttributeError/StopIteration/RecursionError并返回None | 文件损坏与内部程序缺陷都变成来源不可用 | 建议保留文件/解析错误出口，逐路径核对后收窄内部缺陷兜底；本批捕获不动 |
| D93 | `current_event_directory.packet`：清单摘要、schema/版本、字节数、来源身份、快照、重复ID及固定39行/38组不匹配即拒绝 | 绑定固定来源并防止混入错误资料；扩充资料需同步固定口径 | 建议保留来源绑定，分别评估固定数量与身份保护；不能单凭低概率整组删除。本批所有检查不变 |
| D94 | `current_event_directory.reference`：query/event_id/node_type/topic类型、160字查询上限和已知topic检查 | 错误查询返回None；超长查询被拒绝而非截断 | 建议集中保留明确的公共入口契约，是否仍需160字上限待用户决定；本批不动 |
| D95 | `current_event_directory.resolve`：坏result/entry_key返回None，并重新读取与比对整份结果 | 阻止失效或被改写的资料跳转，但与后续窗口入口可能重复读来源 | 建议先核对两个实际调用时间点，再明确保留哪处完整核对；无选择属于正常状态，不能一并删除。本批不动 |
| D96 | `current_event_directory.derive/_snapshot`：缺绑定、缺来源、无对应事件、构建数量不符时抛ValueError | 资料构建停止，避免发布不完整目录；固定数量限制后续扩展 | 建议保留构建失败显露，固定数量约束与来源更新一起核对；_event仅内联，原有无事件失败分支保持 |
| D97 | `current_event_directory.packet`：来源说明NOTES先读取并验摘要，随后在清单循环再次读同一文件并核验；不是玩家笔记 | 能发现两次读取间文件变化，但同次调用重复I/O和路径检查。定向模拟第二次字节变化已确认返回None，未改文件 | 建议复用首份已验证字节，在清单循环保留类型/摘要校验，使同次解析使用同一快照；代价是不再发现读取后立刻变化。替代保留二次读取。本批不修改，等审核 |
| D98 | `player_reference_notes.note_for`：公开资料name不是非空文字时返回None | 坏标题被视为无资料，隐藏笔记入口；并不检查私人笔记正文 | 建议核准上游数据契约后在资料读取入口处理，内部不重复兜底；替代保留当前分支。未修改，待审 |
| D99 | `player_reference_notes`：菜单request先note_for再open_note/reference_target/note_for；open_reference先核对身份，刷新选择后再note_for比较 | 同次导航重复读来源，但选择信号可同步更新页面，末次比较能拒绝中途变化；菜单展开和后来点击是不同时间点，不能合并 | 建议只对确证无交互/信号间隔的链路传递一次核准结果；保留跨交互及刷新后的核对。替代保留现状。本批只移动context定义，不改校验 |
| D100 | `reference_dialog.ReferenceDialog.calculate`：解析和evaluator共同捕获ValueError/KeyError/TypeError | 输入错误有提示，计算器内部缺陷也变成输入提示；旧结果已被invalidate清空 | 建议逐个计算器明确输入错误出口后收窄到解析/输入校验，内部计算缺陷暴露；替代保留此出口。未修改，待审，不借D03授权扩大范围 |
| D101 | `timing.profiles`：公开timing-profiles.json不存在时返回空operators并缓存 | 允许缺资料启动，但缺文件可能表现为所有时序资料未知；恢复文件后缓存仍可能保持空 | 建议明确安装包必需文件契约后取消缺文件静默默认，或保留并提供来源缺失状态；本批未改，等待审核 |
| D102 | `amiya_continuous_reference.attach_result`：full缺amiya_continuous_reference时直接返回；当前唯一产品调用方已检查该项 | 允许绕过调用方单独调用时静默无操作；正常产品路径重复确认同一份结果 | 建议将被调用函数改为直接读取已确认项，保留调用方分派；替代保留可独立调用约定。本批未删，等待审核 |
| D103 | `relic_damage_factors.parameter_factor`已逐条verified_rule后调用source_factor，后者重新筛选并再次逐条核验同一来源 | 独立source_factor仍需入口来源核对；当前连用路径重复核对不含异步、I/O或用户交互 | 建议提取供两入口共用的已核验来源算式，两个入口各核对一次；不取消独立入口核验、不放宽来源绑定。替代保留当前双重核对。本批未改，待审核 |
| D104 | `shield_break_reference.finish_shield_break_reference`：ordinary(window_damage)为None时把已知窗口小计改成0 | 窗口小计不会空缺，但可能把尚不确定的来源当作零；需核对各生产路径是否可达 | 建议先核对可达生产者后保留未知或直接使用已证数值，勿把None自动视为零；替代保留并限定其前置条件。本批未改，待审核 |
| D105 | `panel_native_bridge._bits/_raw/prepare.term_value`：浮点打包或名义定点转换遇到OverflowError、struct.error、ValueError时返回None | 超大或无法转换的数值显示为未知；也可能把内部转换缺陷隐藏为资料不足。普通None未知输入与这些异常出口应分开核对 | 建议逐处限定可达输入后只保留实际数值范围错误，内部类型/格式缺陷暴露；替代保留原出口。三处捕获未改，term_value仅移出逐字段循环，原捕获体和范围不变；待审核 |
| D106 | `panel_native_bridge._record`：term缺省或空字典时以`term or _term(None)`补未知算式 | 支持缺项调用；当前prepare/finish三个产品调用点均传入算式，可能掩盖生产者漏传或空字典 | 建议确认独立调用契约后让term成为必传参数并直接使用，未知基础仍用明确_term(None)表达；替代保留缺省。未修改，待审核 |
| D107 | `catalog.operator_attributes`：潜能属性不在mapping或formulaItem不是ADDITION时忽略；模组属性不在小写映射时也忽略 | 新字段/公式不会中断计算，但可能漏掉有效加成；当前已适配干员模组字段均在映射中，全干员资料另有cost/block_cnt字段 | 建议明确支持字段范围后，对未支持项保留显式未知或限定来源，而非静默给完整结果；替代保留当前筛选并标明支持范围。此项不授权扩展费用/阻挡计算，本批未修改，待审核 |
| D108 | `catalog.operator_attributes`：阶段首尾等级相同则插值比例取0，避免分母为0 | 可表达只有一个等级点的阶段，结果取首帧；本批固定全干员资料中未出现此情形 | 建议按单等级资料的正式支持契约决定保留；替代在数据入口拒绝该结构并移除计算内分支。未修改，不以当前0例推断永远不可达，待审核 |
| D109 | `calibration_experiment._panel_value`重复检查data对象/键集合、observation对象类型；唯一产品调用方同一轮已核对这些结构 | 单独绕过调用者使用私有函数时有定制错误；当前正常链重复核对，values类型和非空仍是该函数首次检查 | 建议保留调用入口检查和values检查，删除已确认结构的重复分支；替代保留独立私有调用支持。本批未删除，待审核 |
| D110 | `calibration_experiment.calibration_experiment`每条记录的try涵盖结构检查、面板计算、条件比较和数值分析，捕获ValueError/TypeError/KeyError/IndexError/OverflowError并记为record_validation_error | 一条坏记录不会中断其他记录，但内部缺陷也可能显示成输入错误 | 建议划清输入解析/校验边界，收窄捕获范围并保留坏记录可见；替代保留现有隔离。捕获体、类型与覆盖阶段不变，本批仅复用阶段内已有面板；待审核 |
| D111 | `calibration_experiment._timing_value`再次检查data是字典且仅含scenario/observation；唯一产品调用方已在同轮核对完全相同结构 | 支持绕过调用者直接调用私有函数时给定制错误，当前链重复检查；底层compare_bounded_timing自己的公开入口仍需有效输入校验 | 建议只删除此私有适配器的重复结构分支，保留调用入口与底层时刻数据校验；替代保留私有独立调用支持。本批未改，待审核 |
| D112 | `timing_calibration._number`在数值入口捕获OverflowError及ValueError；本项只涉及其中ValueError | 内建int/float的有限性/非负检查已能按正常错误路径拒绝坏值；10**1000可实际触发OverflowError，需保留。ValueError在当前JSON基础数值输入中没有触发证据，可能容忍自定义数值子类错误 | 建议只删除ValueError捕获，保留OverflowError和原输入错误提示；替代明确支持自定义数值子类并保留该捕获。现有整处捕获未改，待审核；不将输入超大整数的OverflowError当作低概率兜底删除 |
| D113 | `bounded_calibration._number`捕获ValueError/OverflowError；本项仅ValueError | 超大整数实际需要OverflowError转输入错误；当前JSON基础数值中未找到ValueError触发，可能容忍自定义数值子类错误 | 建议删除ValueError、保留OverflowError与0–1e12输入范围；替代明确支持自定义子类后保留。现有捕获未改，待审核；不沿用D112作跨模块授权 |
| D114 | `bounded_calibration._bounds`缺少lower_exact/upper_exact时回退到浮点端点字符串 | 可兼容没有精确端点的旧结构；当前本模块与实验生产者均用_interval生成精确端点，正常链没有缺字段证据；回退也可能掩盖生产者丢失精度 | 建议先确认旧结构支持范围，再直接要求精确端点；替代保留兼容并注明精度来源。本批未改，待审核 |
| D115 | `bounded_calibration`校验两个容差后下传至有界比较入口再次校验；`compare_bounded_panels`又向成对比较传入已核验容差 | 各公开入口独立调用需要校验，组合链重复检查；组合入口当前连未使用分组的容差也会检查，不能随意改变 | 建议共享已校验值的内部比较路径，保留每个公开入口及未使用容差原契约；替代保留重复检查。本批只将时刻预测与观察比较分离，以上现存检查均未删除，待审核 |
| D116 | `bounded_calibration._panel_record`检查scenario/observation结构并只转换values，随后`paired_calibration._record`对相同记录结构再次检查 | 两个公开入口独立需要结构检查；转换后顶层键未变，组合路径的第二次检查保护内部传递契约 | 建议组合链使用已校验记录的内部入口，保留独立公开入口与全部观察字段验证；替代保留转换后复核。本批未改，待审核 |
| D117 | `relic_panel_diagnostics`先_scenario校验并规范化，再仅改relic_ids交panel_layers；后者_scenario再次检查字典类型/内部前缀及已填默认值 | 独立面板入口需要校验；诊断内各组合未改变顶层结构或内部键，存在重复契约保护。最初仅首批三名的范围限制比面板支持范围更窄，必须保留；藏品本身各组合不同仍需各自准备 | 建议为已校验场景共享内部面板构造路径，保留诊断首批三名限制及所有逐组合藏品计算；替代保留嵌套复核。本批仅复用完全相同组合，没有删除这些检查，待审核 |
| D118 | `cultivation_comparison.compare_cultivation`第一处try包含培养输入检查、属性计算、档案查询及结果行更新，捕获ValueError/KeyError/TypeError后继续下一方案 | 坏方案可逐行提示，但档案/内部结果缺陷也会被归为方案不可测算 | 建议仅保留实际输入错误出口，界面行构造与内部结构错误暴露；替代保留整段隔离。本批捕获范围、类型和处理体未改，待审核 |
| D119 | 同函数第二处try捕获技能准备/计算、补充技能和结果行更新的ValueError，保留属性并提示技能不可测算 | 未解锁或无效技能可保留属性比较；内部计算中的ValueError也可能被当作用户条件问题 | 建议明确输入错误边界后收窄，保留未解锁技能的逐行提示；替代保留当前隔离。本批只传递已有培养属性，既有捕获未改，待审核 |
| D120 | `supplemental_cultivation.compare_cultivation`每方案run_skill_reference捕获ValueError/TypeError/KeyError并生成不可测算行 | 单方案失败不会中断其余方案，但内部缺键/类型缺陷也会变成输入提示 | 建议区分已知输入错误与内部异常后收窄；替代保留逐方案完整隔离。模块本批仅源码回顾，字节未改，待审核 |
| D121 | `cultivation_comparison`先_amount校验信赖并转float，紧接共享入口_operator_attribute_reference再次校验同一信赖有限性与0–100范围 | 两个独立入口各有输入契约，组合路径重复；_amount对布尔值的拒绝不能删除，其他调用者仍需要培养入口校验 | 建议保留外部入口拒绝布尔/范围规则，以已验证培养条件共用内部计算；替代保留重复范围检查。本批未改信赖检查，待审核 |
| D122 | `supplemental_run.run_skill_reference`无本局加成基准调用_skill_reference时捕获所有ValueError并返回baseline=None及错误说明 | 生命符文可能使声明缺口对加成后合法、对原生命不合法，必须保留这类可读缺项；其它内部ValueError也被隐藏为基准不可测算 | 建议限定为已知生命缺口校验错误，其它内部错误上报；替代保留当前所有ValueError隔离。现有捕获体/类型/范围未改，待审核 |
| D123 | `supplemental_comparison.comparison_rows`在baseline为空时改用空字段表，所有差值未知 | 可支持无基准调用；当前等级/培养/敌人三个产品调用方均提供已生成的非空基准及复用字段表，原报告入口仍保留，可能掩盖内部漏传 | 建议确认无基准是否是正式契约后决定保留，或要求必有基准并直接投影；替代保留现有无基准模式。本批未改此分支，待审核 |
| D124 | `supplemental_sp.sp_reference`对已声明bound_char_buffs的子记录使用get(id,{})、get(effects,[])，资料缺失时按空效果处理 | 固定资料15条关联当前均完整；若资料损坏或更新漏同步，可能把本应待确认的自然回技显示为已知 | 建议在资料入口核验已声明关联并上报缺失，消费处直接读取；替代保留当前空效果回退。未改这两处回退，不新增校验，待审核；可选bound_char_buffs不存在不在本项删除范围内 |
| D125 | `supplemental_skills._cultivated_stats`先验证精英/等级/潜能的整数类型和信赖范围，再调用operator_attributes重验同一字段 | 两个入口有各自输入契约，组合路径重复；补充入口还拒绝整数子类、布尔及信赖错误类型，不能简单删第一层 | 建议共用已验证培养计算，保留各外部入口的严格契约；替代保持重复。仅此补充技能入口，D121不覆盖此处；本批未改 |
| D126 | `supplemental_skills._skill_reference`对已由bonuses字典初始化的atk/max_hp/def仍多次get(key,0) | 本函数不会删除这三键，缺键只会来自内部构造契约被破坏；默认0会掩盖缺陷 | 建议三种已初始化键改直接索引；替代保留0回退。本批未改；cost/prob/atk_scale等真正可选天赋键和battle_attributes可选来源不在本项范围 |
| D127 | `supplemental_enemies.enemy_defaults`已有difficulty.value不是0–15整数时强制改为4 | 避免无效默认值进入表单，但可能把损坏/错误读取显示成真实难度4；初次无记录的正常默认另论 | 建议仅缺值采用正常默认，已有坏值显示待确认并提示；替代保留强制4。模块仅源码审查，原文件未改，待审核 |

| D128 | `summons.token_attributes`阶段首尾等级相同则插值比例取0 | 支持单等级召唤物阶段，避免除零；不是D108干员培养函数的同一授权位置 | 建议确认单等级资料契约后决定保留，替代在资料入口拒绝该结构。本批未修改，待审核 |
| D129 | `relics.finish`的regeneration_factor返回None时改用1继续展示已知回复小计 | 保留已知分项，但外部未核验组合也可能被当成无倍率；准备阶段正常会过滤未知组合 | 建议确认是否仅显示已证小计并标完整量未知，替代保留现有倍率1回退。本批未修改，待审核 |

| D130 | `token_module_comparison._compare_token_module`在verified字段计算differences时再次检查base[k]和values[k]均非None | 当前固定32名干员/792份对照中的42个已确认差值字段均非空；若未来确认字段仍缺基准或结果，现分支会静默省略差值 | 建议确认verified是否保证两端数值后删除重复判空；替代保留允许已确认字段缺差值的契约。本批未改，需审核；其它未知字段、无规则、未解锁分支不在本项范围 |

| D131 | `token_budget_view.TokenBudgetDialog.calculate`捕获ValueError/KeyError/TypeError，将计算异常改为界面提示 | ValueError包含正常输入错误，KeyError/TypeError也可能是内部结果或资料缺陷；缺陷被当作输入提示 | 建议核对入口错误契约后仅保留正常输入ValueError，删除其余内部类型/缺键兜底；替代保留原三类。尚未授权，原样保留 |
| D132 | 同方法使用row.get("stock_within_reference")容忍结果缺字段 | token_budget每行都生成此键；字段缺失会静默省略库存提示 | 建议改为row["stock_within_reference"]，仍保留正常None/False含义；替代保持缺键不提示。尚未授权，原样保留 |

| D133 | `token_budget.token_budget`以stage.get("count_reference")读取每个对照阶段必定生成的字段 | 缺键会被视为无数量参考，改变范围文字，掩盖上游结果缺字段；正常None仍是无资料 | 建议改直接索引，保留正常None含义；替代允许历史/自建结果缺键。本模块当前只接收即时对照结果，未发现历史结果入口。尚未授权，原样保留，暂不整模块销项 |

| D134 | `summons.duration_reference/module_reference/token_cost_reference/token_attributes`及`token_counts.token_count_reference`共五处用scenario.get("level") or 满级处理输入 | 缺少等级/None正常使用默认，但0、False、空字符串也静默当满级；直调资料函数会得到满级参考，当前主计算入口通常先拒绝这些值 | 建议明确仅缺省/None使用默认，其余由实际外部入口拒绝，已验证调用直接传培养；替代保留现有假值默认。五处统一待审，本批复用解析结果但保留原or语义；本机4类输入新旧结果相同 |

| D135 | `operator_engine.selected_talents`使用scenario.get("level") or 满级 | 未给等级是正常默认，但0/False/空字符串也会按满级选择天赋；深海色实际直调四种值均与70级相同 | 建议仅缺省/None使用默认，已验证培养从入口传入；替代保留假值默认。此项独立于D134五处，未改、待审核，不推定主计算入口允许这些值 |

| D136 | ammo_reference.refill_parameters及refill_before_empty_is_safe的两处OverflowError捕获 | 超大整数经math.isfinite转浮点溢出，分别返回None/False；现有10**400测试覆盖 | 建议保留数值入口的这两处错误出口；替代先限定范围再转数值。未改，待审核，不授权其它捕获 |
| D137 | partial_packet_reference使用get("partial_packet_rules",[]) | 固定资料缺该字段时静默作为无支持规则；当前资料有此字段 | 建议直接读取必填字段；替代保留旧格式缺字段兼容。未改，待审核 |
| D138 | mei_module_reference.reference的level or 满级 | 0/False/空字符串也按满级参与模组条件 | 建议仅缺省/None默认；替代保留假值默认。独立于D134/135，未改，待审核 |
| D139 | mei_module_reference.reference的part not in catalog_parts | 拒绝其它模组/培养来源的part被当成本模组资料；已有foreign_parts算例 | 建议保留来源核对；替代删除会允许外来条目进入候选。与后续index重复查找需一起考虑，未改，待审核 |

| D140 | gnosis_module_reference.selected_reference的固定资料身份组合检查 | 原坚冰名/字段、特性resKey/标签/参数、二三级4个prefab及resKey/目标/隐藏/标签任一改变时不输出已核验资料；现有unreviewed prefab算例覆盖 | 建议保留，防止新资料错套原规则；替代直接接受变更会把未核验来源标成已核验。只登记，未改；普通培养/候选适用性判断不在本项 |

| D141 | mei_module_reference共享参数入口查不到固定模组时返回无资料 | next默认None与module is None分支处理目录缺项；独立界面仍先严格next，缺项仍直接报错 | 建议保留参数入口无资料行为；替代删除后暴露固定源缺失。原分支不变，未扩大到界面，待审核 |
| D142 | mei_module_static_reference._qualification的封存stage→resKey与TRAIT绑定检查 | 参数存在但原生资源身份不符时禁止使用封存单包公式 | 建议保留来源绑定；替代仅凭参数数值接受会误套规则。检查原样保留，待审核；技能1/2适用范围不在此项 |

| D143 | relic_healing_factors.verified_flower_factor固定来源组合核对 | 多件叠加时核对藏品ID、原buff位置/key、数值、已核验标志及证据路径；不符返回未知 | 建议保留来源绑定；替代直接叠加会把未核验来源套用同一公式。未改，待审核 |
| D144 | susuro_healing/guardian_healing.selected_trait两处level or 满级 | 0/False/空字符串也被当作满级 | 建议仅缺省/None默认；替代保留假值默认。未改，独立于D134/135/138，待审核 |
| D145 | 上述两处candidate unlockCondition缺失/空值默认PHASE_0、等级1 | 缺少解锁资料时仍可能选中候选 | 建议改为必填读取或明确无资料；替代保留旧资料默认。未改，待审核 |
| D146 | 苏苏洛与古米/黍固定resKey及1.15/0.5参数匹配 | 固定源变化时拒绝套用封存受疗比例公式 | 建议保留身份/参数绑定；替代直接接受变化会扩展未经核验公式。未改，待审核；职业/候选适用性检查不在此项 |
| D147 | 两处attach_result对六个治疗字段及总治疗量使用get默认None | 结果缺字段时按未知继续而不暴露缺字段 | 建议确认结果契约后改必填读取；替代保留缺项兼容。本批只复用同一次读取，未删除缺项None行为，待审核 |

| D148 | recipient_native_ratio._source的OSError捕获、固定SHA256不符返回None及诊断未知传播 | 固定原件派生包读不到/字节不符时不计算封存数值，仍返回声明与未知结果；lru_cache也会缓存None | 建议保留证据绑定和未知出口，缓存失效策略另议；替代直接抛出或取消绑定会改变可用性/来源口径。原样未改，待审核 |
| D149 | recipient_native_ratio._cultivation查不到已选固定模组时ValueError | 输入身份已通过，但本地固定培养目录缺项时报告明确错误 | 建议保留；替代移除会在后续访问时报内部异常。仅此位置，原样未改，待审核 |

| D150 | RecipientNativeRatioPanel._append与calculate的ValueError/TypeError出口 | 正常格式/范围错误需要提示；TypeError还会把内部缺陷当输入问题，_append捕获范围也包含序列化与界面更新 | 建议保留正常ValueError提示、删除TypeError兜底并收窄_append到解析/验证；替代保留原范围。两处原样未改，待审核，不包含其它面板 |

| D151 | stage_floor_reference.sixth_floor_reference 的固定标题/区域/icon/原关卡字段及可选传入关卡身份比对 | 固定资料被换版、字段错配或调用者传入其它变体时返回None，避免把其它关卡标为第VI层；正常非对应关卡的无资料返回不属本项 | 建议保留来源与关卡身份核对，逐字段核实是否已由资料入口保证后再精简；替代直接信任构建数据会少一层版本错配拦截。本批原样，待审核 |
| D152 | current_named_reward_origins_view.make_event_dialog 首行row字典/item_id文字检查 | 错误内部调用返回None而不是暴露类型或缺键问题；当前唯一产品调用者从已刷新模型行中选择 | 建议在确认该调用契约后删这处类型兜底，内部缺陷直接暴露；替代保留独立原始输入入口。原样，待审核 |
| D153 | 同函数重新model.reference并确认整行属于fresh.rows | 用户点击时来源变化或条目被改写便拒绝打开；父open_event同次操作已刷新整份来源，可能重复读取 | 建议核实同次操作的来源快照边界后复用父层已核对结果，保留一次身份核验；替代保留两处，覆盖两次读取之间发生变更。原样，待审核，不借用D95授权 |
| D154 | 同函数七个已知reader分支之后return None | 模型新增或错误reader键时静默不打开；原模型实际输出固定七类 | 建议改为明确暴露不支持的内部reader，或在模型入口只接受已实现键；替代保留无窗口返回。原样，待审核，不包含七种正常分派 |

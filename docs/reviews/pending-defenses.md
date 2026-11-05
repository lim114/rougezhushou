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

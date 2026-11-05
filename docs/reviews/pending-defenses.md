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

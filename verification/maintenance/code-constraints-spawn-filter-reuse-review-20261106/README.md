# 维护：出怪列表复用队列筛选结果

CurrentBattlePanel._actions_changed过去为分组与条目各按kind筛一次完整actions。现保存kind_rows，分组与条目都复用，条目仅追加group/focus/enemy条件；显示总数仍取完整actions。筛选函数只读入参，无修改或事件处理。分组控件清空/选中期间信号阻塞，因此不在两个消费点间重新改变kind。未加函数、异常捕获或容错策略。

player_spawn_filters全文回顾：group_key与action_rows有多个调用，record_text负责实质资料格式化，不是单次转发。已有D52的分组资格、未知筛选及内部结构兜底待审，本批未动，不重复编号。current_battle_view只核对_actions_changed/focus_action，不将整个大模块计完成。

16项定向通过（13.405秒），覆盖主/条件分支、隐藏/随机/装置、敌人匹配、分组、零值、来源丢失、阅读状态及位置入口。未跑全量。窗口已更新、可见且响应，截图在.local/code-constraints-review-143。只减少同次刷新的重复筛选，不据此声称总体识别提速。初次搜索误包含数据文件且读取了不存在的控件文件，改为仅Python并定位真实current_battle_view调用；未修改数据。

覆盖仍为完整59、部分196、仅异常40、结构263；待审273组D38—D310。

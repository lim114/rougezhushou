# 地图资料入口契约整改

D88：删除make_reader的record/id/title合并兜底。作战调用者构造字典；标题不用调用方值，而从CurrentBattlePanel已核验结果取得。事件分支由binding_for独立入口核对完整资料；地图节点记录来自node_dossier。

核对调用位置：player_map、current_event_battles_view、player_cannot_links、player_calculation_target、player_note_reference、player_reference_links、player_scene_battle及两份功能验收入口。正常未知身份、来源丢失和未支持类型保持None；内部作战漏ID直接暴露。

25项定向通过：无调用方标题仍使用准确资料标题、缺ID抛出、事件调用绑定入口、未知类型、历史事件及作战来源拒绝、布局/主题。未跑全量。模块整体回顾状态暂不升级。新版测试窗口仍待用户退出旧助手后更新。

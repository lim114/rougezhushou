# 302调谐仪式阅读窗口候选

只准备`rouge/ritual_weakening_view.py`与`tests/test_ritual_weakening_view_302.py`。父NodeCatalog接线、旧文件、正式来源包和Git均由根代理负责。

`RitualWeakeningPanel.set_reference(event_id, *, scope_key=None)`。公开`choice/reading_tabs/player_text/source_text/packet/open_stage_button/battle_window/battle_preview`。仅六个完整选项，三条同名源私钥使用不同流程和选项序号。默认不选，选择只显示说明。原选项叙述与已核对的弱化效果分开；首次灾厄之口不毁危朽限定保留，伤害降低不当无伤，源私钥只替代对应一项需求，不表示一次替代全部步骤。

显式“查看相关作战：畸症”按钮前fresh核完整tuple和整row、固定stage reference_only及immediate_transition=null；不造转场token，不修改event_battle_links。独立QDialog懒加载现BattlePreviewPanel，不连接主App stageSelected、不改当前主战斗或父事件阅读。相同stage重复打开使用现set_stage，保对象不重载；同有效scope刷新不触碰子预览，保地图选点、wave/enemy/reward、context和读区。子窗手动关闭仅hide，重开可沿用；scope或source失效则清stage、close并deleteLater整树，两个属性None，恢复必须重选/再点击。

玩家页不显示原ID、URL或0.5配置参数；完整原对象在资料页。所有实际选择/消耗/附着/效果/数值/资格仍未知，计算与本局状态不写入。读区同范围选择及未选择均保留页签、选区与实际非零滚动；不同父scope/源scope清旧，source恢复不重选。

必要direct-QDialog测试最终13项，含6tuple→3效果/3私钥，交付替代/叙述与效果限定、8actual未知、显式真BattlePreview固定地图、关闭重开、同scope阅读与地图/对象保留、源失败整树清理、按钮fresh失败与跨私钥拒绝、source/父scope变化、warm临时源破坏、每refresh查询次数，以及预览依赖初始化失败清半建窗口/手选重试。runner把公开manifest和新模块复制临时ROOT，4环境目录临时；可只读引用既有公开BattlePreview依赖，不构造MainWindow、不采样、不聊天。正式Windows及父页状态验收由根代理执行，缓存检查不叠加其正式计数。

首12项实际5F（纯临时fixture漏既有公开node-events.json；原源码/完整stderr/process在first-real-direct-dialog）。补齐该文件，保留原12全部断言，并为UI预览依赖异常清理新增1项；corrected-direct-dialog实际13/0F0E/exit0，来源前后未变。准备命令的一次PowerShell引用错误单独说明在PREPARATION_ERRORS.md，不混成业务测试结果。最终SHA见HANDOFF。

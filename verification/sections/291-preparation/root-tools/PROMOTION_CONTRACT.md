# 291提升前静态核对：尚未提升、未运行测试或窗口

本清单不表示291已启动/完成。`PROMOTION_FILES.json`列出全部32项候选源路径、目标路径、候选SHA/bytes，以及每一项当前live是否存在和精确前置SHA。26项新建、6项替换；6项替换仅为app/map_view/event_planning/node_catalog_view/player_node_information及历史290集成测试。私人状态、配置、游戏样本均不在清单。

## 采用哪个版本

- 核心/UI/四份新测试及旧290测试迁移：`.cache/p3-291-window-candidate/revision3b/draft/**`。
- 数据、builder和8份原资料包：`.cache/p3-291-candidate/`中清单的精确路径。
- **窗口采用本目录`window/verify_peace_guardian_window_291.py`的新v2**，未来目标`scripts/verify_peace_guardian_window_291.py`。旧d52窗口原件保留，不用于最终提升。v2只补最终关闭后的zero-attempt gate，并区分被拦截尝试与实际执行；未改变产品。
- 两类必要测试前置原件也在32项内：精确原290规划模块，以及location fixtures/SCHEMA_EVIDENCE/schema-source。不得用当前修改后规划替代原对照。
- 资料包README/manifest保留其生成时的缓存准备身份和原字节；正式交付状态由本节功能回执/进度另记。随意修改这些被pin文字会使来源拒绝，不能在未重新绑定时做文案清理。

## 精确新增合同

1. `choice_eligibility.rows[*].movement_result_reference`只用于`community_group_019:scene:1:choice:0`。有效时`annotation_role=selection_result`，仅这条原附注从unparsed移出；raw conditional、checks/status/原ID/上下文/资源预算保留。源无效时reference为unknown，原unparsed恢复。VISION无该字段，不借用MOVE条件；其余10条未解析附注不改。
2. 机制reference_kind为`documented_current_floor_resident_movement_exception`。`completion_exception_reference`明确one_way=true、condition_matches=null、converse=false、negation_implies_successful_movement_verified=false。actual完成/目标/移动/战斗/后态均null；source_scene_link_verified=false。此项不是原入口修复，25/57缺口不减。
3. 位置reference_kind为不同的`resident_location_reference`。binding包含epoch、zone_id、template_id、node_id、row、col、grid.rows/cols、type_evidence_role、map_historical及observed/remembered原类型。每次按完整typed当前图重新生成、精确比较。位置来自已读或记忆的精确`“居民”据点`类型；不取预测/模板/visited推完成或目标。
4. 新4个控件加label只提供独立位置和两关固定资料，默认None、不选第一个。`枯枝/败叶`只是既有目录固定关卡，不加入MOVE event_battle_links，不主张实际触发其中一关。源失效时隐藏、清空、禁用。
5. MapView新增`referenceNodeSelected`、`reference_binding`及本地UI origin。`select_node(...,emit_selected=False,reference_binding=...)`仅在新binding守卫路径使用；深复制完整binding。该origin不写本局/私人状态，不是资格、目的地、路线或实际完成证据。
6. App新增`map_reference_node_selected`逐次核最新graph/run id/historical与完整证据；新局同id、坐标/grid/类型证据/身份/history变更即失效并清UI选择，绝不绑替代节点。`set_map`和技术开关在有效参考意图下仍更新地图详情，保持原事件阅读。
7. `map_node_selected(...,update_catalog=True)`保留旧默认。普通地图点击/下拉选择清reference origin，仍发原nodeSelected并自动跟随原bound-dossier链；旧普通binding仍走原六字段守卫与默认选点。没有宽泛blockSignals/finally全局flag，也不假定排队信号可借瞬时flag保护。
8. 仅MainWindow将显式“查看地图所选节点”按钮原slot改接`show_selected_map_node_contents`：从最新MapView.graph/selected读取，过期/无选择直接拒绝，不fallback旧node_context。用户显式查看才替换阅读绑定；独立NodeCatalogPanel的原按钮语义不变。

## 静态可执行性与仍待实际验证

`WINDOW_EXECUTABILITY_STATIC_REVIEW.json`记录实际纯文件检查：32项候选路径存在；runtime manifest10成员均匹配；完整expected event/scene/choice与当前目录逐字typed匹配；窗口所列29个选定来源路径可由虚拟提升得到；GameCapture/DesktopBackend/MapView/App所用方法存在；PySide6/win32gui/win32process安装路径仅用PathFinder定位，**未import/未加载DLL**；两个既有固定作战网格/图片路径和SHA有效。

窗口在canonical脚本校验后才import Qt；四临时状态路径在构造MainWindow前替换，refresh_windows覆写为clear；八个外部入口在原函数执行前阻断并计数。初始/每阶段及event loop关闭后均检查零attempt；无自动采样启用语句。截图只使用该验收窗口`window.grab()`，不读取桌面或游戏窗口。失败回调close+exit1，成功保留至deadline后close；窗口关闭/Qt退出与来源前后相等必须实际满足。完整QApplication teardown仍由外层原验收监管处理，不把单窗口close冒充全进程清理。

最终窗口检查数/执行数/截图数/几何阶段数均从实际断言或记录计算，不预填passed/N。源guard为29项选定范围，并非整个App所有传递依赖；本批未重复执行已通过全量，不把选定范围等同完整源码冻结。

**仍未验证**：实际DLL导入、原生QPA/HWND、信号和选择状态、两关预览实际加载、三尺寸及高DPI布局、非零滚动/选区、120秒收尾。五个新增纵排widget在720高时可能挤压阅读区域；260×120只是未来验收操作阈值，不是已观察的通用可用性结论。失败应保留首实际源/日志并改进，不放宽断言或改称不可用。

新测试方法声明72（19源helper+29位置+19接入+5信号），历史290方法保留7；当前实际unittest/Qt/窗口执行均0。原v1/r2/首r3/r3b/d52/首静态工具错误均保留，不能把声明、AST或缓存测试代替正式产品通过。

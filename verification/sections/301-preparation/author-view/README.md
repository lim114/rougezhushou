# 301具名奖励图文窗口候选

只准备两个可提升文件：`rouge/named_reward_items_view.py` 与 `tests/test_named_reward_items_view_301.py`。生产父入口、旧界面、资料包、项目记录与Git由根代理负责，本目录不修改。

API：`NamedRewardItemsPanel.set_reference(event_id, *, scope_key=None)`；公开 `choice`、`reading_tabs`、`player_text`、`source_text`、`icon`、`packet`。默认不选；选完整选项立即fresh查图文，没有第二按钮。重复物品用流程/选项序号、选项标题区分，条件保留正文。

玩家页依次显示物品名与类别、对应选项、原选项条件、用途、完整物品说明、图鉴解锁说明、数量与实际未知。图鉴解锁不当本局选择门槛；不默认1件，不将用途中参数视为本局生效，也不改变计算藏品或本局状态。代码ID、完整原JSON和来源URL只在资料页。

每次刷新调用一次event_reference；选中时再调用一次item_details并比较整条reference，核item/icon身份。显示前从固定相对路径读取图片原字节并核SHA/bytes，再以同一字节创建QPixmap，避免核对路径后另读不同图像。后端全包13图任一失效即全部拒绝。任何源/详情/图像错误清两页与图像，恢复不重选。

阅读身份包含event、父scope、来源scope、完整scene/choice/reference。相同有效范围保留已选或未选的资料页、选区及真实非零滚动；父范围或来源范围变化清旧选择；源恢复仍手选。手动取消清物品图文但保留完整来源阅读入口。

隔离检查使用`run_direct_dialog_checks.py`复制后端公开manifest所有成员及本UI/test到临时ROOT，APPDATA/LOCALAPPDATA/TEMP/TMP均临时，QPA offscreen；只构造新QDialog，不构造MainWindow、不采样、不聊天、不读取私人配置。必要测试包含16完整选项/13真图片、12收藏品与1零件、重复物品的独立条件、图鉴解锁隔离、数量/actual未知、已选与未选阅读留存、scope变化、warm源/无关图失效和恢复、精确引用拒绝、单次查询数。此检查不是正式Windows或产品总验收；最终HANDOFF引用真实首跑原件，不预填通过数。

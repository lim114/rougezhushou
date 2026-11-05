# 维护：地图阅读状态统一归属并删除重复恢复

原先楼层readings保存节点/资料选择/滚动，entry_readings又按节点保存查询/资料选择/展开/滚动。show_floor在selected完成后再次选资料、设滚动和恢复展开，旧资料消失时仍会把旧滚动套到节点概况。

现在floor_selections只保存楼层最后选中的节点；entry_readings统一保存节点的阅读状态。show_floor只切节点并调用selected，selected在条目选择之后一次恢复展开与有效阅读位置。删除初始默认展开的重复设置及仅剩一个调用点的restore_entry_expansion包装。没有新增状态文件、外部框架或错误恢复，不改本局数据。

固定视口的修改前对照：切楼层概况阅读通过；一组展开3次、失效资料旧滚动17覆盖概况0的两项失败。改后通过；补测发现待确认节点单独返回时丢失概况滚动，已修正该路径再完整运行本批11项，全部通过。最初只固定高度的夹具、所有失败和中间轮次均留在.local/code-constraints-review-33，不改写成通过。

检查覆盖同节点刷新、折叠选择、跨节点查询、切楼层返回、待确认节点概况、资料失效、手动新局清UI状态和定位回调。没有全量检查。原测试窗口正常关闭后重开，工具条可见响应；这不是实机游戏验收。

原有node_sprite/open_hover_entry/remember_entry_reading/open_entry/check_reference方法AST以及selected异常处理AST未变。D87—D88只登记，player_map_reader代码未改。其主题入口有多个真实调用方，先区分重复主题应用与必要的主题切换后再整改；不能凭包装短就删除。

[进度](PROGRESS.md) · [统一待审清单](../../../../docs/reviews/pending-defenses.md)

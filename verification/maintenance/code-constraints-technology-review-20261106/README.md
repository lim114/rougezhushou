# 维护：科技资料与跳转刷新

technology、technology_view、technology_state全文回顾。内部只读标签/门槛不再深复制整表，公开返回数据仍独立复制，调用者不可修改缓存。重复名称计数读取复用。界面筛选值每次populate只读一次；show_technology通过Qt QSignalBlocker合并搜索/筛选清除，随后一次populate。该作用域用于正常批量编辑，不新增罕见异常恢复或try/catch。

26项定向通过（1.346秒）。57节点×普通/技术×有无临时档案共228条旧新文字一致；筛选跳转的选中项、57项列表和正文一致，populate末尾直接render调用2→1（不冒称全界面绘制次数）。_plain承担领域文本转换，_timestamp承担时间验证；界面方法是实际信号入口，不机械内联。

technology_view完整销项；另外两模块重复核验和存档保护D300—D303待审，未改私人状态。完整53、部分177、仅异常40、结构288，共558。待审266组。无全量，窗口更新并核对可见/响应，原始证据仅.local/code-constraints-review-137/。

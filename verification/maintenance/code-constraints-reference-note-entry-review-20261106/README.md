# 笔记资料入口整改

D98：expansion_reference.rows经_plain及未命名默认文字生成name，detail从rows返回；note_for删除重复非空文字保护，直接取必填name。

D99：菜单点击context已核验生成canonical content，直接进入原show_compact/open_saved_note，不再经open_note重复reference_target/note_for读取。独立open_note保留校验；菜单展开与后续点击各读一次；open_reference刷新/选择信号后的核对保留。这些不是同一时间点。

9项定向通过：点击只读一次、展开到点击来源丢失拒绝、独立入口拒绝、必填字段错误显露、现有资料身份与私人笔记保持检查。未跑全量，未改私人数据。新版测试窗口仍待用户退出旧助手后更新。

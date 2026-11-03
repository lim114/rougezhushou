# 永无安宁：卡德霍、痛楚化身与猎犬的资料接口

三个入口严格为普通关卡 `ro6_b_4` 的 `enemy_2145_cadejo@0`、`enemy_2146_cadesd@0`、`enemy_2137_shsdgo@0`。字符串身份与整数等级均严格核对；布尔值、浮点数、其它关卡及“痛苦将息”的同名/自定义敌人不借用本入口。

`rouge.boss_hunt_reference.hunt_reference(stage_id, enemy_id, level)` 对无关身份提前返回 `None`，不读取新增资料。有效结果包含 `source_valid=True`、`status='documented_reference'`、`reference` 和 `source_identity`。身份在结果及 reference 两层保留，`entry_name` 区分所选敌人，四个动态主题为 `condition_flow`、`cadejo`、`avatars`、`hound`。它们是阅读分组，不是四个必经阶段。

`reference_text(result, topic_id=None)` 再次核对完整当前结果后输出玩家总览或指定主题，拒绝沿用伪造或过期资料。玩家说明不用连写的无单位原卡标题数字；8张完整技能卡、3张能力卡、术语提示、标题DOM及来源差异保留在技术资料中。原文索引遗漏的 tooltip 清单已从完整原DOM重建，首个索引和修正记录均保留。

11项实际状态字段恒为未知；当前服务器核验、数值模型、地图、藏品、本局状态修改标志均为 false。资料中的首次击倒、关卡生成、退场及技能结束不是同一事件；20秒/10秒、原图鉴/社区修正版、存疑波次分别保留。“痛苦将息”存在独立技能覆写；两个自定义化身的完整原技能非空，不能从旧 definitions 为空推断没有技能或照搬基础数值。

每次确切目标查询重新核对 manifest/data 与12份公开运行期成员，比较当前两个完整选定关卡、五个完整技能定义及八个相关绑定；不缓存可被污染的解析包，返回独立副本。完整原数据库和两份原关卡只在构建时核对，不每次查询重读，也不在运行期依赖 `.cache`。来源失效时返回无 reference/source_identity 的结果，界面清除旧阅读、选择和三张图片；来源恢复不能自动重开旧内容。

构建器 `scripts/build_boss_hunt_reference_311.py` 支持 `--root`、`--output-root`、`--check` 和三个完整原件位置选项，详见 RUNTIME_README。构建原件缺失不代表重建通过；实际产品验收仅以 `verification/sections/311.json` 及其真实运行回执为准。

技术JSON显示前仅将U+00A0、U+2028、U+2029写成JSON转义，避免Qt纯文本读回规范化改变原义；中文保留可读，JSON解码后仍须逐字等于完整原对象。原始HTML/数据与来源摘要不为迎合显示而改写，首轮失败及修复前件另存于311验收准备记录。

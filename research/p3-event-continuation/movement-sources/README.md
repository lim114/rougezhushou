# 第258组候选：加工品获取清单与来源机会审查

状态：工作目录封存可迁移；仅新增文件，未修改生产入口、全局索引或提交。26 项必要验收（18 API / source / builder，8 Qt offscreen）通过。生产标准 tests.test_* 入口及既有真实入口由 ROOT 迁移后核验。

## 已完成能力

- 可勾选固定原目录 12 件 MOVE 加工品作为获取目标；持有布尔与件数分别显示，已持有不自动清掉目标。
- 完整审查 6 类独立渠道：诡意行商购买、秘境行商购买、秘境行商种子培育、险路尽头离层、险路小径离层、险路恶敌通关。源自 12 项原件身份、冻结 PRTS 原卡片来源标志及主文档入口原句，不通过名字、后缀或 prose 推入口 origin。
- 两商店保留 10 项一般文档范围、2 项明确禁售。逐项核对当前陈列三态，API 仅在明确完整陈列清单声明时把缺项判无。文档 10 个条目售价与原 module 中 12 个 sellPrice=1 的基础估价完全分开；默认不使用文档价比较预算，需明确无修正情形或独立报价，矛盾报价不覆盖，Qt 仍可修改纠正。
- 种子 7 项明确来源标志、5 项类别不符；小八界具名例外和中/高稀有度、1 个奖励的原句来自种子原卡片，归档完整原卡片 SHA。核对持有种子与培育完成声明，不预扣件数，不把黄色跨局模式限制推广到加工品。
- 尽头/首领来源标志明确 5 项，小径 5 项，其他 7 项各保留待证，不视为禁止。尽头/小径独立数量参考 1 件；首领原句未列数量，保持未知。数量不相加为领取总量。
- 独立目录模式列全 6 渠道；绑定声明图时按节点当前读取类型或明确原枚举定位，未知节点保留 6 类待证。秘境行商独立保留购买和培育两行；当前林间空地不复用旧行商作现入口。过去类型只列历史参考，不借用本次金币、库存、陈列或完成声明。
- 每行拥有稳定 review_key、原物品 ID 与声明图 node_id / row / col / zone_id / template_id / epoch。面板可发只读地图定位信号与事件目录信号，3 份三重身事件组分别保留；图类型变化、位置变化、epoch 变化不借旧输入。清单/来源选择、折叠、阅读光标/滚动在相同引用刷新时保留。

## 源证据与边界

重用 `research/p3-event-continuation/source-receipt.json`：原 JSON commit a550f5e048bb94e7cdefc6eb97a4091f0c4c7add、原完整文件 SHA、PRTS 主页面 revision 433770、零件原文 revision 434637 与稀有度模板 revision 432790。没有为已闭合事实重复 fetch。

`selected-original.json` 是原件截取，完整包含 scrapItemToType、MOVE12 items / moveScrapData、nodeTypeData；本组 receipt 校验截取 SHA。原 module 未序列化 acquisition flags。**bossdrop / pathdrop / seedreward / nosell 来自冻结 PRTS 原卡片，明确不是 game 原 flags。** 原 item ID / 名称 / 类型 / rarity / sellPrice 的对应关系才绑定到原 module/items。稀有度数值沿用既有逐一双向闭合的完整30项 PRTS 卡片/原表，未把颜色或低/中措辞当数值枚举。

四个 HTML 片段从冻结主页面按节点 UL 标题及其后平衡 DL 原字节截取（各仅698–1215 bytes），并校验 SHA；不是只抽标题，也不是整张宽表。渠道数据保存精确获取原句、版本链接与片段 SHA。Boss 根据卡片旗标的原句绑定，未伪造独立数量原文。

固定目录和 PRTS 文档条件覆盖不等于完整服务器池。实际池成员、服务器资格、当前陈列、真实报价、实际可达、掉率、领取与本局库存写入均保持 unknown/False。原件明确25 scene / 57 option 的 origin 缺口继续保留；3 份独立三重身文档入口不等于 origin 原场景链已证。

## 精确迁移清单

以下从 `work/p3-movement-sources/` 复制，由 ROOT 执行：

| 工作文件 | 生产目标 |
|---|---|
| movement_source_planning.py | rouge/movement_source_planning.py |
| movement_source_view.py | rouge/movement_source_view.py |
| data/movement-source-reference.json | rouge/data/movement-source-reference.json |
| build_movement_source_reference.py | scripts/build_movement_source_reference.py |
| test_movement_source_planning.py | tests/test_movement_source_planning.py |
| test_movement_source_view.py | tests/test_movement_source_view.py |
| selected-original.json | research/p3-event-continuation/movement-sources/selected-original.json |
| source-receipt.json | research/p3-event-continuation/movement-sources/source-receipt.json |
| battle_shop-source.html | research/p3-event-continuation/movement-sources/battle_shop-source.html |
| scrap_shop-source.html | research/p3-event-continuation/movement-sources/scrap_shop-source.html |
| final_exit-source.html | research/p3-event-continuation/movement-sources/final_exit-source.html |
| path_exit-source.html | research/p3-event-continuation/movement-sources/path_exit-source.html |
| README.md | research/p3-event-continuation/movement-sources/README.md |
| verification.json | research/p3-event-continuation/movement-sources/verification.json |
| acceptance.log | research/p3-event-continuation/movement-sources/acceptance.log |

不要迁移 work 数据目录中两个指向生产 duel/node-catalog 的符号链接、ordinary_battle-source.html（临时调查，不属于最终六渠道）或 __pycache__。来源产物迁移后可删该多余调查片段；不迁移旧 seed / exchange，因为已经由 ROOT 分别集成。

## 接口与真实入口接线建议

`movement_source(item_id, channel_id, context=None, declaration=None, historical=False)` 返回单项来源、条件三态与独立数量/价格参考；`source_review(target_item_ids, graph=None, context=None, declarations_by_node=None, epoch=None)` 返回目标×来源完整行。输入只读。引用绑定当前 duel reference/node catalogue SHA，一旦改变需要重建，不静默复用旧目录。

`MovementSourcePanel(parent)` 非模态：

- `set_reference(target_item_ids=None, graph=None, context=None, *, epoch=None)`：显式指定目标；None 保留原清单。首次可传 [] 让用户勾选12项，或从已选择原加工品传 [exact_id]。
- `set_map_context(graph=None, context=None, *, epoch=None)`：刷新声明图，保留获取目标及相同图内临时输入。context=None 时保留原上下文。
- `set_context(context=None)`：刷新库存/资源上下文，不清清单。
- `mapNodeSelected(str, object)`：仅发 node_id 与严格位置 binding，供既有地图只读定位复核。
- `catalogEventSelected(str)`：仅发目录事件 ID，供既有事件详情打开，不能视为选定当前实例。

ROOT 可在 NodeCatalog 现有 `function` 记录的 `node_type == 诡意行商 / 秘境行商`、现有 `event` 记录 node_types 包含 `险路尽头 / 险路小径`，或 BattlePanel 原节点/关卡为 `险路恶敌` 的来源参考入口接入。目录中的 `community_group_033` 是险路尽头；`community_group_034 / 035 / 036` 均标题三重身，但事件 ID 和 entry_scene_keys 独立，不合并、不虚构 function_nodes 出口。地图工具入口可将当前 graph 与 runtime context / epoch 传入本面板；不得把声明图输入提升为真实可达性。

## 验收入口

工作目录：

```sh
.venv/bin/python work/p3-movement-sources/build_movement_source_reference.py --root /workspace/rougezhushou --research /workspace/rougezhushou/work/p3-movement-sources --output work/p3-movement-sources/data/movement-source-reference.json
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s work/p3-movement-sources -p 'test_movement_source*.py' -v
```

标准生产（ROOT 迁移后）：

```sh
.venv/bin/python scripts/build_movement_source_reference.py
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.test_movement_source_planning tests.test_movement_source_view -v
```

当前首轮 API18/18，Qt 首轮8/8；收窄主文档片段、增加原件截取 SHA 与入口原句后，全26/26通过（0.413s）。无失败运行；Qt offscreen propagateSizeHints 提示不影响验收。

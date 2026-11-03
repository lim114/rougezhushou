# 第301节候选研究：从精确节点选项手动阅读具名奖励图文

本文件仅为研究与接口建议，尚未建立301功能scope、实现、产品测试或原生验收。

## 已核实事实与错误前提修正

- `node-reward-reference.json.event_rewards`有17条原始typed奖励记录，但只有16条能由现有`node_catalog.event_reward_options`返回到完整社区选项；它们覆盖10个事件、13种物品。17不是17物品，也不是17个已经恢复的服务器入口。
- 未绑定的是`choice_ro6_rest_4`（金色凝滞“查看无人机”→高级物资配给券）。其原表说明存在，但当前目录没有对应奖励关联，不能为了覆盖17把它补成入口。本提案排除它，原始17总数保持。
- 已绑定16条涉及12种收藏品和1种零件。13件都有固定完整`items`对象，其中12件也有完整`relics`对象；笼控器为SCRAP，不能改称收藏品或套藏品数值。13件原表`usage`与`description`均非空（未绑定的配给券description为空，另属不同边界）。
- 12件收藏品的实际PNG均已存在，完整原item.iconId与固定资源回执文件名相同，实际SHA256及Git blob SHA1逐一匹配。笼控器没有既有下载图，但固定资源commit→rogueitem目录tree→唯一blob链完整；已单次定向HTTP200取得30240字节PNG，SHA256 `bc20db6ea6baf773ad5c1d34dafec6dfa75744c95b80c788f3fca347827c57f8`、Git blob `6e800c66f45d26c763c3d5aa65b95a054f0e4bc1`均匹配原tree。没有按相似图/同图名称推断。
- 295沙盘α（`rogue_6_relic_final_1`）和297怦然信标（`rogue_6_relic_final_3`）都不在这17条typed记录里。本组13件/16选项与它们不重复，原入口继续保留。

## 精确范围（完整key在inventory中逐条保存）

| 事件与目录ID | 选项范围 | 新增可阅读物品 |
| --- | --- | --- |
| 血衣之下 / group005 | scene0 choice0/1/2 | 他缚、“剑锤”、一串钱伥 |
| 擒与缚 / group006 | scene0 choice0/1 | 翱翼、虬蜕 |
| 沉寂之屋 / group007 | scene0 choice0/1 | 笼控器；两条条件与同物品分开保留 |
| 黑诞 / group008 | scene0 choice0 | 猎印 |
| 被歌颂的影子 / group010 | scene17 choice0 | 犬植浆 |
| 愈创之心 / group011 | scene0 choice0/1/2 | 追忆；三条不同条件不得按同名合并 |
| 和平守卫者 / group019 | scene0 choice0 | 厄运火杆 |
| 独活 / group020 | scene0 choice0 | 同行者 |
| 泪之聚落 / group022 | scene0 choice0 | 击坠“神明” |
| 回滚文明 / group025 | scene9 choice0 | 焚毁“文明” |

## 当前用户界面缺口及查重结论

`rouge/player_node_information.py:256`起按精确choice显示“具名奖励：名称；数量未确认；实际领取未知”，不带物品图片或完整用途/说明。`rouge/node_catalog_view.py:227`起技术正文也只附具名奖励名；`NodeCatalogPanel`没有从这16条reward choice到图文阅读器的通用按钮或信号。

现有`documented_item_button/open_documented_items`只针对295的`community_group_021`；297的`expedition_button`只针对024。它们均不覆盖上表10个事件。主计算页`rouge/app.py:870–880`虽有独立藏品列表及用途tooltip，但列表用于勾选算例，不保存节点scene/choice/reward身份，也无该选项到完整图片/故事说明的跳转；因此不能将独立查表误称节点奖励图文已交付。

这组功能的实际价值是玩家从正在阅读的事件进入精确物品详情，不必跨页面手搜或误勾成计算状态；它是阅读能力，不是新增掉落机制或奖励池。

## 建议的最小接缝（供根确定正式接口）

1. 独立只读`named_reward_items` API，以原38目录与原17typed完全不变为约束。`event_reference(event_id)`只对上表10事件返回完整选项行；`item_details(event_id, scene_key, choice_key)`只接受本组16个三元组，且必须仍唯一对应同一个原choice ID与item ID，不能按标题或列表首项挑。当前每个三元组唯一；若未来变成多条应明确未知而非默认。
2. 每行保留完整社区choice、原游戏choice、完整原typed奖励、完整item以及适用时的完整relic；quantity/eligibility/条件沿原参考，不把文献的条件列表变成当前本局可选结论。`game_choice_ids`原空列表保持，尤其沉寂之屋289两文献链接不能变成脚本入口已恢复。
3. 将本组完整选中对象/目录/17typed/图标等做精选来源包，完整游戏表从已公开300固定源重建，避免逐次读17.9MB。每适用query fresh精选权威字节、完整当前目标事件与既有奖励实际对象typed核对，再校验内部缓存摘要、返回deepcopy；来源失效清空旧图文。图标精确绑定固定资源commit+item.iconId+PNG SHA/blob，而非只文件存在。
4. `NodeCatalogPanel`增加独立手动“查看具名奖励说明”入口，不借292作战筛选器，不自动采用其当前首选项。新modeless读者默认选项-1，手选完整choice后再手动打开图片/用途/完整说明/原解锁文字；保留同scope choice/tab/cursor/非零scroll，跨scope或sourcefail清旧图，恢复后不自动选回。
5. 不改`node_catalog.py`、`node_rewards.py`或原`event_reward_options`返回；不必向295/297塞新物品或改它们特殊文案。295 formatter有“部署费用变化不是源石锭”等α专属说明，不能不加区分地复用到所有13件。玩家页按收藏品/零件分组说明，完整原始标识与来源放依据页。

## 最小验收范围与风险

- 16完整tuple→13物品逐条完整原对象和精确图标核对，覆盖所有10事件而不是只挑一个示例；重复物品的两条/三条选项条件与完整身份分别保留。
- 原17typed、38事件、190资源、37或全部非目标player文案逐值对照保持；295/297入口不变。配给券不在新的入口里。数量、完整掉落池、当前服务器资格、实际领取与持有始终未知，不写Run、不自动勾计算用藏品。
- 真实UI检查至少含多物品事件、同物品不同条件、SCRAP笼控器、scene17犬植浆/scene9焚毁文明、同scope刷新、来源失效/恢复及非目标切换。所有正式计数必须来自实际回执，本研究查询/下载不算验收。
- 原item用途可能带战斗触发/阶段规则（厄运火杆、追忆等），只显示原文，不能据此新增数值计算或路线/事件排除。`unlockCondDesc`是图鉴说明，不自动等价于当前选项门槛。
- 采用固定game commit与资源commit，未证明当前国服完全相同；不减少15/25/57/10、完整地图81/59等既有缺口。

## 研究原件与限制

`named-reward-inventory.json`保存17条完整奖励/原choice/item/relic、全部38当前reward query、16精确绑定与各PNG实际字节校验；`exact-scrap-icon-first/`保留唯一HTTP请求/原PNG。首次inventory里297排除项的item ID曾写成待核占位`cargo_1`，后已读取实际模块常量核为`final_3`；原稿保留在`initial-inventory-before-identity-verification/`，此占位未用于任何新奖励绑定。

本研究只读公开数据与源码、调用无状态公开资料查询并下载1个固定原图标；未改生产/文档、Git、Qt、游戏、聊天或私人状态；未建立301完成声明。

# 零件交换完整文档池

本组是在首组狭路相逢的独立完整功能之外，实现失与得的零件提供物与结果候选比较。全文档覆盖30原零件，每种档次的明确结果池均9项。高档可得一次性喷气背包及3涂装概念体，保留这些物品的原中档；种子、枯苔藓球、笼控器不可作为文档结果。前提内可得到同件，不预扣、不返还、不自动更新本局。

声带允许交换零件；手掌允许第2次，第2次的首次类型门指SCRAP/RELIC，不是MOVE/GOODS/PASSIVE。声明件数与布尔持有分别保留，False持有可排除，但True不编造件数；自然入口第I/VI层规则不推广到强制内容/秘境。1件数量来自固定427904两个“接过零件”场景的独立原文，入口链仍未证。434637完整交换规则另列，完整文档池不是完整服务器池。

10项首轮Qt/模型检查全部通过，记录first-tests.txt。暂存于work以免污染首组原子提交。无需新网络请求，首组冻结的原模块与raw参数复用；完整规则及主页面失与得行保存在本目录。

产品转移：

- scrap_exchange_planning.py → rouge/scrap_exchange_planning.py
- scrap_exchange_view.py → rouge/scrap_exchange_view.py
- build_scrap_exchange_reference.py → scripts/build_scrap_exchange_reference.py
- test_scrap_exchange_planning.py → tests/test_scrap_exchange_planning.py
- exchange-node-fragment.html、exchange-rules.wiki、first-tests.txt、README.md → research/p3-event-continuation/exchange/
- data/scrap-exchange-reference.json → rouge/data/scrap-exchange-reference.json。data的另外一个文件是只读symlink，应留在scratch。

转移后 `scripts/build_scrap_exchange_reference.py` 的ROOT会自动指向仓库；`build()`和已交付JSON需全等。必要检查：`QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest tests.test_scrap_exchange_planning -v`。

接口 `exchange_candidates(offered_item_id, context=None, exchange_index=1, vocal_cords_unlocked=None, palm_unlocked=None, first_exchange_item_type=None, owned_quantity=None)`；`ScrapExchangePanel.set_reference(offered_item_id=None, context=None)`、`set_context(context)`。root可在失与得功能节点、回滚文明事件及零件目录挂入口；本组没有改既有UI或全局索引，没有提交或推送。

实际按钮、随机陈列数、消耗及服务器资格未知。临时offscreen验证不冒充原Windows、游戏或聊天验证。

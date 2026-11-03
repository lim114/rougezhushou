# 移动恶笼草：固定文档435751的条件数量参考

本包仅补 `enemy_2152_shezlc`（移动敌人）的文档条件参考，不证明本局实际等级、实际出现、击倒、抵达终点或服务器结算。级别0、1、2各自独立段落都注明战后击倒额外10源石锭、抵达路径终点扣10源石锭。不能把“箱型恶笼草”装置与其移动敌人重复计奖。

`moving-mobile-response.html` 是本次 `https://m.prts.wiki/w/恶笼草` HTTP200返回的完整原始UTF-8响应体，106062字节，SHA256 `ac67db472d7cbfe9caef105b9ab17eb4fda43f0b09a8a229e61eeca8392c2430`，不是搜索摘要或手录HTML。文内 `wgCurRevisionId`、`wgRevisionId` 和固定链接均指435751。页面最后编辑于2026-10-05；抓取发生于2026-10-16本机时间。`mobile-response-receipt.json` 原样保存该次请求的状态、字节数、SHA及Content-Type；没有声称保存HTTP全部原始头。

根代理独立的直接网页读取原回传保存在 `root-independent-web-open-actual.json`（JSON字符串）。它不是HTML字节，也不是服务器实测，但与本响应体的三个级别条件相符。`scripts/build_moving_reward_current_reference.py` 使用HTMLParser的真实h2分块，避开目录与JavaScript字符串；`extraction.json` 保存每一块的源字节区间/SHA和各自条件。可离线重复核对：

```
.venv\Scripts\python.exe -X utf8 scripts/build_moving_reward_current_reference.py --html research/p3-moving-reward-current/moving-mobile-response.html --output research/p3-moving-reward-current/extraction.json --check
```

旧版428232数量边界和旧数据未改，仍保存在既有 `research/p3-battle-rewards` 与 `rouge/data/battle-reward-reference.json`。本包是独立current overlay。先前desktop/fixed/raw HTTP403及隔离headless固定页连接关闭的原回执、stderr也分别保留；headless进程退出0但DOM为空且无PDF，所以没有计为取证成功。仅复制这些公开抓取回执，不复制新建浏览器profile或任何私人状态。

运行时仅当每条固定引用都精确对应上述实体、`useDb is True`、`level`是0/1/2中的原生整数、且显式 `overwrittenData is None`，才给条件数量。缺字段、bool/float等级、override、任一坏引用或来源失效均整组未知，不静默丢掉坏项。多个合法级别的数量相同可以显示条件共识，不能据此确认实际等级或把多个引用相加为总奖励。数组、路线或动态生成的额外变体仍不能由此穷尽。

PRTS为玩家共同编写的资料，非官方服务器脚本。PRTS其他内容依其页面知识共享署名-非商业性使用-相同方式共享许可；游戏名称、文本等权利属于鹰角及关联权利人。文档链接：`https://prts.wiki/index.php?title=恶笼草&oldid=435751`。整个HTML仅用于本项目可审计来源保存；未把网页脚本执行为游戏机制，也未证明其余奖励池。

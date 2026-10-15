# 沉寂之屋两项具名零件的文档内容关联

这是固定资料补充，不能当作当前服务器执行、实际选项可用、奖励数量或领取证明。

已有原奖励表早已包含两项笼控器及其SCRAP类型；本包只核对社区目录两条未关联选项和这些已有奖励的内容联系。保留原目录的game_choice_ids为空和source-scene关系未证，未恢复25场景/57选项的原生入口。

- BWiki原HTTP页：`https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录`，2026-10-15已取得的完整HTML，修订349818；可见内容日期2026-07-27。`bwiki-investigation.html`原字节来自既有研究，未重新联网。沉寂之屋表的两项完整标题和结果，只去原游戏富文本后与原choices逐字相符；入口全文也相符。
- PRTS旧目录原HTTP页：`https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid=427904`，`prts-events-427904.html`保留已封原字节。两项custom描述明确增加“零件”和括号内用途。不能用全局删词或删括号制造全文匹配；本包分别保存原词。
- 固定原游戏表：Kengxxiao/ArknightsGameData，commit a550f5e048bb94e7cdefc6eb97a4091f0c4c7add，完整源17943244字节，SHA256 f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86。`extract_original_records.py`只读已有完整下载并核对完整SHA，产出`original-records.json`中两choices、入口场景、item原对象；运行时不需要完整17MB表。

原displayData.itemId直接为rogue_6_scrap_G_12，items给出笼控器/SCRAP。费用分别为2目标生命值和8源石锭，归属不同选项，不合并为入场费。数量未序列化，不补1。预算与资格独立；不据此更新背包、资源或后续事件。

构建器`build_event_named_reward_links_289.py`只读取本包已归档HTML、选定原记录和固定既有目录/奖励表，生成新的补充数据/提取回执/清单；不改旧目录及其sourceSHA。运行时先fresh核对全部清单字节，原件更改或缺失即拒绝该补充，不使用先前解析缓存掩盖变化。

BWiki页面的社区文字按其页面许可与署名要求使用，PRTS社区文字保留来源；原游戏文本与数据权利属于鹰角及关联权利人。获取网页不产生额外授权。本包仅保存必要取证原件，不复制社区脚本实现。

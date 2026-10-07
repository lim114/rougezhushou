# P2第26–30节候选：机械师持续参数与长期科技资料

只读审计，未修改仓库文件。固定提交a550f5e048bb94e7cdefc6eb97a4091f0c4c7add。source-receipt.json重新核对4份原件字节与SHA-256；mechanist-reproductions.json保存6个公共计算/共享token API场景；technology-source.json保存完整精确选择器；technology-reproduction.json保存目录缺口与边引用完整性。这些是审计复现，不是新增产品回归，也不是当前热更新/原生Windows验证。

## 候选26：结构性原理持续参数的独立资料参考

精确来源：character_table.token_10069_mcnist_mcgraf.talents[0]，PHASE_1/PHASE_2分别skill@duration=20/30。battle_equip_table.uniequip_002_mcnist.phases[1].parts[3]、phases[2].parts[2]均为isToken=true、TALENT_DATA_ONLY、talentIndex=0、validInMapTag=rogue_6，skill@duration=-1且upgradeDescription=持续时间无限。uniequip_table.equipDict.uniequip_002_mcnist及候选unlockCondition明确精二60级。

现状：召唤与天赋说明已有30秒/模组无限的文字，不应宣称它完全缺失。共享token_attributes只给培养属性，module_reference仅支持深海色；机械师六种场景均没有结构化生命周期参数或适用条件字段。正常未装备/模组未解锁下、二/三阶模组的不同持续参数不能供独立调用者核对。可新增专门的duration/reference资料，不扩展攻击时钟。避免把深海色的hp_pct/stock/concurrent schema硬套到机械师。

可改边界：只对精确mechanist/token/module对建立基础20/30秒与主题6二/三阶无限参数参考，明确“持续参数”及“实际部署时间未知”。精零尚未解锁召唤物不能显示有效基础生命周期；精二59级不套模组；一阶无无限；其它地图不能套rogue_6条件。在当前项目主题6固定范围展示时仍保留来源的适用主题。无限用明确状态而不是负数秒，实际死亡/撤退/技能更换不是无限保证。

不确定：实际部署完成、技能同步/继承、冲锋碰撞、屏障首跳/刷新/受伤计时及当前热更新。原表参数不能改变当前完整输出/周期或使未知冲锋变可算。三阶屏障每秒4%/最大20%有描述与参数，但把它也做时钟计算需要新绑定。

验证建议：精一/精二20/30，精零未解锁；模组1/2/3、59/60级门槛、相同培养其它token和地图不泄漏；来源哈希/选择器存在；所有技能/rank只改变资料不改变数值输出；输入及缓存隔离；已有模组天赋文字保留，报告只新增简明参考。

## 候选27：主题6长期科技的本地资料目录与前置门槛

精确来源：roguelike_topic_table.customizeData.rogue_6.commonDevelopment，包括developments(57节点：33 NORMAL、21 KEY、3 DIFFICULTY)、developmentsTokens(9)、developmentRawTextGroup(6)和developmentsDifficultyNodeInfos(3)。节点rawDesc/buffDisplayInfo给显示资料，frontNodeId/nextNodeId给关系，所有边均指向本57节点之一。难度门槛enableGrade=3/6/9及enableDesc原文明确。

现状：rouge/data/run-config.json无科技资料；run_config/prepare_run只接分队和难度。读取目录可得骨架初始护盾+1、毛皮我方防御+4%、信息素可部署人数+1等资料，当前产品无查询/展示接口。可完成目录、根据ID查资料、前后节点与原始门槛的说明，作为剩余“长期科技/效果逐项核验”的独立资料范围。

可改边界：将原表显示资料/ID与可验证前后关系持久化为项目公开数据，给简单资料入口与可读查询（适用当前主题6，参数/来源进技术资料）。难度节点门槛按原文展示；不得用前置树位置推导所有后继节点的当前实际生效规则，frontNodeId列表只证明显示边，不能推导AND/OR解锁条件；也不要累计展示数字并当成已应用效果。明确账户解锁状态未知。不修改本局私人状态，不新增OCR范围。

不确定：当前账号解锁、实际buff脚本/属性合成层、普通/其它模式激活/持久/重置。outerbuff-query记录的tech_buff_table 10条tree_branch ID与本57节点无交集；旧roguelike_table.outBuffs属于刻俄柏；buff_table404已知，不再重复。恢复计算必须获得明确绑定rogue_6_outbuff ID的配置/脚本与当前解锁观察。目录完成不能销长期科技全部计算待办。

验证建议：57节点、3门槛、明确ID唯一；无悬空边；同名节点按ID保留（颊囊等重复不能并为一个）；KEY原文保留；节点信息的复制隔离/未知ID；科技目录不改变calculate_damage输出或写入run state；Linux/Wine实际简单测试窗口可浏览/响应，原生Windows另列。

## 持续边界

这两个候选各自是一节，目录与界面不拆为重复节。22–25已有独立方案不重复；瞬发/多段时钟另在/tmp/p2-audit/instant-window-026-030。它们不足以证明P2全部完成，未知机制仍留在待办。

# 固定主队列的同组候选与关联包

本包用于普通战斗预览中的中文手动阅读。既有第163节已经提供原键分组查询；本组不声称发现新的随机机制。选择本关全部资料或当前出怪条目的关联资料后，玩家可以分别查看具体敌人、空动作、预置装置，以及符合条件的固定出怪资料入口。

来源固定为ArknightsGameData `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。69个关卡引用38份完整原level：主队列285组、215包。原文SHA、完整原level与转换后完整battle-previews同时绑定；普通/紧急、波/片段和同名动作分别保留。五个预置实体的中文名来自同版本character_table的完整选定记录，原表SHA及原URL保留；运行时不读取完整角色表或本局状态。

`randomSpawnGroupKey`只在同一完整主动作队列内按原键分组。`randomSpawnGroupPackKey`单独列关系，包含未写group键的成员。没有据此补选中次数、唯一/互斥或同时出现证明；不提供概率，也不把候选数量或包数量相加为敌人总数。条件分支不借同名键、routeIndex或主路线。

SPAWN保持全部同ID关卡等级引用；只有唯一等级且基础主路线有可用名义起格，才提供手动查看固定格图/敌人资料的入口。它不是实际入场位置或当前敌人存在证明。ACTIVATE_PREDEFINED只按完整原件alias唯一匹配预置对象；不按routeIndex定位。空key的激活动作是未指定目标，不能当作EMPTY空动作。EMPTY只表示该固定动作不生成敌人，不能推断整关或整段没有敌人。

每次query重新核对manifest、全battle-previews、数据/名称/说明及当前关卡完整level字节；既有battle_data缓存的source与完整选中stage还须严格匹配独立解析值。解析快照仅内部缓存，每次返回只复制本次资料。来源失效清除旧资料，token须再次fresh resolve；不会生成真实目标或选择游戏选项。

重放：`python scripts/build_spawn_candidates_299.py`默认只读比对，不写文件；初次采集可显式`--primary-root <同版本公开game-data缓存根> --write`，生成后仍需正式产品必要与原生验收。source build、缓存API检查与产品实际验收分别记录，不能互相冒称。未知当前服务器、实际启用/选择/生成数、回调、全局时钟、实际路径和本局奖励均不新增推断。

# 首领形态与转换只读接口

`TARGET = ('ro6_b_6', 'enemy_2150_shchmr', 0)`，引用等级仅接受严格整数0；False、0.0、其它关卡／敌人／等级均返回None，且不会开启新增来源读取。

`phase_reference(stage_id, enemy_id, level)`：精确目标有效时返回`source_valid=True/status='documented_reference'`，`reference`保留完整原研究对象，并提供顶层`stage_id/enemy_id/level/boss_name`。`reference.phases`保留原`phase_id`且增加同值`id`。六个名称条目为first/calamity_1/second/calamity_2/third/flying；这不是六条血。`skills[].documented_modes`改用完整原文标题抽取并与独立复核逐值核对；原空数组保存在`original_documented_modes`，原研究文件不改。六张技能卡、七条转换、完整共同能力及四条不能直接对算的差异仍完整保留。

有效`source_identity`恰为`{manifest_sha256,data_sha256}`。精确目标来源失效时返回`source_valid=False/status='source_unavailable'/reference=None/source_identity=None`；不回旧条目。没有返回实际当前形态、定时、目标或阶段属性。`ACTUAL_FIELDS`全None；current_server_verified/numerical_phase_model_added/run_state_updated/inventory_updated/modifiers_changed/maps_changed全False。

`reference_text(result, phase_id=None)`为纯中文资料格式化，总览列全部有源形态／招式／进入离开与循环；指定有效字符串id只列对应招式与相关进出边，仍列共同能力／限制。无效id不回退其它形态。原DOM／原字段保留在reference供独立技术页查看；普通正文不映射未知Fire／Fireball记录到形态。主目标退场只说明技能中断，不当成转阶段。循环不重生及延长灾厄留存的文字明确标为“文献说明注”。

## 来源分层

`ROOT`为项目根；`DATA='rouge/data/boss-phase-reference.json'`；`MANIFEST='research/p3-boss-phase-309/source-manifest.json'`。manifest硬SHA固定，data硬SHA固定；每次目标查询新读全部8个runtime_files，逐完整文件SHA和长度核对；文件与父目录不得为符号链接。不存在可变解析缓存；返回值为独立深拷贝。

runtime文件：DATA、selected-original-records.json、player-reading-data-candidate.json、boss-complete.html、stage-complete.html、http-source-records.json、final-review/seven-complete-visible-cards.json、final-review/source-review.json。相对路径均在同PACK（DATA除外）。一份失效即全包来源不可核对。

随后对当前`battle_preview.battle_data()`的完整target stage／完整enemy／全局source，以及`enemy_skills.skill_data()`的完整该敌人技能定义／该关卡绑定／source做严格类型及完整对象比较。其它无关关卡变化不使本资料失效。不会每query重读9.9MB battle catalogue、15MB敌人库或完整level；不得声称每query全库fresh。

构建时真实核完整原敌人数据库、完整原level、完整battle-previews、完整enemy-skill-references与selected对象。原大型文件复用已有固定原件，不重复新增15MB文件。云端离线重建可由`--enemy-database`显式提供同SHA完整原件；不自动联网或以片段替代。

`scripts/build_boss_phase_reference_309.py --root <repo> [--output-root <dir>]`默认生成data／manifest／模块及来源构建回执；`--check`在临时目录重建并比较生成字节，当前文件不写。完整HTML本体与七卡DOM逐对象核对，不把正则摘片当完整来源；正则只在已经固定完整标题中读取模式标签和检查页面修订号。

源原HANDOFF b2c2318f...始终不改。首次代理来源构建和第一次窗口/必要检查原件分别保留在verification/sections/309-preparation/candidate-first-source-build、309-necessary-attempt1和309-native-attempt1；它们不是最终当前源码的运行回执。

根代理随后按静态核对取消未知原技能的全局名称映射，并在飞行招式下直接展开已有文献明确交叉引用的未熄之地效果，保留其完整条件；不合并冷却/技力或新增数值。当前build-receipt.json来自根代理实际重新构建，过程在verification/sections/309-preparation/flight-inline-refinement/source-rebuild/process.json；原DATA及全部原文不变。第二次source --check、83项必要检查与27项原生唯一检查均实际退出0，回执在309-source-attempt2、309-necessary-attempt2、309-native-attempt2。资料范围和未决机制以verification/sections/309.json为准，不据测试通过推定游戏实际阶段。

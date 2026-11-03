# 洛伦茨与源阶方：交替激活及模块资料接口

`rouge.boss_cycle_reference.TARGETS`严格为`('ro6_b_5','enemy_2147_shophm',0)`和`('ro6_b_5','enemy_2148_shorbb',0)`。关卡、敌人必须为字符串，等级必须为严格整数0；False、0.0、其它身份均不是入口，并返回None且不开启新增来源读取。源阶粒素仅是相关原敌人；源阶方模块是关卡装置，不是第三个敌人入口。

`cycle_reference(stage_id,enemy_id,level)`有效时返回`source_valid=True/status='documented_reference'`，`reference`含精确`stage_id/enemy_id/level/entry_name`、动态`topics`及完整有源说明。四个阅读主题为flow／lorentz／cube／module，不是形态数量。`source_identity`为`{manifest_sha256,data_sha256}`。精确目标来源失效时返回`source_valid=False/status='source_unavailable'/reference=None/source_identity=None`，不沿用旧说明。

`reference_text(result,topic_id=None)`给出普通中文总览或指定主题的条件说明；无效主题不会代选其它条目。完整技能／能力原文、DOM、关卡预设和来源身份保留供技术页查阅。文献流程不认作本局事件序列；两个主体按各自条件与技能结束分别切换，不生成同步时刻。未列模式标签的技能显示为文献未限定模式，不能从空标签推断无技能或任意模式均生效。

`ACTUAL_FIELDS`：actual_lorentz_mode、actual_cube_mode、actual_modules、actual_half_hp_gate、actual_skill、actual_transition、actual_elapsed_time、actual_target、actual_route、phase_stats、actual_damage均为None。current_server_verified、numerical_phase_model_added、run_state_updated、inventory_updated、modifiers_changed、maps_changed均为False。

## 固定来源与失效

`ROOT`为项目根；`DATA='rouge/data/boss-cycle-reference.json'`；`MANIFEST='research/p3-boss-cycle-310/source-manifest.json'`。manifest与data均硬固定SHA；每次精确目标查询重新核对manifest.runtime_files列出的全部新公开源文件的完整SHA及长度，源文件或父目录的链接不准入。完整文献随包固定，运行期不联网。

运行期对selected-original-records中完整target关卡及三个相关敌人的完整技能定义／关卡绑定，与当前battle_data／skill_data对象做严格类型和完整对象核对。任何目标对象污染均使来源不可核对；无关关卡变化不借此改写本资料。查询不缓存可变解析包，公开返回为深拷贝。

构建期独立核对完整原数据库、完整level、battle-previews及enemy-skill-references与精选完整对象；运行只核新小原件及当前target对象，不宣称每次查询重读全部数据库／level／battle catalogue。大型原件复用已有固定副本；缺失时构建器可显式接受同SHA的原数据库与原level，不能以片段替代。

`scripts/build_boss_cycle_reference_310.py --root <repo> [--output-root <dir>]`重建数据、manifest和模块；`--check`在临时目录重建并逐字节比对生成物，不写当前生成物。完整HTML与完整卡／表对象在构建期核对，标题模式和正文角色分别保留。

模块资料中的基准属性、技力需求不等于本局预测面板或实际秒数；“首次低于50%”是有历史条件的文献触发，不能只看当前血量反推；扣30目标生命不等于所有对局必败；不从原预设声明推实际组数或位置。正式验收范围及实际结果查看`verification/sections/310.json`的真实文件；没有该回执时不能从资料构建记录推断产品验收。

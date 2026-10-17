# 命运所指来源合同

selected-authority-records.json保留实际提取原字节187ded...，含完整2event/6scene/5community choice/6primary choice。
完整11FEATURE+双沙盘+bubble03的14items/relics、两版完整DOM、唯一end2完整全文块保留。
choice-rule-map.json schema=curiosity_node_choice_rule_map_v1，字段固定：
choices[{event_id,scene_key,choice_key,reference_id,choice_title,choice_description,condition_text,
original_choice_ids,documented_rules[{rule_id,title,text,source_refs}],related_stage_reference}]。
related_stage_reference仅stage_id/title/reference_only/immediate_transition四字段；后者始终null，仅转换和已有决战两行有值。
node_context_reference={title,texts,source_refs,documented_main_floor:5,actual_node_ids:null}是独立背景，不放进每个选项结果。
其余顶层source/source_reference/notice/unknowns完整保留。actual_*由后端统一null，source_valid只固定资料。

031 scene0 choice0原候选end2_1带end_2_change，end2_4的itemId为空，不能合并或选择当前实例。
原正文同段同时含3节点与双沙盘标记，引用同一完整段，不篡改拆段；不同row仍只显示自己的结果。
1件收藏品具体池未知；50源石锭只该选项费用，不借给其它行。已存在的资格/战斗/资源接口不重做。
所有FEATURE参数只作旁证；limit/count/not_hold不证明实际执行/消费/次数/附着。bubble03名字取独立文献。

全17MB和完整HTML复用300/301公开源，只供重建。后端builder另生成DATA和最终source-manifest，不覆盖本包原件。
runtime只fresh精选完整对象、DATA及当前完整目标catalog，warm缓存完整性/typed JSON/深拷贝必需。

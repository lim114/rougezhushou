# 280固定缓存合同v1：费用舍入共识

原型`skill_cost_rounding_consensus.py`；公开API=`skill_cost_rounding_consensus(payload)`,`single_cost_consensus_reference(operation,cost,modifier_bits)`,`source_data()`,`public_example()`。无公共data/source覆盖，无RC选择输入；278 exact-only原接口和文件不改。公共包拟`research/p2-cost-rounding-consensus-280`，query拟`sp-cost-consensus`。

顶层exact keys：`receiver_exists`tri、`actions`1–50。action exact keys：`id,kind,ordinary_native_path,modifier_read,cost_decode,conversion_normally,operation_normally,round_normally`。kind仅rune_add/rune_mul/relic_mul；action/read ID全局唯一非空public label<=120字符。tri严格true/false/null，不接受整数0/1。

modifier_read SingleRead exact keys=`id,normal,bits`(unsigned32/null)；cost_decode IntRead=`id,normal,value`(signed32/null)，bool/float拒绝。各kind只表示已经进入该源的数字前缀，省略owner/BB存在性/lookup found、encoder和store；它们没有自动通过。ordinary资格和两operand读正常性均独立。新API没有从上一action向下一action传播decoded值。

固定stages=`modifier_read,cost_decode,int32_to_single,single_operation,round`，每stage exact keys=`name,called,normal,reference`。read/操作正常性unknown→未来called:null；已证failed→未来false。输入值未知或不在数字安全域不等于没有调用：若相应normal事实明确，可保留unknown数值的正常prefix；没有选择RC或虚构数值。round normal=true不是编码/写入/实际费用变化证明。

Result top exact keys=`kind,source,payload,rows,actual_cost_after,actual_sp_after,complete_cycle`，kind=skill_cost_rounding_consensus；后三恒null。source=`valid,status,proof_sha256,method_count,byte_span_count`。

每row exact keys=`id,kind,called,normal,status,stages,consensus_reference,encoder_argument_reference,actual_cost_after,actual_sp_after,complete_cycle`。encoder_argument_reference只有数字prefix所有normal=true且16候选共识时为Int32；它是若独立后续链继续时的条件参数，不声明encoder/store已调用。

scalar operation仅add/mul，cost signed32/null，modifier_bits unsigned32/null；返回dict，source失效返回null。dict exact keys：

`operation,cost_int32,modifier_bits,status,rc_pair_scope,cost_conversion_candidates,cases,possible_operation_bits,integer_candidates,same_rc_integer_candidates,int32_to_single_exact,all_operations_exact,integer_consensus_reference,expanded_beyond_exact_only`。

- rc_pair_scope固定`all16_independent_RC_pairs_conservative_superset`；不是实际游戏RC或切换记录。
- cost_conversion_candidates恰4项(已知有效cost时)，每项exact keys=`rc,cost_single_bits,exact`。rc0/1/2/3对应RN-even/RD/RU/RZ。cost0转换canonical +0 bits0；此Integer转换不会凭空生成负zero。
- cases恰16项(已知cost+finite normal/zero modifier时)，固定conversion rc外层、operation rc内层。exact keys=`conversion_rc,operation_rc,cost_single_bits,operation_exact,mathematical_numerator,mathematical_denominator,result_bits_candidates,status,rounded_int32_reference`。精确数学ratio基于**该转换后的Single**，不是无限精度原cost；正常非零结果bits单项，零结果保守[0,2147483648]；unsupported结果bits列表空/整数null。
- possible_operation_bits为所有候选bits去重排序；integer_candidates为已资格Int32结果去重排序，不能因只有其中一项而冒称全域共识。same_rc_integer_candidates仅16中的rc相同四项诊断，不影响判定；unsupported仍不忽略。
- int32_to_single_exact表示原cost转换全4结果精确；all_operations_exact表示全部理想Single运算精确(unknown→null)。只有这两者true且完整候选合格时原exact-only域已覆盖；expanded_beyond_exact_only仅当本次共识成功而该原exact域条件不满足时true。它不调用旧接口或伪造旧回执。
- integer_consensus_reference只有全部16资格、每个rounded均有效signed32且相同才为整数。否则null，哪怕diag只有一个值也不能代替all16。
- 输入unknown/nonfinite/subnormal则cases空、integer reference null；cost known可保留四转换候选。运算underflow/overflow和Int32域外保存16分支诊断但所有complete consensus null。

所有状态串只是机器合同；UI由root译为中文可读项。源包严格SHA、normal资格和实际值分开，actual cost/SP/完整周期恒unknown。

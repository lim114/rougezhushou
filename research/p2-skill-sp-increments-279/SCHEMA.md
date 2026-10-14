# 279固定缓存合同v1

准备不计完成。原型`skill_sp_increment_reference.py`，公开API仅`skill_sp_increment_reference(payload)`、`source_data()`、`public_example()`及`single_ge_zero_reference(bits)`、`single_increment_reference(bits)`、`mask_bit_reference(mask,slot)`；没有公开source/data覆盖。query拟`sp-increments`，生产集成由root处理。

顶层exact keys：`receiver_exists` tri、`actions`1–50。每action公共`id,kind,ordinary_native_path`；kind为`sp_data_init,skill_data_init,attack_gain,damage_gain`。action/read ID全局唯一非空public label<=120字符。tri仅true/false/null，不接受0/1。

Reads exact keys：PointerRead=`id,normal,exists,identity`；BoolRead=`id,normal,value`；IntRead=`id,normal,value`(signed32/null)；LengthRead=`id,normal,value`(unsigned32/null)；ByteRead同形(value unsigned8/null)；SingleRead=`id,normal,bits`(unsigned32/null)；LookupRead=`id,normal,found,bits`。identity为public label/null，null仅未知标签；pointer exists独立tri。

## sp_data_init

附加exact keys：`captured_blackboard,inited_read,array_allocation,array_install_normally,write_barrier_normally,slots`。前二分别PointerRead/BoolRead，allocation为PointerRead，仅是allocator正常返回资格及opaque指针；它请求长度4，不推返回数组内容。slots恰好4，顺序slot0–3，每slot exact keys：

`slot,key_format_normally,key_identity,lookup,mask_read,mask_store_normally,increment_copy_normally,increment_decode,array_read,array_length_read,array_store_normally`。

slot为0–3固定序号；key_identity public label/null；lookup LookupRead；mask IntRead；increment_decode SingleRead；array PointerRead；length LengthRead；各normally tri。captured BB只捕获一次，各槽不存在另一个pointer。

固定stages：`blackboard_capture,inited_read,array_allocation,array_install,write_barrier`，之后每槽前缀`s0.`到`s3.`加`blackboard_check,key_format,lookup,mask_read,mask_set,mask_store,increment_copy,increment_decode,array_read,array_check,length_read,bounds_check,array_store`。

inited true正常return，后续false；unknown未来null。BB不存在时key/lookup不调用，进入fallback；BB存在时key+lookup独立正常资格，found false进入fallback，true进入BTS路径。BTS路径读取未知mask但正常可继续写，保存fullmask:null、known_set_bit；bits未知不阻断direct slot store。fallback mask未知影响分支，后续null；缺bit默认1.0(bits1065353216)，有bit独立24byte copy+decoder。每槽独立array/length，null/越界导致row.normal=false，保留此前array_install/mask/已写slots。读正常返回空指针时read.normal=true；失败属于之后guard。比较本身normal=true不等于条件true。

## skill_data_init

附加exact keys：`inited_read,duration_first_read,flag_store_normally,ge_normally,first_blackboard_read,duration_second_read,assign_normally,sp_data_read,second_blackboard_read,sp_init_normally`。Reads依次Bool/Single/Pointer/Single/Pointer/Pointer。first duration正常即继续flag store，即使值未知。GE在flag之后；首版rhs0 finite normal/zero得到引用Boolean，未知比较结果则未来null。GEfalse正常跳过firstBB/second duration/Assign；true第一BB需要存在，独立第二duration未知但正常read可作为opaque参数传Assign并继续。SpData不存在失败；secondBB不存在也允许传给Init，没有提前null guard。

固定stages：`inited_read,duration_first_read,flag_store,duration_ge,first_blackboard_read,duration_second_read,duration_assign,sp_data_read,second_blackboard_read,sp_init`。

写prefix：`field:m_inited,value:true`；Assign参数`blackboard_identity,duration_bits,key_identity:null`；Init参数`sp_data_identity,blackboard_identity,blackboard_exists`。此处仅资格化调用，不把另一个sp_data_init action结果自动合并；没有void Boolean返回。

## attack_gain / damage_gain

共同附加exact keys：`sp_type_read,array_read,index_normally,array_length_read,amount_read,single_to_fp_normally,recover_normally`。Reads依次Int/Pointer/Length/Single。damage额外`cancelled_read,modifier_flag_read`，分别BoolRead/ByteRead。spType只测试低byte bit2/4；bit未启用正常return。damage cancelled true或+0x28 flag!=0正常return；该byte的字段中文语义不猜。

固定stages：attack=`sp_type_read,array_read,index,array_check,length_read,bounds_check,amount_read,single_to_fp,recover_request`；damage在sp_type_read后增加`cancelled_read,modifier_flag_read`。modifier_flag_read读取已fresh核的value-type字段ignoreForSp native +0x28 byte；用非零判定，不附加伤害或事件统计。array字段read发生在raw index helper调用之前，null guard在它之后。array length用unsigned32比较，attack索引1/damage2。

amount bits未知/nonfinite/subnormal/越界不能给raw，但若Single转换和Recover请求各自正常事实已明确，其调用可以继续、amount_raw:null。这里未知的是数值而非分支；不能虚构异常或未来false。normal未知仍让后续called:null。请求参数`amount_raw,force:false`；不推实际SP改变或恢复许可。未调用时无recover参数。

## 公共输出

Result top：`kind,source,payload,rows,actual_array_after,actual_sp_after,complete_cycle`；kind=`skill_sp_increment_reference`。后三恒null。source=`valid,status,proof_sha256,method_count,byte_span_count`。

每row固定：`id,kind,called,normal,status,stages,stored_prefixes,slot_references,duration_ge_reference,assign_arguments,sp_init_arguments,increment_reference,recover_arguments,actual_array_after,actual_sp_after,complete_cycle`。stage exact keys=`name,called,normal,reference`。完整stages保留；未资格的分支called:null，已证不调用为false。row.called由receiver/ordinary/source资格独立三态；row.normal为本次闭合支路的正常终态，不等于实际值完整。

stored_prefixes顺序列表：array install=`field:m_incrementsForAllSpTypes,identity,exists,requested_length:4`；mask store=`field:spType,value,known_set_bit`；slot store=`field:m_incrementsForAllSpTypes,identity,index,bits`；Skill flag如上。

slot_references每项=`slot,index_name,mask_bit,value_source,value_bits,mask_reference,array_identity`；index_name仅TIME/ATTACK/TAKEN_DAMAGE/NEVER_USE，value_source为blackboard/default_one/protected_increment/unknown；mask_reference是helper dict或null。不同槽的身份、mask和decoder均不继承前值。

helpers均返回dict，source失效返回null：

- mask helper keys=`mask_int32,slot,result_int32_reference,known_set_bit`，slot0–3，mask可null；result为low32 OR再signed重解释或null，known_set_bit为`1<<slot`。
- GE helper keys=`bits,status,rhs_bits,adjusted_rhs_bits,ge_boolean_reference`，rhs_bits0、调整bits3072837036(0xb727c5ac)；首版finite normal/zero已证，subnormal/nonfinite unknown。
- increment helper keys=`bits,status,scale_q,scaled_numerator,scaled_denominator,raw_reference`；Q4294967296，finite normal/zero的exact scaled signed64域toward-zero；其余raw null。不默认RC/FTZ/DAZ，不把raw转换当实际SP增加。

声明normal=true允许已证正常读但值未知；是否阻断未来按源中分支/运算需求区分。typed direct writes/opaque正常调用可继续；控制条件未知不可选择路径。不把参数payload变成实际实例或current state。

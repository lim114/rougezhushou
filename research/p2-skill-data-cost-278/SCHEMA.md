# 278成本数据固定缓存合同v1（四槽留后继）

准备不计278完成。原型文件`skill_data_cost_reference.py`；API：`source_data()`、`public_example()`、`skill_data_cost_reference(payload)`、`single_cost_reference(operation,cost,modifier_bits)`、`signed_scale_reference(cost,scale)`。没有公共data/source覆盖。Single helper operation仅add/mul，bits为unsigned32原位型。signed helper返回低32乘积。两个helper均返回dict，来源失败返回null。

首版Single安全域：先要求cost:Int32可**精确**表示Single（不是只限定±2^24；允许其它精确可表示整数）。modifier必须finite normal或signedzero；操作结果也必须为精确可表示normal/zero Single。随后有限half-even整数结果必须在signed32范围。其余保留unknown，**不默认MXCSR、FTZ/DAZ、异常掩码或Python默认rounding**。可在后继扩展全部允许RC结果合流；本版不引入RC选择或自动取nearest。源事实closed方法与32-method proof一致。

顶层exact keys：`receiver_exists` tri、`actions`列表1–50，全局唯一public IDs最大120字符（action/read ID不能重复）。每action公共exact keys：`id,kind,ordinary_native_path`，tri仅true/false/null。

通用read exact keys：

- PointerRead：`id,normal,exists,identity`，exists独立tri，identity非空public label或null；null仅未知标签。
- IntRead：`id,normal,value`，value signed32/null（拒绝bool/float）。
- SingleRead：`id,normal,bits`，bits unsigned32/null（拒绝bool/float）。
- BoolRead：`id,normal,value` tri。
- RuneModifierRead：`id,normal,found,bits`，found独立tri；false正常return，无SPdata读取。

每kind附加exact keys：

|kind|fields|
|---|---|
|rune_add/rune_mul|owner_read/character_data_read/skill_data_read/blackboard_read/sp_data_read各PointerRead；modifier_read为RuneModifierRead；cost_decode:IntRead；cost_copy_normally/single_conversion_normally/single_arithmetic_normally/round_normally/encode_normally/store_normally各tri；encoded_payload_identity public label/null。|
|relic_mul|同rune，但modifier_read为SingleRead，没有found key/缺key正常skip。|
|scale_cost|first_data_read/first_sp_data_read/owner_read/second_data_read各PointerRead；cost_decode:IntRead、scale_read:IntRead（在decode之后的独立m_scale读）；cost_copy_normally/encode_normally/store_normally/update_normally各tri；encoded_payload_identity public label/null；update_sp_data_identity public label/null（仅传参身份，不推存在或与first相同）。|
|replace_cost|new_cost:signed32/null；first_data_read/first_sp_data_read/second_data_read/second_sp_data_read/first_owner_read/second_owner_read/third_data_read各PointerRead；modify_type_read:BoolRead；type_value_read:IntRead（原SpType bitmask允许未命名值，不用枚举clamp）；unity_truth_read:BoolRead；encode_normally/store_normally/type_store_normally/update_normally各tri；encoded_payload_identity/update_sp_data_identity public label/null。|

PointerRead正常返回false存在：只有源码到达对应null check才阻断，不能一读取就提前检查。**Single成本kind的skill_data_read不存在是正常早return**。SingleRune modifier found=false也是正常早return。scale的owner_read后仍先second_data_read，再检查data/owner；replace的second_owner_read后仍先third_data_read，再检查data/owner；replace第一owner允许null传给Unity truthiness。unknown存在/normal/found使依赖它的future called=null，不能false。已证异常/早return之后才called=false。

固定stage顺序（每stage exact name/called/normal/reference）：

- rune_add/rune_mul/relic_mul：`owner_read,character_data_read,skill_data_read,blackboard_read,modifier_read,sp_data_read,cost_copy,cost_decode,single_conversion,single_arithmetic,round,encode,store`。
- scale_cost：`first_data_read,first_sp_data_read,cost_copy,cost_decode,scale_read,imul,encode,store,owner_read,second_data_read,update`。
- replace_cost：`first_data_read,first_sp_data_read,encode,first_sp_data_check,store,modify_type_read,second_data_read,second_sp_data_read,type_value_read,type_store,first_owner_read,unity_truth_read,second_owner_read,third_data_read,update`。

replace_cost第一spData字段read可正常返回null，但**encode先于它的null check**。之后raw null导致失败，保留已证encode前缀；不得把它提前跳过。modifyType=false跳过secondData/typeRead/store，onlycost=true；true执行后onlycost=false。修改type后首owner Unity truthiness=false是正常return（非raw-pointer读取成功/非Entity.alive），不再读secondOwner/thirdData/update。true才进行独立后两次读。检查thirdData和secondOwner后用thirdData.spData身份调用Update，不能替换为first/secondData。

scale_cost写后读取owner，再读取secondData；到此才检查secondData和owner。两者正常存在才调用Update(data2.spData,onlycost=true)。数据参数可以是不同身份，m_scale是Int32低32乘法，不当浮点百分比或maxCharge。只记录该调用参数与其正常返回，不推276后续max/解码/计时器或当前SP状态。

Single helper dict exact keys：`operation,cost_int32,modifier_bits,status,cost_single_exact,binary_operation_exact,mathematical_numerator,mathematical_denominator,result_single_bits,rounded_int32_reference`。数学ratio仅理想精确实数运算，**不是**实际MULSS/ADDSS结果。安全Single未知时result bits和最终rounded均null。
Signed helper dict exact keys：`cost_int32,scale_int32,product_int32_reference`（unsigned low32重解释signed32，无clamp）。

Result top：`kind,source,payload,rows,actual_cost_after,actual_sp_after,complete_cycle`（kind值skill_data_cost_reference）。每row：`id,kind,called,normal,status,stages,arithmetic_reference,encoder_argument_reference,stored_prefixes,update_arguments,actual_cost_after,actual_sp_after,complete_cycle`。source：`valid,status,proof_sha256,method_count,byte_span_count`。
actual_cost_after/actual_sp_after/complete_cycle在top及每row恒null。

- stored_prefixes为顺序列表；cost写入：`field,byte_count,payload_identity,decoded_value`，field=spCost、byte_count20、decoded_value=null；type写：`field,value`，field=spType，不推fallback数组及实际owner状态。
- update_arguments：`owner_identity,sp_data_identity,only_update_sp_cost`；normal void update没有虚构Boolean返回。它仅调用参数，不证明运行时更新完成后的字段。
- encoder_argument_reference是成本encoder入参，非实际decoded成本。第二action cost_decode即使全部正常，也始终读取自己独立value，不能从前一个编码入参补值。

所有stages完整列出。正常getter/PointerRead即使返回null，也保留该read.normal=true；之后失败属于row.normal=false。未知读点值或未闭合Single安全域时保留已证prefix，future called=null；不输出source未证数字。只有numeric转换/运算引用闭合且相应normal=true才推进round/encode/store。false/source无效/未资格ordinary分支不能拿候选参数生成实际数值。

例外须按真实控制流：replace_cost的type_value_read正常返回但value=null，仅表示未知Int32，源码直接store，不依赖该数值进行分支/算式。独立type_store_normally=true时可以保留`spType,value:null`的已写前缀并继续owner/Update资格；onlycost仍由已知modifyType=true推出false。不得为此默认为某个SpType或解释真实恢复效果。

first_sp_data_check.normal描述CPU比较正常完成，不是“指针存在=true”。存在false时stage.normal=true/reference.exists=false，随后异常归row.normal=false/store未来called=false；存在unknown时比较仍正常、条件未知，future called=null。

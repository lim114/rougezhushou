# 281设计：完整费用流程中的舍入共识

准备不计281完成；仅本目录，生产/私人状态不改。

原任务提出“完整已证写入/owner/UpdateData顺序”。源事实必须区分：三Single方法85326/85329/85835仅修改费用并返回；owner与UpdateSpData属于另外的84998 scale_cost和84880 replace_cost。不能把它们拼接到Single方法。此纠正与最初任务表述并存，root已确认按五kind独立方案推进。

方案保留278全部默认公开接口/代码/结果。新模块先复用SHA固定的278公开结果作为完整source-qualified prelude与非Single结果，不改旧evaluator；仅在Single行cost_decode stage确实called=true/normal=true时，于新结果副本重建五个数字尾阶段：Single转换、加/乘、round、encode、20byte store。旧返回值及其文件不修改；numeric tail重建是局外纯计算，不是重复执行游戏写入。

280公开scalar helper提供all16保守RC组合的条件整数引用。只有全域合格且一致才能给encoder参数数字。若读值缺失、候选分歧或安全域未闭合，正常round/encode/store的独立事实仍可保存opaque参数及20byte写前缀；它不证明整数、protected roundtrip或修改后decoded cost。

scale/replace直接沿用278公开行的全部既有字段，含deferred raw-owner null check、后续data read顺序、独立owner/data身份、onlycost及Update参数；只附新wrapper分类，不用Single共识改其逻辑。每个action的decoded cost仍独立；不能把前行encoder参数当下行解码值、不能合并乘加再取整。

固定内部模块路径与两个core文件SHA先于载入检查；没有公共source/evaluator注入，没有monkeypatch。依赖公共source_data门和本组links/manifest都有效才调用组合逻辑；任意来源失效不输出数值/写入/更新引用。新模块的输入边界沿用278严格五kind合同，不增加RC选择或任意mode参数。

验收：新共识整数到实际source store prefix；RC分歧/未知输入但normal资格可opaque完成；normal未知保留future called:null，failed future:false；prelude失败/正常早return不越过；五kind输入严格校验、ID唯一；scale/replace既有字段与278结果完全相同；旧默认API before/after字节相同；2cores/2source包/新links任一失效全部抑制；actual cost/SP/完整周期恒unknown。

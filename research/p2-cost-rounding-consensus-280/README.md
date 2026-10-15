#280缓存准备：费用舍入共识

新API不改变278 exact-only接口。对三种成本数字前缀的Int32→Single转换四RC，再对Single加/乘四RC，共16组合；只有全部正常有限/零结果经原half-even规则成为同一有效signed32整数时才给共识。未知游戏MXCSR不以CPU默认nearest替代，未证同/异RC耦合不缩成4个对角线。

10×Single bits3e4ccccd约0.2的中间结果不精确，但全部最终整数为2；10×bits3d4ccccd约0.05仍为0/1未知。Single约1.05(bits3f866666)在费用20闭合21，费用30仍31/32。16777217转Single有16777216/16777218两个候选，乘0最后共识0、乘1继续未知。负数不夹成零，zero结果不猜实际符号位。

两步必须逐次舍入，不能直接对无限精度cost×modifier取整。每行decoder与modifier独立，public.independent_next_decode实际声明101，不继承前行整数。候选集只是源支持的条件正常结果，不是游戏取样或RC选择；normal指令/round资格未知时不把未来调用写成false。

nonfinite/subnormal/underflow/overflow或任何Int32域外候选使完整共识unknown。precision异常handler重写输入/结果不在引用域，不默认mask已开启。这里只给条件数字与可能下一encoder入参，没有encoder/store/update操作；actual cost、SP和完整周期始终unknown。

9源方法、546独立指令、759 fresh原文件跨度；Intel Volume1及Volume2abcd权威文档支持4RC和明确round控制。source SHA/support文件失效使全部引用失效。PDF下载失败及初次多匹配fused标题的更正完整保留，未采用错误标签。

准备不计280完成，不修改生产/tests/私人状态，不执行DLL/读取内存/操作游戏或聊天。root正式集成、必要验收与普通push后另记完成状态。

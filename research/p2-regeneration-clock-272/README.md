# 第272节：常态生命回复率与逐点定时器

候选本机原件与第271节相同：DLL SHA256 583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5，metadata SHA256 d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f。26方法、1589条唯一可达指令、277段元数据/原件字节均重新与原文件逐字节核对。未执行DLL或读取进程内存；不证明当前游戏实例、服务器或热更新等价。

普通get_sumUpHpRecoveryPerSec读取属性13、maxHP、属性19，先FP乘maxHP×ratio，再FP加flat。这里只接受独立已读的FP快照及正常读取资格。三花13/19 MULTIPLIER的旧资料不含当前GetValue缓存脏标链；不能拿旧double藏品组合直接代入作为实际FP属性。

Entity.m_hpRecoverTimer声明类型是PrecisePeriodicTimer，virtual槽4/5/7分别为ready/Update/Next；继承基础ResetButKeepPastTime。周期有效为P>42950，到期为R<42950，均是严格FP原值条件。有效时Update写wrap(R-delta)而不夹零；每次Next成功先写wrap(R+P)，再独立读取HP、请求wrap(HP+ONE)并访问setter，随后继续检查。初始无效定时器正常跳过，连delta也不减。这里没有推导setter接受、最终生命、回调或实机时钟。

脏标仅纳入13/19。13由原jump table的第6项指向0x1806f73e3，19由独立直接跳转到相同分支。MAX_HP等其它属性有额外前处理，排除。该分支先drain(0)，正常返回后首次读取回复率判断能否回复；成立才第二次独立读取回复率计算新周期。不能默认两次快照相同。资格不成立时MarkInvalid把P/R都写-ONE。改速公式为past=wrap(oldP-oldR)，newR=max(0,wrap(newP-past))，随后写newP；不是按旧剩余比例缩放。

本节FP倒数只支持分子ONE、分母0（原码返回-ONE）或非零绝对值≥42950的安全子域。原125条division指令累积额外一位商，最终加1、无符号右移1、再赋符号；该子域不进入溢出饱和分支。更小非零分母保持未知，不用Python浮点round或简单整除伪装完整原生除法。第二次读取即使变为零、负数或极大数，也不借第一次的资格或数值替代。

公开算例：旧P=1/2、R=1/4，先推进1/8秒后R=1/8；两次独立声明回复率4，newP=1/4，保留past=3/8使newR夹为0。下次声明推进3/4秒，以900、901、902、903四个独立HP读值分别得到901、902、903、904的请求参数，最终定时器P/R均1/4。最终HP不等于自动取904。

每次HP访问的正常返回独立。访问明确失败则保留已经Next的状态并停止后续；访问未知且仍可能补发时，已知Next前缀与最终状态分开。正常类型域的未知FP与零乘可闭合为零，但不能跳过读取资格。原始计算反例、源码、初次失败测试及夹具错误保留于verification/sections/272-review-findings.json与对应before文件，修正后用同输入重算。

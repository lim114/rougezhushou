#279缓存准备：按类型技力增量与初始化

这组纯文件参数参照支持SpData.Init四槽、SkillData.InitIfNot、攻击/受击的单次增量请求。没有执行游戏DLL、读取内存、操作游戏或使用私人截图。来源为17个原方法、938独立指令、1670个fresh原件字节跨度；源包SHA不符则所有数值参照失效。

Blackboard指针是一次捕获后四槽共用；各lookup、mask和array字段快照独立。缺mask bit的槽默认Single1.0，但不会启用spType，攻击/受击仍需各自bit。BB成功先BTS写mask、后数组null/长度检查，因此短数组失败也保留已写mask。未知Single原bits/未知完整mask的正常direct write只留未知值前缀，不补成0或1。get_inited只证数组指针非空，不证明长度和内容。

SkillData先读duration、写m_inited=true，再做Single GE；失败不撤销flag。GE是inclusive >= rhs−Single epsilon，rhs0的−epsilon位型b727c5ac本身命中true；它不是固定点strict GE/EPS。first/second duration、first/second Blackboard分别资格，second BB可null传给SpData.Init。

攻击索引1、受击索引2来自raw helper1844dc660的mov eax,ecx/ret，metadata名字未知。Single转FP是MULSS(Q=2^32)+CVTTSS2SI，安全finite normal/zero signed64域才给toward-zero请求量；例如−1→−Q，Single epsilon→42949，−2^31→MIN64。越界/非有限/环境不明仍unknown；独立声明正常的调用可传opaque参数，不制造数值。

OnTick普通指令没有直接slot0数组读取/乘法。完整数组归属、实际SP、事件数量、自然时钟和技能完整周期一律unknown。这里只分析局外单次参数与调用前缀；没有实战收益统计、战斗站位或自动操作。

public-example.json含全部4kind、无bit默认1、独立lookup/mask/array、mask写后数组越界、负Single epsilon inclusive、flag早写后GE未知、正负请求、cancelled早return和未知转换opaque请求。准备不计279完成；root提升生产/必要验收/普通push后另记真实状态。

CPU指令资格：[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)。它不证明游戏当前MXCSR或当前hotfix。

# 第271节：藏品逐包修饰的数值参考

本节绑定候选本机 GameAssembly.dll 与 metadata 的固定字节，未执行游戏原件或读取进程内存。21个方法、1630条唯一可达指令及420段元数据/原件字节已逐字节复核；不证明当前运行游戏、服务器或热更新与候选原件等价。

12件固定来源的参数、模板及buff索引沿用已绑定公开数据。物理/法术/真实承伤来源以base_one规则在float32层合并成一个模块；三件治疗及两件元素来源为独立模块。治疗只纳入heal_scale，不纳入另两种生命回复通道；霜牡蛎只纳入buff索引1的damage_scale，不纳入索引0的元素积累倍率。

预处理顺序与修饰顺序是两个独立声明，最多36种组合仅用于展示离散数值参考，不能作为实际可达顺序、概率或平均值。普通原生链、无中间修改、Modifier存在、入链值、类型/目标/方向、启用/黑板/数字资格和不可改值标记均独立。接第269节时还必须声明创建与返回值到入链间未改变的资格。

DamageScale取消早停是cancelled且isDamage，治疗模块则直接按cancelled早停。类型过滤与isDamage使用同一个类型值，不能把关联条件当作两个独立未知。缺失黑板的异常、数值查找失败的默认ONE、正常转换资格、setter尝试与实际存储分别记录；不可改值不证明前面的读取/转换能正常返回。

固定1000FP的三治疗模块得到9380208443390和9380208443391两个raw参考；三法术来源合并后得到8160437248000和8160438272000。差异保留为精确整数，不在小数显示时抹平。实际Modifier、HP/EP/SP结算、完整伤害/治疗、事件时钟、获取顺序及热更新仍未知。

## 转换硬件依据

查阅日期：2026-10-14。[Intel SDM Volume 2A](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf)，253666-060US，2016年9月：CVTTSD2SI章节3-274/275的操作伪代码为截断，列有Invalid、Precision异常；CVTSS2SD章节3-261/262列有Invalid、Denormal异常。[Intel浮点参考表](https://www.intel.com/content/www/us/en/developer/articles/technical/floating-point-reference-sheet-for-intel-architecture.html)，ID659453，2021-03-29更新，说明MXCSR及异常屏蔽对行为的影响。

本节没有读取当前MXCSR。因此非有限、超signed64范围、非零subnormal及乘2^32后非整数的转换不被核准为正常返回。旧版手册CVTT描述段与同页操作伪代码存在措辞冲突，采用指令操作伪代码和异常列表，不由该描述推导新舍入规则。没有将异常屏蔽状态或任意默认结果伪造为实际运行事实。

## 修正与验收

三项原始反例及修正前源码见verification/sections/271-review-findings.json和271-review-before-module.py。修正后保持原输入重新计算，不覆盖before。测试、Windows公共隔离窗口和原项目更新回执在verification/sections；私人配置、本局状态和聊天绑定不进入证据或提交。

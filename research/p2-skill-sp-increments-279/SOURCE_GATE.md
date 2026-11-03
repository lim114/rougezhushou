# 279准备来源门：四槽技力增量与初始化前缀

此目录是纯文件准备，不是279完成或实机技能回转验收。目标是将局外模型中的按类型增量、初始化支路和失败前缀接到已闭合的原始参数链；当前SP、运行中数组内容、自然计时器相位和完整技能周期仍未知。

原件：GameAssembly.dll SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`；global-metadata.dat SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。本轮只重读文件字节、v29元数据和有界原生CFG，没有执行DLL、读取进程内存或操作游戏。278及276旧原件保留；只复用其方法字节，不复用已撤下的保护整数编码→解码传播结论。

## 已证规则

1. `SpData.get_inited` 32850普通分支仅比较`+0x78`数组指针是否非空；不检查长度或四个槽。`get_incrementsForAllSpTypes` 32851仅返回该数组字段。getter结果不能替代完整初始化或槽值读取。
2. `SpData.Init` 32852入口`0x18252b311 mov rbp,rdx`只捕获一次Blackboard参数；四轮`0x18252b440 test rbp,rbp`均使用同一指针。每槽独立的是动态键生成/TryGetFloat返回、mask字段和数组字段，不是Blackboard指针存在性。旧278准备只记录了独立BB尝试、mask和array读点，没有生产4槽实现；此处将captured pointer资格写成明确合同，禁止一轮不存在下一轮存在。
3. Init已初始化结果true时正常早return。false时请求新Single[4]、写`+0x78`、调用write barrier，然后循环0–3。无对应mask bit且该槽未从BB取到值时，默认Single **1.0**，RIP地址`0x186e3fbe0`原8字节`0000803f00000000`。不得沿用早期准备标签的0。
4. BB查找成功时，每槽独立读当前signed32 mask，BTS槽号并先写回mask，再读数组、检查null和unsigned32长度、写Single槽。即使随后数组为空/过短，已写mask仍保留。mask未知但读取正常时，直接BTS/写可保留完整mask未知且该bit已设置的前缀；它不参与此路径分支。
5. BB不存在/未找到时，每槽独立测试当前mask bit。无bit→1.0；有bit→复制24字节protected increment，再用237393保护Float隐式decoder独立正常返回的bits。decoder实际结果未知，不能由编码参数补值。此fallback的mask未知会影响分支，未来调用未知。
6. 每槽`0x18252b4ef`重读数组字段，null和长度检查发生在此前mask写之后。长度比较是低unsigned32；slot store是32位Single原bits的直接写，即使bits未知但正常写资格已给出，也可保留未知值写前缀并继续。不同槽的数组身份不自动合并；不能由四次写推某一实际数组完整。
7. SpTypeIndex元数据为TIME0、ATTACK1、TAKEN_DAMAGE2、NEVER_USE3、E_NUM4。SpType为NONE0、TIME1、ATTACK2、TAKEN_DAMAGE4、ATTACK_OR_DAMAGE6、ALL7。第4初始化mask bit8没有SpType枚举名，不能发明第4种回复机制。
8. `SkillData.InitIfNot` 32863普通未初始化路径先独立读duration，再于`0x18252a587`写m_inited=true，之后调用Single GE(durationFirst,0)。GE/Assign/SpData.Init失败不回滚这个已写flag。GEtrue时先读第一BB、再独立重读duration并调用Assign；然后独立读SpData和第二BB，并调用SpData.Init。第二BB未检查null即可传参，不能把它提前挡住；两次duration、两次BB身份不可复用。
9. Single GE220359是`SUBSS(rhs,epsilon) → COMISS(lhs,adjusted_rhs) → SETAE`，对正常有序比较为**inclusive >=**。epsilon bits为`0x3727c5ac`，rhs=0的调整值是精确Single`0xb727c5ac`。它不是277固定点strict >或固定点EPS42950。首版只支持lhs finite normal/signed zero与rhs0；NaN、subnormal等环境资格不猜。
10. Attack/Heal消费者66749测试spType byte bit2，读取Controller数组`+0x38`，raw helper参数1得到索引1；Damage消费者66748测试bit4，再读isCancelled及Modifier `+0x28` byte，再取索引2。Modifier为value type，metadata字段`ignoreForSp:System.Boolean`boxed offset56，native value offset40(0x28)，这里非零即正常跳过技力请求；不扩成伤害数值或实战事件统计。raw helper`0x1844dc660`已fresh闭合为`mov eax,ecx; ret`两条；metadata身份仍未知，不命名。
11. 消费者Single转FP220498是`MULSS(Single,Q) → CVTTSS2SI(Int64)`，Q为精确Single4294967296(bits`0x4f800000`)；不是Double乘法。finite normal/zero且理想乘积落在signed64有效域时，乘以2^32精确、转换toward-zero，可给请求量raw。越界、subnormal或nonfinite保留未知；单独声明正常调用也不推实际数值。
12. Attack/Damage将该量作为`_RecoverMp(amount,force=false)`参数。它仍有自己的hotfix、owner/stopped/SP读取和setter链；本节只记录请求量及该调用资格，实际SP支付/增加、alive/clamp和完整周期不推。
13. OnTick66751普通78条没有Controller `+0x38`数组读取或slot0乘法；其自然回复由UpdateMultiple得到count、NextMultiple、Int32→FP(count)和_RecoverMp构成。不得把初始化slot0=1.0当自然事件乘数。数组间真实alias和间接callback关系仍未知。

## 仍未闭合

- 四个动态BB键的完整字符串构造/当前表项；lookup使用独立opaque key身份，不能发明字符串。
- 当前XLua/hotfix、实际对象、decoder返回、数组alias或回调后内容。
- 任意rhs Single GE的inexact SUBSS/MXCSR/异常掩码；本节仅rhs0安全域。
- actual SP、事件发生数量、自然计时器、技能完整周期和战斗效果。本程序仅局外参照，不读取实时战斗站位或干预游戏。

CPU资格复用[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)，文件SHA256 `2df6ae80aad83945c4879ef702b863ccbacaf5467e5ea079f1d7261e69ebc315`。它说明指令语义，不说明游戏当前MXCSR。所有pointer存在、read正常性、bit值、opaque身份和调用正常性单独资格；null标签不等于空指针。

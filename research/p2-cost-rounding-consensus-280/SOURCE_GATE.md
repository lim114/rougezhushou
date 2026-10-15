# 280准备来源门：费用Single舍入共识

此组只扩展费用数字引用域，不修改278 exact-only接口或旧回执。准备不计280完成。cost是各行独立正常解码的Int32，modifier是独立Single原bits；即使前一行已有编码入参，下一行也不能继承为实际decoded cost。

原游戏文件绑定沿用278：GameAssembly SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`；metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。原件bytes将fresh复读，不执行DLL/内存/游戏。

## 原始数值链

- Rune Mul85326：decoded cost→MOVD→CVTDQ2PS(`0x180cf70c6`)→MULSS(`0x180cf70c9`)→raw round helper18059e290→Int32 encoder参数。Rune Add85329分别为`0x180cf6e95` CVTDQ2PS与`0x180cf6e98` ADDSS；Relic Mul85835分别为`0x180d0f2a6` CVTDQ2PS与`0x180d0f2a9` MULSS，后者内联同一half-even algorithm。三个源都是逐次修饰spCost，不能把多次乘加合并取整，也不能推实际费用decoder roundtrip。
- raw round helper18059e290 metadata身份仍未知。它先精确把Single扩展Double，再以fractional part、half值与整数奇偶处理ties；非tie正数走floor(x+0.5)、负数走ceil(x−0.5)。callee1804d57f0为原位Double拆fraction/integer，1804d3200和1804d58c0含软件bitmask及显式ROUNDSD fallback。9和10 immediate的bit2=0，选立即数RD/RU，不读取MXCSR RC作floor/ceil。
- 本组仅对finite normal或zero Single且half-even整数落在signed32域的每个候选证明round规则。abs(x)>=0.5且此域内，Single(24 significant bits)扩展Double后加/减0.5可精确表示；abs(x)<0.5时，Double加/减0.5即使inexact，各正常RC也不跨±1，floor/ceil的整数仍0。因此不需要把游戏Double RC默认为nearest。CVTT有效域为toward-zero，最终整数还必须signed32有效；域外不推indefinite返回。

## 权威CPU依据与边界

[Intel SDM Volume1 December2024](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf) SHA `2df6ae80aad83945c4879ef702b863ccbacaf5467e5ea079f1d7261e69ebc315`：4.8.4/4.8.4.1及Table4-8说明相邻可表示值与四RC；11.4.1说明CVTDQ2PS inexact采用MXCSR；AppendixD说明精度、underflow/overflow与异常响应。只有CPU默认设置描述，不能充当游戏当前RC证据。

[Intel SDM Volume2abcd](https://cdrdv2-public.intel.com/774492/325383-sdm-vol-2abcd.pdf)已实际保存11,349,721 bytes，SHA `bc4348020f5d5a27b0207c61e3c88d4e610eaf428658dc5d08a1cc84f98a719b`；fresh PDF bookmark目标ADDSS/CVTDQ2PS/MULSS/ROUNDSD页索引151/378/889/1311。ROUNDSD说明imm8选择RC及precision控制，源软件分支与显式RD/RU分支在安全域得到同一floor/ceil。首次PDF筛选误多匹配V4FMADDSS，原件及修证`SOURCE_INSPECTION_CORRECTION.md`保留；v2不采用该额外命中。

normal指的是声明的普通硬件正常转换/运算结果、读取与round正常完成；不默认为precision mask已开启。未处理precision exception可能阻断，handler也可能改输入/控制/结果，这些不在条件引用域。当前MXCSR/FTZ/DAZ/异常掩码和handler行为均未知，不能由共识整数推实机已执行、费用已写或SP已变。

## 共识规则

1. 对cost→Single枚举RN-even(0)、RD(1)、RU(2)、RZ(3)，每个转换结果再对ADDSS/MULSS枚举四RC，最多16对。保留每个转换后的Single再进行运算，不能只round无限精度cost×modifier。
2. 不要求两条指令同RC。all16是对可能同RC/不同RC的保守超集，非声明游戏确实切换过RC。同RC四条对角线可作为诊断，但不能用它们替代未证明耦合的全16范围。
3. modifier必须finite normal或signed zero；非零理想结果与所有候选必须在finite normal范围。subnormal/nonfinite/overflow、任何Int32 round域外候选都使完整共识未知，不假设FTZ/DAZ、不丢弃不利候选。数学零结果保留两种符号零候选，不猜source实际零符号，最终整数都为0。
4. 只有16对全合格且最终half-even Int32完全一致才给`integer_consensus_reference`。若候选分别0/1、31/32等，保留候选和分歧，完整数值未知。数值引用是条件正常链参数，不是实际decoded费用。
5. 10×bits3e4ccccd可共识2；10×bits3d4ccccd仍0/1未知。Single约1.05(bits3f866666)在cost20可共识21，而cost30可能31/32，不笼统把“1.05”当一个精确实数或所有费用都闭合。条件例不是游戏观察。

剩余：真实激活顺序/对象/BB/hotfix/控制环境、任何protected编码后decoded值、actual cost/SP/时钟和完整技能周期。278 exact-only接口及历史scope不改；新查询独立，不能把它的候选当外部游戏数据。

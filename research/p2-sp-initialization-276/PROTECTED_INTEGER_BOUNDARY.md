# 276 ObscuredInt 编码/解码闭合结果（纯文件来源）

结论：**可以证明条件XOR不变式，不能用“编码/解码正常返回”直接证明输入数值不变。** 当前276草稿的getter返回值应改为独立、严格typed的已声明decoded getter读点。IMUL乘积只表示送入编码器的Int32参数；不能自动传播到getter返回、初始min或后一次maxSp字段写入。本次仅归档新.cache来源，冻结中的核心/manifest/原47证据未修改。

`source-proof-roundtrip-276.json` SHA `a80b9635ff6f434c76a54634d70889d9c0081a08173ee0fad2104b75e2df06f6`：11完整native CFG、305独立指令、452个原DLL/metadata片段重新逐字节匹配；10方法有ThirdPartyAssembly exact token→native pointer及metadata参数/返回签名。0x1865ec110共享generic helper仅保留原地址/11条原指令，没有捏造metadata身份。原GameAssembly/metadata SHA与47证明一致；没有DLL执行、游戏进程内存读取、游戏操作、聊天或生产/core修改。

## 有证顺序

|入口|身份/地址|已经证明的行为|
|---|---|---|
|Int32→ObscuredInt|237419 /0x18660b950|清20字节结果，调用ctor237407，返回同一结果buffer。|
|ctor|237407 /0x18660b650|0x...b6a3读取static K1，0x...b6a5存currentCryptoKey；随后调用单参数Encrypt237409，写hiddenValue，再读取Detector运行状态以记录fakeValue/active，inited=true。|
|单参数Encrypt|237409 /0x18660ad50|0x...adc8独立读取当前static K2，返回32-bit `V xor K2`。它没有读取先前保存在instance内的K1。|
|ObscuredInt→Int32|237420 /0x18660ba40|调用InternalDecrypt237418，不直接返回原ctor参数。|
|InternalDecrypt|237418 /0x18660b0d0|完整CFG66条，inited=true时读hiddenValue和currentCryptoKey，并调用237412；之后独立检查detector和fake值，可调用作弊事件。inited=false是另一个初始化零并返回0的正常分支。|
|双参数Decrypt|237412 /0x18660abc0|saved key非0时直接XOR该key；saved key为0时另读当前static K3并XOR。|
|修改static key|237408 /0x18660b3f0|0x...b43a把调用方的Int32直接写入static cryptoKey，key不是不可变常量。|
|类初始化|237436 /0x18660b610|初始static cryptoKey=444444；不能据此认定每次实际读取永远为444444。|
|Detector运行资格|237935 /0x186606920|独立读取实例/运行标记；未建立实际运行状态。|
|作弊回调|237911 /0x186605700|包含indirect delegate call和virtual tailcalls，实际目标/效果未知。|

布局metadata所列value-type field offset含16字节boxed header；原ctor/decrypt使用unboxed byref的+0/+4/+8/+12/+16。本证明同时绑定metadata field bytes/registered field offsets以及真实操作数，不把static cryptoKey当成instance字段。

## 精确的条件关系

对于新构造、inited=true、完整复制的同一20字节值对象，记输入位型V，ctor第一次保存key为K1，Encrypt独立读取key为K2：

* K1非零：decoded=`(V xor K2) xor K1`。仅在K1=K2时得到V。
* K1为零：Decrypt再读fallback K3，decoded=`(V xor K2) xor K3`。仅在K2=K3时得到V。

这些是在独立参数关系下的source数学不变式，**不是本机游戏中key已经相等的证据**。现有276 payload不包含这三个key读点或保护态完整性，也没有证明跨读点static key不变。`no_intervening_state_changes`原合同只是声明的owner/type/cost/增量/max/timer链；不能悄悄扩展为已核验的全部codec/回调全局状态。

具体源允许的数学反例（不是执行DLL结果）：V20、K1=1、K2=2、inited=true、detector=false，hidden22，decoded23；ctor及decode都可正常返回。V20、K1=0、K2=2、K3=3，decoded21。公开SetNewCryptoKey具有提供这种读点变更的直接写入口；不声称游戏确实这样改变过key。

相同key的正控V20/K1=K2=1→20，只证明条件关系。未知keys时，即使IMUL结果0也不能把decoded getter固定为0；0 xor K2 xor K1仍可非零。MAX/初始min必须使用独立getter读点，而不是把正常返回资格当作roundtrip等价资格。

## 推荐的产品边界与后续

保留`max_sp_reference(cost,charges)`的已证low32 IMUL参数，但capacity result分别显示“编码输入参考”和“独立getter decoded读取”。新增独立getter读点需要不同ID、正常返回三态、typed Int32/null；未知decoded返回值则实体maxSp参数及初始min保持未知（typed MIN32闭合等纯数学域可单独处理，不能绕过read资格）。首/次两次getter依旧不能复用。

若未来确有必要建立自动roundtrip能力，应取得/独立声明同一结果buffer、inited、keyK1/K2/K3、完整copy、普通native路径、实际callback/保护态与无间隔变化资格并重新验收。当前局外应用不读取游戏受保护内存；为了推出一个本来可由独立getter声明处理的参考数值，没有必要改变此边界。

剩余实际unknown：真实keys/保护态、hotfix与回调目标、payload身份、完整copy、真实decoded getter和实际SP。此取证不关闭完整Entity/Character/BasicSkill初始化或完整技能周期。

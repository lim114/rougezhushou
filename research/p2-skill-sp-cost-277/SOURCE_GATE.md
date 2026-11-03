# 277 技力门槛、最小参数与扣费意图来源门

准备范围仅cache：不修改production、测试、正式计数，不执行DLL，不读进程内存，不操作游戏/聊天。首选实质功能组是 **技能门槛覆盖与扣费意图分离**：连接AssignData/ModifyCostMinSp/ModifyCastWithNoSp参数、spEnough的分支比较、ReduceSp的豁免和Modifier构造/Apply调用前缀。它处理当前未实现的m_costMinSp门槛与成本差异，不能用一层包装或新归档冒充完成节。

## 已证入口与顺序

|入口|索引/地址|成立事实/范围|
|---|---|---|
|ModifyCostMinSp|72712 /0x18095aec0|普通native分支0x18095af05直接写Int32 m_costMinSp(+0x9c)，无clamp/max/编码；另一分支XLua，效果未知。|
|ModifyCastWithNoSp|72713 /0x18095ae50|普通分支写bool m_castWithNoSp(+0xa0)，独立hotfix分支。它不是任意技能能否施放的完整资格。|
|AssignData|72662 /0x1809582e0|729条原CFG，先赋data/owner，再BB union/virtual preprocess/Delta与ability/behaviour等初始化。0x180958c76给GetIntOrDefault default−1，0x180958c84返回后0x180958c90写m_costMinSp。完整方法不等于已知cost/初始化SP；虚调用与BB值保持独立。|
|spEnough|72632 /0x1809617c0|先独立owner的Unity null/equality判断；invalid→false。0x1809618a7首次signed读取m_costMinSp，<0才读canCastWithNoSp，true直接true；false读owner.SP然后独立SkillData.spCost。>=0跳过free-cast和dataCost：先读owner.SP，再于0x18096191a另读m_costMinSp作门槛。|
|SkillData.spCost|32861 /0x18252a950|复制protected cost20字节，调用237420 decode。返回decoded值必须独立声明，不能从opaque payload或编码输入推断。|
|GE(FP,FP)|220331 /0x1866e4ba0|0x1866e4c24计算wrap64(threshold−EPS)，随后signed FP.GreaterThan；比较是严格`SP > wrap64(thresholdQ−42950)`，EPS相差恰42950时为false。|
|ReduceSp|72702 /0x18095dad0|传入delta为Int32；0直接true/no request；否则独立canCastWithNoSp，true直接true；再virtual canSkipReduceSp，true直接true。其余signed32 NEG delta，Int32ToFP，读owner作为NewSp source/target，NewSp正常返回后再独立读owner作Apply接收者。不读m_costMinSp，不自动重算cost。|
|NewSp|71008 /0x1808b2670|raw>=0→ADD，raw<0→MINUS，value=Abs(raw)，targetType immediate1=SP，调用71001 ctor；constructor callbacks及返回payload不是自动已知。|
|TSMath.Abs/FP.Abs|220545 /0x1866fed50→220459 /0x1866faa10|一般absolute；MIN64特判为FP.MaxValue=0x7ffffffffffffffe，不能Python abs→2^63。FP.cctor220527证明该常量。|
|ApplyModifier|66665 /0x1806efd80|signature仅(modifier:Modifier,force:Boolean)→Boolean；ReduceSp调用force=false。r9=0是MethodInfo，不是公开mask参数。返回值须独立，不当成已扣SP。|

### 纠正错误前提

`m_costMinSp`不是max(cost,min)的地板。负数是回到dataCost/free-cast路径的选择；非负数是独立门槛覆盖。门槛5、dataCost20、SP5可以满足这一单独getter条件，而ReduceSp(delta20)仍提出−20请求；这不表示完整技能可触发或请求被实际接受。

maxChargeTime/最大储存容量未被spEnough/ReduceSp这些普通方法读取。不能把储存2充能的最大技力40当单次dataCost20门槛，也不能自动扣全部储存充能。当前/首发实例、derived virtual策略、时钟及完整周期未知。

初次m_costMinSp和SP getter之后的第二次m_costMinSp是不同读取；get_owner/Unity比较、SP getter、NewSp source/target owner、Apply接收者也必须区分。正常返回与ordinary path不能合并这些读点或实参。

## 枚举与payload边界

metadata默认值是压缩signed32，不能把原byte02误读成枚举2。TargetType.SP=1；DeltaType.CANCELLED=0/ADD=1/MINUS=2。NewSp不会选择CANCELLED，0 raw会选ADD但ReduceSp(delta0)早已短路，不调用NewSp。PlayerSide构造参数0已由Torappu.PlayerSide.DEFAULT字段316438/default compressed byte00绑定；copy136字节和ctor后可选hotfix保持opaque直到另有原件与资格。

ReduceSp `neg ebx`为低32位NEG：MIN32仍为MIN32，FP参数为MIN64，NewSp magnitude为9223372036854775806。负delta会产生正FP ADD请求；不把测试声明的负数擅自夹成0。`ApplyModifier`的force=false与CancelReasonMask不是同一变量。不要从请求的方向/大小、正常构造、Apply返回true推真实setter、owner.SP变化、扣费成功或回转完成。

## 其它完整生命周期的已证边界

Character.CreateSkill76049/_PreprocessSkill76055/_AssignSkill76057先SkillData.InitIfNot/isValid、创建/前置处理，再AssignSkill对存在的skill调用virtual AssignData(data,owner,externalBB,Delta)，最后PostprocessData(talentMap)。这些virtual/dataFlow/behaviour目标和回调未知，不能宣称完整生成后的SkillData/SP参数唯一由表值决定。

BasicSkill.OnInit72675只在普通前缀清registeredAsModifier/triggerCnt/isOverloaded、设置range与anim引用，随后逐个virtual Behaviour.OnInit；没有直接SP/time重置写入。OnSkillStart72666/End72667含owner通知、行为virtual/event/audio等；不能因方法名Start/End就推断在哪个frame扣费或恢复计时器。UpdateSpRecovery72703根据allowSpRecoveryWhenAffecting/isUsedUp/virtual isAffecting切set_registeredAsModifier，未直接给14/30属性或Timer赋数值。OnCastFinish72704依据virtual affecting走m_waitForSkillEnd=true或另一个virtual end路径。真实注册影响与周期仍未知。

## 严格未知分支

typed tri：读点/返回/存在true、false、null不能混用；unknown路径以source分支合流，未来可能调用是called=null，不是false。先发生的已证prefix保留，未知/异常之后受影响状态未知。不得复用276前件的False过claim；guard缺失不产生数字。入场gettertrue不等于可施放/无控制/活着，跳费true也不等于技能成功。

固定合同见SCHEMA.md；SCHEMA_PLAN.md保留早期建议，不作为最终接口。边界literal见boundary-cases.json。原CFG/metadata与精确byte manifest由source-proof-preparation-277.json提供（49方法/4825独立指令/6859fresh spans，追加FP.Division和Torappu.FP字段以闭合EPS及Abs常量）。前48方法原包已按真实原SHA9aef494fa5e6740bed3d89240174040390b941208bb011627f8ee86864d93098精确保留于source-proof-preparation-277-before-fp-closure.json，原binder字节亦封存。

ApplyModifier的方法签名/返回Boolean已经闭合；其558条有界native提取包含未展开indirect jump table以及动态回调，不能把bounded traversal finished误称全部实际SP分支闭合。本组只引用调用及独立正常Boolean结果，不建模Apply内部数值、Mask过滤或支付成功。

缓存草案及公开例通过40项必要准备检查和完整6859span fresh核对（preparation-check-277.json），仍不计277完成；正式中文界面、必要测试/真实窗口、提交/普通push/要求索引同步由root完成。

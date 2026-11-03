# 278已核技能/SP数据修饰来源门（仅准备）

原件：GameAssembly SHA583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5，metadata SHAd3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f。纯文件提取/元数据；没有执行DLL、读取游戏内存、操作游戏或聊天、修改生产/测试。之前两条错误准备标签与修证保存在preliminary-label-corrections.md。

## 成本修饰：当前实例独立读点与转换层

|method|源地址|已证数值/顺序|
|---|---|---|
|CSkillCdMul.DoPreprocessChar85326|0x180cf6fb0|owner→Character.get_data75906→BattleCharacterData.mainSkill(+0x108)；mainSkill=null正常return。Rune.blackboard→TryGetFloat，false正常return且不读spData。true读取SpData及protected spCost20bytes并独立decode；CVTDQ2PS→MULSS→raw round helper0x18059e290→Int32编码→20bytes spCost写入。|
|CSkillCdAdd.DoPreprocessChar85329|0x180cf6d80|同类正常/缺key分支，但ADDSS；只修改spCost，不是直接修改回复率/计时器。|
|CSkillCostMul.DoPreProcess85835|0x180d0f1a0|预处理context的owner→Character.get_data→mainSkill；mainSkill=null正常return。BasicRelic.blackboard.GetFloat→独立spData/cost decode→CVTDQ2PS→MULSS→Single精确升Double→inline round→Int32编码→20bytes spCost写。不能假设BB缺key正常return。|
|SpScaleAfterSkillCast._ScaleSpCost84998|0x180cef770|Behaviour.get_data第一次→spData→cost decode，随后独立读取m_scale(+0x20)，**low32 signed IMUL**；编码和20bytes写入。随后独立owner读、第二data读；data/owner检查后用secondData.spData调用Entity.UpdateSpData(onlyUpdateSpCost=true)。无Single乘法/round，也不读maxCharge。|
|ModifySpDataAfterSkillCast._ModifySpData84880|0x180cdef00|独立输入Int32 newSpCost，先编码再检查firstData.spData是否null，然后20bytes写；随后modifySpType字段true才取secondData并直接写配置SpType，onlyUpdateSpCost从true切false。之后firstOwner→Unity truthiness；true才secondOwner→thirdData→raw owner/data检查→Entity.UpdateSpData(thirdData.spData,onlycost)。不能复用三data/两owner读。|

Character.get_data75906返回类型已fresh核为Torappu.Battle.BattleCharacterData；field88069 mainSkill:SkillData偏移0x108。不是persistent Torappu.CharacterData.favorKeyFrames（单独类型调查已保留，不作为这条链的字段）。所有读取/copy/编码/后续decode必须独立资格。两次编码正常及两次正常decode不能证明crypto key稳定或roundtrip，更不能把单次写入参数作为实际更新后的费用。

CdMul普通priority getter85325固定返回501；此单个返回值不证明当前已激活列表的顺序、基类Add队列、Relic预处理与Rune预处理的合并顺序或全部叠加规则。每次调用都各自取整并编码；不能直接替换为`round(baseCost×全部乘积+全部和)`。下一步骤必须读自己正常decoded成本快照，而不能自动继承前一步encoding argument。

## Round及Single安全资格

调用地址0x18059e290为**unmapped raw helper**；未证明其metadata方法身份。UnityEngine.CoreModule.dll真实Mathf.RoundToInt282369位于0x186b4c250，代码表已纯文件重映射，两个地址不能互称。

raw helper59条及85835 inline：有限输入Single精确升Double；对±0.5 fractional部分分支检查整数奇偶，奇数向远离零补1，偶数保留；其余用已封存modf0x1804d57f0/floor0x1804d3200/ceil0x1804d58c0。最终CVTTSD2SI32。**有限且Int32转换有效域的结果是half-to-even**，无cost>=0 clamp。

此前的CVTDQ2PS/MULSS/ADDSS受实际MXCSR RC影响；普通native=true不证明RC默认nearest、FTZ/DAZ或异常掩码。[Intel原手册](https://cdrdv2-public.intel.com/843827/253665-sdm-vol-1-dec-24.pdf)4.8.4/10.2.3及AppendixD已查原件（本机PDF SHA2df6ae80aad83945c4879ef702b863ccbacaf5467e5ea079f1d7261e69ebc315）。正式首版可只闭合可精确Single表示的Int32及有限normal/zero Single操作；不精确操作可以保留两相邻Single边界，当所有允许结果的最后整数round相同才给独立整数reference，否则unknown。子正规数/NaN/Infinity/overflow/超Int32有效转换域继续unknown。

必要条件反例：cost10、Single coef bits0x3d4ccccd。MULSS nearest可得0.5并round0，round-up可得下一个Single并round1；没有游戏MXCSR原证，不能默认0。cost16777217在Int32→Single阶段也受RC，不能当精确整数。条件例不证明当前游戏配置。

## 数据初始化四槽：不等于完整恢复状态

SpData.get_inited32850普通分支只判断m_incrementsForAllSpTypes(+0x78)非null；不检查数组长度或四个值。Init32852普通path在该getter为true时早return。false时请求new Single[4]并赋字段，然后四轮分别进行独立BB尝试与mask/array观察。

found=true：读取当轮mask，BTS slot bit1/2/4/8并写mask，**这项写在当轮数组null/length/slot写之前**。found=false或BB不存在：独立当前mask有bit时复制protected increment24bytes并读独立Single decode；无bit则原常量Single1.0。每个slot独立重读数组receiver/null/length再写，不能从一次分配推全部写在同一数组。

SpType枚举0/1/2/4/6/7已绑定；SpType bit8无命名。另Init key helper的源usage和metadata已确证使用**SpTypeIndex**：0 TIME、1 ATTACK、2 DAMAGE、3 NEVER_USE、E_NUM4。slot3只可标NEVER_USE索引，不能宣称一种新恢复渠道。实际key helper185efd730仍含动态ToString/缓存/回调，四个真实BB key尚未闭合，依然保留unknown。

SkillData.InitIfNot32863先取首次duration，再于0x18252a587直接置m_inited=true，之后进行Single GE/独立BB Assign及SpData.Init。后段失败不能回滚此已证前缀；Assign使用另一次duration和BB读取；传给SpData.Init的是又一次BB读取。不得把277的FP EPS42950套到这个Single GE。

## 实质交付建议及边界

建议278闭合一组“技能数据成本转换与已写前缀”：三种Single cost变换、signed32行为倍率/直接费用更新、四槽初始化已写mask/数组记录，输入按独立typed read点与normal/存在三态处理。相互接续实际已证成本更新/仅cost刷新边界，实际时钟或完整技能周期仍unknown。公共例应同时含half-even、两步各取整与独立decode差异、RC不确定例、MIN32 low32乘法、mask先写后array失败/中途数组替换/flag先写后失败。

实际激活列表、BB值、hotfix、derived实例、保护值payload、crypto keys、修改后真实费用/当前SP/完整技能周期均未知。不能给任何未证明字段设置默认资格，更不能为此准备增加正式节数。

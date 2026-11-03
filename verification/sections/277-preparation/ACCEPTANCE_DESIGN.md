# 277 独立验收设计（尚未执行，不计完成）

已读取 `.cache/research/p2-skill-sp-lifecycle-277/SOURCE_GATE.md`、`SCHEMA_PLAN.md` 和原get_spEnough/ReduceSp/GE/NewSp/TSMath.Abs/FP.Abs汇编。最终API schema与source-proof gate尚待负责人封闭；下面先记录不耦合实现的判定合同，实际输入字段待确认后才冻结。全部工作限此cache目录，不改production/tests，不读游戏内存、不操作游戏/聊天。

## 验收的判断依据

* 原get_spEnough先检查raw owner对应的Unity对象null/equality结果。它不是Entity.alive。此raw读点与后续get_owner/Entity.SP独立。
* first_min<0才查询free-cast，false才走SP和decoded SkillData.spCost。first_min>=0跳过free/dataCost，先SP，后second_min。first与second不可复用。
* GE是signed SP > wrap64(threshold*4294967296−42950)，恰等于下边界为false；不写>=，不比较host float SP。
* ReduceSp传入delta独立于min阈值、dataCost、充能容量或上一getter值。delta0/free-cast true/virtual skip true各有短路，返回true仍不证明支付成功或技能成功。
* 有效扣费路径signed32 NEG后转FP；负delta可能提出ADD，MIN32仍MIN32再变MIN64，Abs特判9223372036854775806。只报告已证NewSp ctor参数与Apply意图；不解码返回Modifier，不推实际SP改变。
* 未来调用取决于unknown分支时called=null；已证早退后的调用才false。异常、未知normal和独立返回bool均分开。

## 最小必要验收组

1. 修改参数：正常write最小阈值5、负阈值−1、MIN32/MAX32原样；free-cast true/false；未知ordinary/hotfix与store异常保持unknown；不能以state写入值代替后续显式read。
2. 门槛：same input三点strict EPS（below/equal/above）；门槛0负SP边界；second_min MIN32的减EPS回绕；first5但second20、first0但second−1、first负值但dataCost7； >=0时free=true/dataCost20不影响其分支。
3. 读点：raw Unity owner invalid早退；first_min未知、free未知、SP正常资格未知、second_min正常资格未知、decodedCost unknown；未来called=null与已知未调用false分别核验；get_owner null/normal false不借raw owner。
4. 扣费：delta0、独立free true、virtual skip true三个短路；delta20（MINUS20Q）、delta−1（ADD Q）、MIN32（MINUS/MAX−1）、MAX32；只以源定义枚举SP=1、ADD=1、MINUS=2比较，不凭字段名猜作用。
5. 请求链：NewSp正常/异常/未知，136byte复制正常/异常/未知，Apply receiver独立null/normal/身份未知，Apply boolfalse/true/null和normal分别测试；normaltrue、early returntrue、Apply true都保持actual_cost_paid/actual_owner_sp_after/actual_cast_success/complete_cycle=null。
6. 组内不关联：modify_min5、admission SP5（dataCost20跳过）与reduce delta20并列；后者free读值不能借前者true/false。减费请求本身不引用274自然恢复或276初始解码乘积。
7. 输入边界：Int32/FP拒绝bool、float、越界；typed tri拒绝0/1或文本；唯一read/action id与exact keys；禁止alive或maxCharge替代所需读点；source guard漂移只能未知，不产生新数值。
8. 纯度：同input两次调用与深copy相等；不改变caller/state/read快照；public example仅声明输入，不覆写实际情景或run memory。

## 独立字面量算术（signed整数，非核心输出golden）

|门槛Int32|FP门槛raw|signed比较下边界raw|
|---|---:|---:|
|0|0|−42950|
|5|21474836480|21474793530|
|20|85899345920|85899302970|
|−1|−4294967296|−4295010246|
|MIN32|−9223372036854775808|9223372036854732858|
|MAX32|9223372032559808512|9223372032559765562|

门槛5下，SPraw21474793529/21474793530/21474793531对应false/false/true。
门槛0下，SPraw−42951/−42950/−42949对应false/false/true。
second_min MIN32下，SPraw9223372036854732858为false，9223372036854732859为true；普通negative SP仍false。

delta20：NEG Int32−20，FPraw−85899345920，NewSp MINUS(2)，magnitude85899345920。
delta−1：NEG Int32+1，FPraw4294967296，NewSp ADD(1)，magnitude4294967296。
deltaMIN32：NEG仍−2147483648，FPraw−9223372036854775808，NewSp MINUS(2)，magnitude9223372036854775806。
deltaMAX32：NEG−2147483647，FPraw−9223372032559808512，NewSp MINUS(2)，magnitude9223372032559808512。

## 最终schema需要解决的歧义

* OwnerRead normal=true + identity=null究竟known null pointer还是身份未知？身份未知而已确认非空必须可单独表达，不能凭缺label推null。
* admission应区分raw owner/Unity comparison和后续get_owner（以及其null访问资格）；现建议仅一个owner_read不能完整描述两者变更。
* NewSp source/target owner与Apply receiver必须两个不同读点；存在性、getter正常性、payload的normal/完整copy均独立。Apply Boolean不是公开的setter写入结果。
* `source-proof-preparation-277.json`、FP.cctor MAX与Int32ToFP/EPS原字节尚须最终封闭；此设计不把准备说明当已执行验收。

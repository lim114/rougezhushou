#277缓存准备：技力门槛与扣费意图

这份草案不计正式277完成。主API仅接受payload，不允许外部覆盖source_valid。源码SHA绑定的独立读取按普通native分支复现门槛、参数写入和扣费请求前缀。

门槛覆盖不等于扣费：public.override的SP5/门槛5得到true，但public.debit20提出20Q的MINUS参数，正常Apply返回false。public.changed_second首次读5、第二次读7，必须使用后一次，结果false。public.free_admission的free=true不复用于后续ReduceSp。public.min32演示NEG signed32最小值仍为最小值，Abs(MIN64)饱和值是9223372036854775806。

代数边界：SP>wrap64(thresholdQ−42950)为严格比较，等于右边界为false。原DLL/metadata、方法行、返回参数native type、字段偏移、压缩枚举默认值、全部纳入的指令/RIP字节均已文件核验；没有执行DLL、读游戏内存、模拟游戏接口、付款或setter效果。

独立资格：hotfix/virtual当前目标、decoded dataCost、两次门槛读、两次owner、调用/复制是否正常分别声明。NewSp返回opaque136字节Modifier，即使Apply返回true也不推实际SP变化或支付成功。未知分支的未来called=null；仅源支路证明跳过时called=false。实际SP、真实支付、技能施放成功和完整周期始终null。

ApplyModifier66665返回Boolean并接收Modifier/force:Boolean；ReduceSp传false。NewSp没有公开cancel mask参数；ctor callbacks以及Apply内部jump-table/effects尚不闭合，不建模其实际状态。

source-proof.json保留所有49方法4825条独立指令6859处fresh byte spans与来源哈希。source_manifest.json与该证明分别由core常量SHA绑定。公共例和回执仅含公开声明输入，不能代替实机算例。

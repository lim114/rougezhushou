# 技力初始化与控制器生命周期：第276节来源与适用范围

本目录绑定技力初始化与数据切换的局外声明参考。验收回执独立列明实际执行范围；来源文件不能替代本局观察。原始47方法提取证据保持原字节，公共副本保留全部方法、CFG、物理偏移、指令/元数据原始字节及身份绑定。提取工具的缓存路径仅为准备来源记录，运行时不依赖这些路径。数据仅从原文件读取，不执行游戏DLL，不读取游戏进程内存。

主证原件：GameAssembly.dll SHA `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`；global-metadata.dat SHA `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。来源不是社区估计或其他技能的相邻规则。原准备证明SHA `e1653b6e4bd3f737339f8d34b962615c6ee1760f725f4d74cb2e087f16b2d139`。完整范围47方法、4866条独立指令、6351个原始字节片段；另独立继承274已经公开绑定的TSMath.Max220529原22条指令。本批重新读取全部原文件并逐片段核对，6373片段无缺省成功。

## 来源成立的能力

- SpData.get_maxSp32849先解码spCost，再解码maxChargeTime，`imul`低32位并编码Int32；调用方分别声明正常解码值后，可计算有符号32位回绕乘积，结果仅为编码前参数；Entity使用的容量必须由另一次独立max_decode_read提供。它不自动解码游戏的受保护值，也不对cost作正数限制或饱和截断。
- Entity.Init66624仅建模SP相关前缀：第一次独立上限、独立initSp、signed min、`CVTDQ2PS`、System.Single编码器220443、40字节(16/16/8)复制；随后第二次独立上限、Entity.set_maxSp66442直接Int32写入，再进入独立控制器Reset。第一次上限限制初始候选，第二次上限供容量写入，不能重复使用一次读取。
- 初始字段复制绕过275公共setter，未出现alive/force条件和零下限。负初始值不截零。Single只能在整数可精确表示且乘Q后处于signed64域时给出精确构造参数；16777217、MAX32等不精确输入缺实际MXCSR，保留未知，不能默认最近偶数为游戏规则。准确的构造参数及复制调用仍不证明实际解码后技力。
- SpController66753只证明增量数组分配、默认PrecisePeriodicTimer25983构造与赋引用等正常前缀。默认计时器是0/0，与MarkInvalid25976的−Q/−Q不同；不从分配推断owner、type、cost或数组值为零。可选构造后hotfix的效果未知；结果止于已完成的前缀，不能宣称回调后的状态。
- Reset66745先写owner，后检查data，依次写type/cost不透明20字节段、复制增量，再读独立canRecover和第二次rate。Array.Copy失败/未知不产生已知部分元素；owner/type/cost的已完成前缀单独保留。
- UpdateSpData66747先复制cost；onlyUpdateSpCost=true直接返回，不读type/增量/owner/rate/timer。全量更新再读资格与独立第二rate，调用KeepPast；此方法不进行274的OnTick(0)补发。Entity.UpdateSpData66606则在控制器cost-only之前依旧读取并写maxSp。

## 必须保持的重置差异

原Periodic.Reset25973@0x181e04750先取FP.Zero，在0x181e047d5调用TSMath.Max220529@0x1866ff750，然后写P。TSMath.Max在0x1866ff794作signed比较，0x1866ff797为jg。`waitFirstPeriod=true`随后直接写R=P。因此Reset(newP,true)是P=max(0,newP)、R=P；第二次rate为0时除法参数结果−Q，但Reset实际参考写值为0/0，不能当作MarkInvalid。

Reset(bool true)25972@0x181e04840直接R=当前P，包括0/负数，不增加validity判断。ResetButKeepPastTime25974@0x181e044e0则P=newP原值、R=max(0,newP−(oldP−oldR))，减法使用来源绑定的signed64回绕；该方法没有old-invalid/restart分支，不对P截零。

严格绑定修后274核心SHA `c19124aaaddf04774ae54c193c4bd0cd49199ad1a90eba3883d1d29b4226084f`、275setter SHA `1f489e8078e12825ca9c6ef37b6b40a91303e63df9aaf2308bf5c3739638ba52`和既证FP运算SHA `e2f7e5ec412248f2e62a58333936c0c8e2d50536a443a095ccb77e54fc098f19`。复用的是有证非溢出域FP除法/加减代码；没有通过读取实际属性、热修复状态或受保护内存获得参数。

## 严格声明与结果边界

API合同见SCHEMA.md。每个pointer存在、正常读取、编码/复制完成、独立读点身份和普通native路径都需分开声明；ordinary=true不能替代未知的实例/复制资格。false和null不同。已完成前缀、当前尝试调用、未知/失败后的后态均分开，不能把未知改为一次正常返回。

`public_example()`包含4项：默认构造0/0；first20/init30/second21；cost-only先写容量27并保留计时器；独立first20/init−5/second15，其编码构造参数为−21474836480。两次Entity.Init皆使用独立Reset第二rate4Q，P/R=1073741824。示例是公开字面量，不是本局观察。

`natural_clock_link()`仅生成分开的274严格声明请求，不执行时钟，不覆盖现有274/275请求、读取快照或本局记忆。当前真实技力、属性、热修复等价、完整初始化和首次/施放/回转周期始终未知；Entity.Init后续虚调用、Character/BasicSkill初始化与Modifier效果尚未闭合。不能以该前缀输出完整周期总量。

## 验收边界

允许提升的内容为276核心、source manifest、公共proof/README和必要独立测试；依赖副本仅用于缓存准备，正式项目保留真实已经修复的274/275文件。准备测试使用隔离的Python包根，不调用DLL，不创建Qt窗口。窗口脚本只在主代理完成正式query/UI接入后用临时状态运行；实际窗口结果以verification/sections/276-window.json为准；未执行范围不计原Windows/game/chat/private样本通过。实际source guard需要明确提供原件文件路径；原件不可得时按unavailable/unknown记录，不能沿用历史回执冒充新核验。

## 受保护整数边界补证

protected-integer-proof.json额外保留11完整CFG、305独立指令和452新原字节span。构造器保存static K1，Encrypt再独立读取K2；Decrypt使用非零K1或重新读取fallback K3。SetNewCryptoKey允许写入静态键，因此正常调用不保证读键相同。五个条件位向量例仅为源代数参考，不是游戏执行/真实键。容量乘积与独立解码值分开，不推保护态相等，也不把编码参数0自动解码为0。详见PROTECTED_INTEGER_BOUNDARY.md；原47范围与6373片段回执不将这11方法重计。

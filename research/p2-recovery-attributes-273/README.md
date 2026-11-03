# 第273节：常态回复属性13/19的FP缓存与重算

候选本机原件的DLL SHA256为583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5，metadata SHA256为d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f。source-proof.json保存34方法、2945条唯一可达指令、4836个原字节span的完整准备束；本节已重新核对其20份来源文件、原件完整SHA和每条原生/元数据字节。仅纯文件读取，不执行DLL，不读取进程内存，不证明当前实例、热更新或服务器等价。准备束内的本机cache路径是保留的来源追溯记录，运行时仅依赖manifest绑定的公开原件。

GetValue先检查dirty。未脏时只读取独立解码缓存，不执行Calculate；脏时按登记顺序枚举修饰器。聚合起值为ADD=0、MULT=ONE、FINALADD=0、FINALSCALER=ONE；GetValue正常返回true的修饰器前三桶相加，第四桶相乘，false则跳过。单个buff缓存的倍率增量起值为0，与属性聚合的MULT起值ONE不同。枚举正常结束后才清脏，随后读取raw与范围、解码、求值及写缓存；原生公式为((raw+ADD)*max(0,MULT)+FINALADD)*FINALSCALER，随后max(min(value,upper),lower)。加乘按signed64 FP回绕。动态反转范围遵循该顺序，不改成另一种Clamp或拒绝输入；未知上界且value<=已知lower时仍可闭合到lower，但不得跳过任何正常读取资格。

元数据默认范围：13为[0,9223372036854775806]，19为[0,ONE]；前者是FP.MaxValue而非signed64最大值。动态范围覆盖独立声明。清脏之前的枚举失败不声明已清脏；raw/range/store阶段失败保留已发生的清脏前缀。未调用getter与跳过成员分别记录。库存未全时只显示已列四桶和已列preClamp，不把它们当完整值或下界；固定/反转范围在满足读取资格时仍可闭合常量。未脏缓存编解码不在本节闭合，缓存写参数不能直接当成下一次解码值。getter/Calculate不产生MarkDirty回调。

三花legacy_81/82/83原buff1作用属性13、buff2作用属性19，均为MULTIPLIER，loadBB=true、default=0、fetchBaseFromSource=false。TryGetFP对Single做FP转换；只有正常返回且numberFound=false才使用default0，读取异常不回退。成功取得0或负值不会改成ONE。signed32 stack_count先转FP再乘。0.2f/0.3f/0.4f分别得到858993472、1288490240、1717986944，合计属性MULT原值8160437952。这是属性增量累加；与271治疗逐包模块的独立连乘是不同通道，不能互相代用。

公开独立算例的raw13=10*ONE、raw19=ONE/16及三花各一层得到81604379520和510027372。两个各自有身份与资格的getter读点分别供272 canRecover和period读取；独立maxHP=100*ONE时两次回复率均132607116720。相同数值不能证明实际两次正常读取，更不能重复绑定同一读点。桥接不覆盖已有272快照。

本节只交付独立声明范围的参考计算与中文测试查询。实际库存、附着、缓存、脏标、当前属性、时钟、最终HP及完整治疗保持未知，不采集或操作游戏，不发送聊天。原始源码、真实反例、修正前后结果及失败测试保留在verification/sections/273-*。早期注入独立合同的审查与后续真实manifest绑定审查明确分开，前者不冒称运行时来源验收。

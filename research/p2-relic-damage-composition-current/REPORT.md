# 固定藏品同类伤害组合：隔离候选

本研究可交付一个实际功能组：关闭七低星补充面板中有原件支持的同类承伤藏品组合未知，并接入阿猛与冰中火的元素伤害独立连乘。它不闭合所有最终伤害来源，也不是实战校准。

## 交付与校验

- `relic-damage-composition.patch`：17文件，包含9条固定来源的生成元数据、限定组合器、现有核心/补充计算接入、中文说明、11项新测试及精选原件。源码只在draft，未修改共享tracked。
- `draft-validation.json`：150相关检查，149通过、1历史skip；最终17直接检查通过；87技能无藏品默认结果整结构相同。9条数据仅新增组合证据/组合方式和元素组合状态，不改数值或其他藏品。
- `public/independent-verification.json`：当前28精选方法、4099条独立指令字节、477项metadata/codegen/MethodSpec/字段/常量绑定，以及原生预制体与模板bundle哈希均一致。
- 当前`git apply --ignore-space-change --check`通过。使用`--ignore-space-change`是当前CRLF/LF差异；不是为了接受内容冲突。根代理随后有同文件改动时需重新check并局部集成。
- 没有真实窗口、游戏、当前热更新或聊天测试，没有操作游戏、读取私人状态、发送聊天、commit或计节。

## 错误前提已撤回

最初怀疑“法伤三件+断杖-波纹”核心默认全部加算。检查产品scope后确认波纹的`deployed_casters`已经属于战斗条件说明，当前不会进入数值。此项不是当前用户数值错误，不恢复输入/效果、不计功能。实际有缺口的是补充计算把两件同类承伤都标未知，以及元素两件组合被旧未核验保护过滤。

`get_relicType`的RIP是类TypeInfo，不是原始藏品键字符串。来源映射改为明确验证cctor的StringLiteral、静态字段0x30/0x40、Register<GBuffNormal/GBuffStackBaseOne>的MethodSpec与0x184599e10共享泛型callee。注册Add和创建TryGetValue均实际为Dictionary<string,Type>；普通GetTypeFromHandle、ToLower、Activator.CreateInstance也核对metadata/codegen目标，而非猜类名。

## 真实原件链

本机DLL SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`；metadata `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`；基包 `26-09-13-15-28-10-30688348`。源文件全部只读，DLL未加载/执行。固定原始rogue6参数绑定commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。

1. 原始`global_buff_stack_base_one`精确映射GBuffStackBaseOne。Preprocess 0x180d12270，按完整prefabKey找已有GlobalBuffData；既有分支0x180d12501调用AddBlackboardBaseOneStrictly 0x18231d460。数值同键用`addss`后`subss 1.0`，结果是old+new−1，再以一个合并后的黑板/实例执行。并非两次独立伤害乘算。
2. 锈蚀刀片/赶车夫的长鞭/复仇者都是同phy key：参数参考1+0.15+0.25+0.35=1.75。制式防暴用具/皇帝的收藏/璀璨悲泣都是同mag key：1+0.2+0.3+0.4=1.9。文明的存续pure2.5保持其单件类型，不能与phy/mag混合。
3. 阿猛、冰中火伤害部分原始均是`global_buff_normal`、`enemy_take_element_damage_up[fix]`，分别index0/index1、damage_scale2和1.75。GBuffNormal预处理复制黑板后分别append。实际GlobalBuff全局去重字段`_key`为空（并非LevelData.prefabKey为空）、子buff disableOverride=1，GetOverrideKey返回空而NewBuff直接启用，相同子key不会覆盖成一个。
4. 原模板event10明确ON_TAKE_DAMAGE。DamageScale 0x181052b10的实际flags为mask过滤、非OneMinus、非Stackable、非ValidStackCnt。匹配类型后取当前Modifier.value和自身damage_scale，FP乘法后set_value。BuffContainer.OnTakeDamage依次传递更新后的Modifier，因此两独立normal来源参数层2×1.75=3.5。
5. Battle.DamageType为PHYSICAL1/MAGICAL2/PURE3/HEAL4/ELEMENT5，mask2/4/8/16/32。实际IndexBelongToBinaryMask做1<<index后mask检验。三个普通类型和元素互不借用倍率，HEAL/损伤积累不是此元素生命伤害mask。

精确语义和绑定保存在public，不依赖参数名字相同的推测。198已有正常GBuff/覆盖创建链被复用，新增需要的base-one、DamageScale、事件循环与注册/类型链单独核对。

## 功能与边界

- 七低星补充路径从“同类>1件未知”改为仅对白名单已证来源做参数合并，保留未知来源反例；参照已有目标防御/保底/法抗处理后应用。报告明确是参数算术参考，非实战全技能总量。
- 核心hit仅在阿猛/冰中火精确组合时使用3.5。冰中火原有损伤积累1.75仍独立处理；不改变其他伤害类型、治疗、资源回转或无藏品默认。
- 同ID去重、逆序结果、零值手动效果、伪造proof markers均覆盖。手填非零元素承伤和二者混合时没有来源层证据：双藏品部分退出计算，保留既有明确手动参数小计并将出现元素伤害的正值完整量/DPS保守标未知；没有元素输出/零输出不由此变未知。此保护不会自动解释手填参数的真实来源。
- 不恢复波纹/部署术师数量或其他已降为战斗说明的藏品，不新增事件输入/预算包装。
- base-one原生按float32累加并减1，获取顺序可能影响最后几个二进制位。显示1.9等是原始参数算术，未宣称bit精确FP或实际packet取整。元素2与1.75在该乘法层可精确二进制表达，但实际前后伤害取整仍不由此闭合。
- 当前XLua/热更新、实际附着/覆盖时机、获得顺序、目标状态及其他天赋/敌方/手动/未来来源组合仍未知。不要把这个组当作所有P2最终伤害项完成。

## 公开查阅

[锈蚀刀片](https://prts.wiki/w/锈蚀刀片)与[阿猛](https://prts.wiki/w/阿猛)描述吻合单件原始参数；[拟造物质编目](https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目)记录冰中火元素损伤和元素伤害75%。这些页面只作描述对照，不作为组合或实机算例依据。未取得条件匹配的公开完整成对算例。

## 集成建议

根代理串行`git apply --ignore-space-change --check .cache/batch209-400/review/final-factor/relic-damage-composition.patch`后集成，必要时只应用局部hunk与新的研究目录。运行本候选17项检查，沿根代理当前功能节的其余必要验证/到期全量。进度销项范围只写“七低星固定同类承伤组合及阿猛+冰中火参数层”；其他最终伤害组合保留未知。候选不带索引、节数、私人文件或commit，均由root决定。

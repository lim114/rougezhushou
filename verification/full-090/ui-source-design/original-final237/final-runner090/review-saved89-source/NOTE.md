此包只定义 actual90 源码对五份公开临时状态的界面消费合同，0 constructor、
apply、产品/helper/API、formatter、tests、Qt/Wine。固定源码commit5e2ff697。
当前源码字节与该commit逐件相同。没有运行MainWindow或pending runner独审；
source080仍负责唯一正式审查。

这里的五份状态是patched作者newtests的saved38中的sequence19、9、3、22、6
之后状态，不是最初unpatched source89 case1–5。它们的完整native状态和输入
树逐份绑定到原gzip记录；未重跑原38或source5。原来源是公开RunState临时
测试输入，不是原生OCR或游戏观察。

训练开关False时，current_operator_state直接返回显式隔离account字典。True
时先取本局member；member不存在或present为假也返回account。有效member
过滤invalid_fields后覆盖account.fields，但skill_ranks只保留过滤后的本局
ranks，不继承account ranks。过滤是key字面相等，不是重新验证培养值。
此五份的invalid_fields/invalid_skill_ranks均为空，故只能声明源码规则，
不能把它们算作已执行的invalid过滤分支。operator_summary另外以str(key)
过滤invalid_skill_ranks；在这里空列表/空runranks不会产生差异。

按UI代理提供的account E2/L60/trust100/P1/moduleNone/module_level0、ranks1–3
均10，以及每state先reset override/正常update_operator：False十表中的五行
均使用account，Mechanist S1 rank10。True的19/9使用run E0/L1/trust100，3/6
使用run E0/L2/trust25；它们run ranks为空，故rank7且标未确认预览。22的
Mechanist已离队，True也回account E2/L60/rank10。E0只开放S1，E2开放S1–3，
Mechanist默认选择S1。Myrtle account的第三rank只是fixture元数据，不会产生
Myrtle第三技能，本组只观察Mechanist培养/技能与两人roster。

有效run中只有原字段elite/level或加trust进入run_confirmed_fields。缺少的
trust/potential/module仍由account提供；相应界面加账号参考、本局未确认标记。
不从sources={}虚构培养来源receipt。模块None只说明当前参数未计模组；不
推实际装备状态、数值效果或原生未知机制。表的account_fixture是来源分类，
不是新scope值：fallback按原account字典原样返回，scope保持其显式输入。

recruited_operator_ids完全独立于训练开关及crew_count，按profile存在、present
truthy、scope不是account筛选。19→两人，9→仅Mechanist，3→两人，22→空，
6→仅Mechanist。sequence9根本没有Myrtle key；表中None是“缺失owner”的
投影sentinel，不能称原present=None/False，也不能写回原状态。额外key存在
表明确这一点。

所有selected stored crew都是int2/1/2/0/1，None observed仍保留int2，不是
stored人数未知。run_state.summary只在stored None显示未确认，否则str，
不校验或修复历史bool人数。现有summary人数行按原present flags计数；它不
向training_conditions提供精英、技能或等级。不能从人数推培养或伤害数值。

技能、elite/module字段的读取过滤与技能combo开放条件是两个来源步骤。
operator_summary的selected_skill还要求type is int与索引范围；当前saved
fields没有selected_skill，combo的S1来自默认，不能冒称已读取所选技能。
skill_rank_value先str键再int键，无本局rank时按当前elite回退7或10。

未来把完整状态deepcopy到existing window.run.state只验证窗口consumer，
不能冒称重新通过constructor/apply/落盘pipeline或原生观察。bootstrap已有
构造必须单列实际计数。update_operator仍会走845/846/847及998的属性/helper
和可能多次calculate路径；只读窗口阶段是否额外调用API须由实际observer
记录，不能套用本审0call数字或按10state推10API。没有运行pending runner。

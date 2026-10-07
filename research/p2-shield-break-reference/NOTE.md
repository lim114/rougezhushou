第 53 节：机械师 S2 破屏条件来源

所有改动位于外部持久 snapshot，根代理独占 tracked。基线冻结于 fba536e118906f58ed2bcef359480f76e0ae4d67（51）；baseline-freeze.json 记录现有源文件哈希。当前 root 的后续改动不能被此 snapshot 覆盖。section53.patch 只包含列出的 6 个文件；research 可单独复制，scripts/verify_cloud.py 的一行 runner 登记由根代理合入。

固定来源

复用并重新校验 ArknightsGameData a550f5e048bb94e7cdefc6eb97a4091f0c4c7add 的 character/skill 原表：char_4230_mcnist.skills[1] 指向 skchr_mcnist_2；全部十级原描述与 blackboard 保存在 source-receipt.json。rank10 atk=1.5、atk_scale=2、trigger_time=8，技能类型 AMMO、duration=-1、可手动停止。原表支持屏障摧毁时的条件法伤以及弹药参数，不提供实际破屏/爆炸命中时刻、双方归属、双方耗弹映射、原生破屏/耗弹/再次获屏/结束顺序或当前客户端获取。GUI 原 tooltip 已把总次数称为条件估算，且明确不自动推断弹药消耗；未变 GUI 标签或选项。

公开结果闭合

base_attack=1000、rank10、shield_break_count=1：原实现观察窗0仍给5000法伤且 complete=True；现在明确窗0实际0，独立条件5000仍可审阅。正窗口或未指定窗口实际破屏伤害未知，不把输入次数放到任意事件帧。count2 + 手动结束20秒：原单次技能50000/周期91000；现在实际聚合未知，已计普通攻击小计40000/81000，条件爆炸10000独立保留。SP和手动结束参数不变，但手动结束参数不等于已核验实际耗尽时刻。显式短窗口沿用原0普通攻击小计，不新增普通攻击时钟。全技能 aggregate total/phase/cycle/window 和 DPS 都沿 legacy → estimate → finisher → relics.finish → report 入口检查。

父代理的独立初审指出原始值 ==0 漏数字字符串 '0'。已改为显式 window key + estimate 中已验证归一化秒值；敌生命周期沿现有 finite 归一化。只指定 window0 才排除，未提供 window 且未知 duration 导致显示0秒并不证明实际空窗。字符串 enemy0 + 手动结束的 total/phase/cycle/DPS 也归零。空本体射程/阻塞不能排除独立结构性原理爆炸。根代理最后补查发现旧 result.scope 仍称“仅实际屏障破碎”，且继承至 estimate.scenario_scope 与报告。helper 已同步两字段为“声明总破屏次数的法术爆炸条件参考，事件时刻未知；已计普通攻击仅为手动结束参数参考。”；两模式的零/正计数报告及794条 public report 均禁止旧实际破屏声明，伤害/SP/结束数值不因此变化。计数0保留原数值和组件；其技能实际结束及 native scope 仍未核验，因此 complete=False。条件组件不写 source_unit，以免把合计猜成单个来源归属。

验证与范围

15 新测试、89 相关回归全部通过。外部 snapshot 精选731项：730通过、1历史skip；selected-regression.log 是实际 runner 输出。成对 public-baseline.json/public-draft.json 共794场景、1588次真实 calculate_damage 调用；含12字符串零边界和8首伤藏品场景。166个零计数场景数值和组件保持，312个空窗/敌零实际0，316个正窗未定位实际unknown，308个手动结束普通攻击小计保持。新增54个 numeric float/decimal/scientific string 计数等值场景。两种 timing_mode、rank1/7/10、计数0/1/2/8/9、手动结束与否、窗口未给/0/1/10、敌零/空射程均覆盖。输入与 catalog 缓存哈希保持。public 首伤藏品 fight_1/fight_2 在当前 offline scope 仅作参考，未注入 first_damage 倍率；治疗藏品不改变爆炸法伤或普通攻击伤害。

55/57独立审阅发现新 helper int(raw) 漏旧入口接受的 "1.0"/"1e0"。已复用旧 _skill_damage_base 局部副本验证后的 float→int 语义，不扩 bool 资格或 charge_count。独立原始失败回执没有修改，相关摘录及原文件哈希在 independent-count-compatibility-finding.json。

一次精选728项执行因外部 snapshot 漏复制既有 Yato research receipt 出错；复制 unchanged 的公开 receipt 后已复跑成功，该 failure 记录于 validation.json。未重复同一 unresolved 问题三次。未执行 Wine/Qt UI/native Windows/当前游戏。根代理已独立完整审阅新版核心、14 tests 与旧断言变化，无当前阻断；主仓合入后的回归仍待执行。review-followup.json 明确区分根代理实际审阅与子代理后续只读审阅。

最终子代理独立审阅已对最后冻结 patch SHA 1e0993a11b6ca572de3ab748570341381abde30a1f4652f6e04cd2a69f43c173 签署，无阻断。32初次+20末次真实 public 调用、15新测试全部通过；independent-review.json、independent-scope-count-final-review.json 与实际 independent-final-tests.log 可审阅。旧review/hash完整保留在 independent-review-initial.json。根 scope 与55/57 count独立发现均有归因。未修改这些独立回执原文。

# Draft 045 — 两异格阿米娅开启来源与观察归属

只修改 `/tmp/p2-draft45`。原始复现基线是 `codex/p2-development` Section 040 提交 `9f49ea54a5f3f04553848523ce093e9e5e9f0cc6`；`base-receipt.json` 留存其生产源码哈希，源码与测试均复制冻结，不使用后续移动中的生产测试。`data` 和 `research` 仅用于公开资料读取。最终四个补丁文件只在/tmp重基父代理Section043提交 `e0774e8`；原40复现代码保留在 `baseline`，最终补丁比较的43原文件在 `baseline-043`，exact SHA及依赖文件在 `healing-043-base-receipt.json`。父代理仍继续后续节，不能用本目录完整旧文件覆盖后续生产改动；按 `draft.patch` 合并窄 hunks，再在最终生产 HEAD 验证。未修改生产 tracked 文件，也未调用网络、原生游戏或聊天。

## 原资料与变更前公开复现

原表 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。父代理正常 TLS HTTP200 获取原 manifest 所列 `char_patch_table.json`，48761 B，SHA256 `d1850d5aeec1a9246a0531e88c167e66745644957662c8272fc764f54904c57e`；本代理重新计算该文件 hash 与 pinned `skill_table.json` SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`，均匹配。保存于 `source-receipt.json`，保留 exact selectors 原值和 `/tmp/p2-audit/patch-operators/source-and-reproduction.json` 的出处。独立审阅计划在 `/tmp/p2-audit/after-040/amiya-phase-NOTE.md`。

- `char_patch_table.patchChars.char_1001_amiya2.skills[1].skillId = skchr_amiya2_2`，`skill_table.skchr_amiya2_2.levels[9]`：立即寻找前方生命最低目标，10斩，前9击法术2.2倍、最后一击4.4倍真实；斩击期间击倒 +40%攻击/+20法抗，最多3层，接下来的伤害变真实；战斗仅一次。原 duration35、自然SPcost20/init0。该字句不证明10次同在t0命中，也不证明斩击结束或后续相位。
- `char_patch_table.patchChars.char_1037_amiya3.skills[1].skillId = skchr_amiya3_2`，`skill_table.skchr_amiya3_2.levels[9]`：立刻范围一次2倍攻击，命中每敌 +30%攻击最多5层，接下来变真实且可攻2目标；战斗仅一次。原 duration32、自然SPcost20/init10。开启、命中加攻、派生治疗的实际链顺序仍未知。
- 原 patch E2 青色怒火7%技能加倍及诚挚期许HP8%/skill2.5%每秒回复原值也保存。前者保留既有培养/技能攻击参考，后者是独立自身生命回复，不随敌人0生命取消。

旧40公开 `window_seconds=0`：战术S2仍27588伤害（22572法术+5016真实）、医疗S2仍2000伤害/1000伤转疗。`public-baseline.json` 在任何draft源码变更后的首次公开回执中使用复制的未改40生产代码，重现同一问题；原36 cases已有父代理修改前生产回执。所有场景使用公开输入，无下划线私有参数。

## 窄实现与保持未知

1. `instant` 对显式 `window==0` 无来源。正窗口沿用 literal immediate 参数来源，不推断第一客户端帧；Sbell1已有自身零窗口保护继续通过。
2. 战术S2将9法术+1真实斩击改为无实际时间戳的条件来源，不生成10×t0。原名义35秒仅为原表技能持续参数；既有普通攻击参数算术保存为孤立参考，不称斩击结束后另有35秒。声明 kills0..3 仅沿用既有后续buff参数，不反算此前斩击或虚构逐击击倒先后。实际斩击结束、后续起点、完整输出和结束保持未知。
3. 医疗S2保留正窗口 literal单击2000及其1000伤转疗参数来源小计；后续原32秒算术留孤立条件参考，不称开启结束后另有32秒。开启/加攻/治疗实际chain order尚未核验。完整伤害、依赖完整伤害的直接治疗及完整结束保持未知。
4. 两S2的孤立参考使用原名义35/32参数，不随长观察扩长，也不从短观察或有限正生命周期下的参考0次推导实际后续0次。`source_possible` 在正观察/非零生命时使后续 actual未知，即使参考 hits0。原owner范围、打断、前摇及有限生命周期只在孤立参考内沿用，不能绑定未知实际相位；没有新增攻击脚本、概率、友方获取或真实相位。
5. `damage_healing` 在 after-modifier算术完成后检查父伤害actual；任一父伤害未知且ratio>0则完整actual healing未知。已知父来源按同ratio保存在 `known_healing_sources`，让1000 opening参数小计与完整14000条件疗量都可审阅，不声称完整实际治疗14000。`healing_targets=0` 的已知0不被未知伤害覆盖。
6. 父代理43负责既有 `known_healing_subtotals` 最终单因子治疗缩放；本45仅扩展其 `finish` 既有单一healing-factor分支，同步 `known_healing_sources` 的 total/per_hit/event_amounts 和医疗phase两份opening_healing_reference。活玫瑰同一已确认1.2倍率使opening条件源、已知小计、报告都1200，完整actual healing仍unknown；未知多因子叠加沿用未套用规则。
7. 医疗独立自回复仍保存原名义分项1327.104（default HP1658.88×2.5%×32），不进enemy取消集；用 `nominal_duration_reference_seconds` 与报告的条件参考/实际总回复未知明确结束尚未绑定。显式零窗口该分项0，enemy生命周期0仍保存正的原名义参考。
8. 战斗一次 `mode=once`、默认战术初动20/医疗初动10保留，完整recharge/end未知，cycle不适用。术师及两异格S1没有新增模型变更；医疗S1 enemy攻击触发AoE角色由40负责且本draft保持。

## 验证与限制

16项新 public unittest 与12个现有相关模块合计170 tests通过，见 `related-final.log`。包括两个模式的0/短正/长窗口、enemy0/有限正life.1、9/1原倍数、kills0..3验证、攻速不改单斩次数、once/initial、after-modifier伤转疗未知与1000小计、0受疗人数、独立自回复、报告与输入/返回reference隔离。

`public-baseline.json` 与 `public-draft.json` 各64个phase场景及12个S1保持场景，共152 public calls；`public-comparison.json` 记录0边界、全positive actual总伤unknown、初动/once保持、全部S1结果与40基线完全相同。64 phase包含父代理原36公开场景。未用新测试证明客户端机制。

初次检查中有一个新测试将 `damage_taken.value` 误当总倍率（既有API是加成），已按原API更正为 +30%/+70%；没有改变生产模型去满足测试。首次运行还误写不存在 `test_operator_clock` 名与遗漏 `/tmp` research公开fixture，已使用现有 `test_timing` 和公开research路径修正。独立静态审阅找到finite positive reference0不能证明actual0，新增窄保护与针对性public测试后相关170重跑通过。

本draft未执行全云/Wine/UI验证；由父代理最终合入后在每五节批次执行。原生Windows、游戏、桌面采样/聊天均未验证。来源仍缺斩击/开启的当前客户端脚本绑定、后续攻击交接、实际结束、治疗chain order、友方HP/邻接与受疗获取。P2仍未完成，不能由本节宣称全部完成。父代理43已完成全局已知治疗小计缩放，本45消费该规则并只扩展最终来源记录同步；四文件final patch基于已提交43，最终合入不得用完整旧源码覆盖父代理后续改动。

补充运行记录：最初仅将43的relics复制到40依赖集时，缺少41新增token_cost_reference导致import失败；随后只从同一已提交43复制公开依赖并将四patch文件重基43，未伪造/占位导入或改变测试断言来绕过。相关170完整重跑通过。最终public baseline继续使用未改40复制以保留修改前公开复现；draft是43参数规则加45窄变更。

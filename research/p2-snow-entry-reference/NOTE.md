# P2 section 038: 圣聆初雪观察窗口与积雪经过归属

固定 Kengxxiao/ArknightsGameData commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的 character_table 和 skill_table 已重新核验原始 SHA256/字节数。精确技能映射、三技能 level6/9、第一天赋所有阶段/潜能 selector 见 source-receipt.json。仅复用已有固定源，不重试 PRTS403/缺失 native DLL 或绕过代理/TLS。

资料明确 S1「立即」的 5.2×（rank10）/4.8×（rank7）法术伤害来源，并明确地面敌人经过积雪时的天赋伤害。原始第一天赋同时含 E1 .5/.55 与 E2 .75/.8；此前 after-035 只读审计文字说缓存止于 E1，与其自身 selector 和原文件不符，此处直接查原文件予以纠正。生产系数保持原值，不能用错误文字说明为未知机制辩护。

公开 API 复现显示 S1 window0 仍给5200伤害，window1/20 被 duration0 覆盖；manual snow_entries2 在 S1/S3 window0 仍出伤，并向 normal/recharge 再复制一次计数。外部来源的「经过立即」只表示在进入事件成立后即时结算，不证明进入发生在技能开启0秒；当前阶段攻击力也不证明进入时快照。修正保留人工计数的条件 per-hit/total，实际事件、窗口/施放/阶段/周期归属未知，不在 recharge 自动生成另一次计数。空本体攻击范围不证明空积雪场地，观察0或当前敌人0秒生命周期对它没有输出。

S1 显式观察0/1/20保留；立即伤害来源沿用既有参数参考，零观察不计伤。没有 source/native lifecycle 证据，原有0秒结束/12秒充能/12秒周期及5200周期参考另存 sbell_instant_reference.parameter_clock_reference，公共实际 duration/recharge/cycle 字段保持 unknown。不补前后摇或雪扩散时长、multi-charge消费时序。三个技能无entry默认 damage/attack 与既有参考时钟的6个公开算例逐项保留，S1时钟在明确的参数参考中。

S2 completed025 的雪地 DOT 覆盖/首跳未知逻辑继续保留；新 entry unknown 与 DOT unknown 共存，known_damage_subtotals 只含已保留本体来源，未复制/假定任何来源归属。S3 manual2 的当前阶段经过条件伤害3000不合入其114400本体参考或 recharge，完整总量与窗口伤害 unknown；没有entry时原114400/35+50=85秒参数参考不变。

新增11个公开 API 检查涵盖三技能、两种 timing mode、0/1/20、0当前目标生命周期、空owner range、manual2、E1/E2潜能与法抗、DOT与entry两个未知同时存在、默认数值及报告。68个新公开算例、历史 Sbell 复现和6个默认前后核对见 public-reproduction.json。Linux相关92项通过；精选562项运行、561通过、1历史skip。草案只在 /tmp；真实 Windows/game、当前热更新、实际 S1结束/阻回/多充能链、经过时刻/快照/雪的生命周期未验证。

# 麒麟R夜刀S2/S3 · 部署多段的条件来源与未知时钟

固定原始commit：`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。复用已有缓存与只读审计 `/tmp/p2-audit/after-030-instant/{NOTE.md,RESEARCH.md,source-and-reproduction.json}`，未重新请求已403的来源。该审计的读取HEAD早于第30节；本节只复用它的固定原表事实与公共复现，不把旧生产hash当作当前代码hash。

- [skill_table.json](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/skill_table.json)：11,447,929字节，SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。
- [character_table.json](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/character_table.json)：14,975,251字节，SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。
- `character_table.char_1029_yato2.skills[1].skillId=skchr_yato2_2`、`skills[2].skillId=skchr_yato2_3`；精确技能选择器为各技能 `levels[9]`，天赋为该角色 `talents`。两张原表在草稿验证时重新核hash与选择器，原始选定对象见本目录 `source-receipt.json`。

S2描述明确16次斩击；M3黑板 `atk_scale=1.5`、`talent_scale=3.75`，显示参数 `talent_scale_display=2.5` 不代替运算系数。精二第一天赋为每次攻击额外0.2倍法术，第二天赋为技能中及结束后10秒攻击+13%（相应潜能已有覆盖保持）。本节保持原逐击防御/法抗与天赋系数；base_attack1000、精二潜一、物防100/法抗50时条件总量仍32300，物理每击1595、天赋每击423.75。

S3描述明确基础突进2格、命中延长至最多5格；M3黑板 `atk_scale=3`、`min_dist=2`、`max_dist=5`、`dist_interval=0.2`、`dist_unit=0.3`。后两者是距离参数，不是时间间隔。公共 `dash_hits` 保持既有默认1及0..100整数边界；它只给指定碰撞次数的条件伤害参考。base_attack1000、无防御/法抗时指定3次参考仍12204；不按攻速推次数，不从距离生成时钟。

两技能原表为 `duration=-1`、`durationType=NONE`、部署被动触发；本地 timing-profiles 只含普通 Attack1 参考，技能绑定为空。部署初动0与不重复周期保持，但这些参数不证明技能在0秒结束。复用第28–30节的 `unbound_cast_reference` / `preserve_unplaced_sources`：明确窗口0或全局当前目标生命周期0产生实际伤害0，正窗口无实际时钟时伤害保持未知；16击/指定回旋次数的逐击与合计伤害另列条件参考。0/1/10秒观察窗口保持用户原值；无首伤、段间隔、碰撞或结束事件的虚构时间戳。完整持续、阶段与周期总伤未知。

本体 `target_windows=[]`、晚供靶或全程打断不证明周围斩击/突进路径的独立覆盖为空，也不证明取消规则；其条件来源继续保留，实际伤害未知。全局 `target_disappears_seconds=0` 则说明当前单一目标不存在，frames/continuous均实际0，即使正 `dash_hits` 仍只保留条件参考。S1完全不变。

仍缺少S2真实首伤/段间隔/重选范围，S3速度、离散步进、延长与同帧碰撞、物理与第一天赋顺序、当前热更新/动作/皮肤、施放移动/打断与真实结束证据；技能结束后10秒天赋的绝对起点同样未知。没有直接脚本或可绑定实际动作前不补数值。云端公共计算与报告回归不代表Windows实机、游戏采样或桌面聊天验证。

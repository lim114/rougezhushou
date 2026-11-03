# 第 115 节外部准确性算例：公开资料候选（Source-only）

本资料仅为第 115 节实际准确性检验准备独立外部输入和预期结果。没有执行项目、公开 API、测试、Qt/Wine、native 解码或 Git；没有改动仓库文件。Root 必须在实际第 115 节源码上执行核对，填写结果和判定。当前 `all_passed`、actual results 和 115 guard 均为 null。

获取日期：北京时间 2026-10-09。具体 UTC / Asia/Shanghai 获取时间、HTTP 结果和正文 SHA 在 `retrieval-ledger.json`、`accuracy-candidates.json`。

## 四个可用的已支持核心算例

| 外部算例 | 原网页输入与数值结果 | Source-only 项目入口建议 | 必须保留的限定 |
| --- | --- | --- | --- |
| 物理最低伤害 | ATK 500，DEF 约 800，物理伤害约 25 | `rouge.damage.calculate_damage`，维荻 S1 被动、显式 base_attack 500 / enemy_defense 800，读取 physical component.per_hit | 原文有约数；只核对给定名义输入，不证明原实战或 A 等级对应 800 |
| 法术减伤 | ATK 500，RES 约 50，法术伤害约 250 | 同入口，术师阿米娅 S1 R7、base_attack 500 / enemy_resistance 50，读取 magic component.per_hit | 阿米娅只是已支持的数值载体，不是 Wiki 示例指定干员；原文仍为约数 |
| 物理减防 | raw 1200 对同一约 800 DEF，明确举例伤害 400 | 同入口，维荻 S1、base_attack 1200 / enemy_defense 800，读取 physical component.per_hit | 原文 400 未加约号，但目标属性来自前段约数；名义输入的精确数值核对与原实战证据分开 |
| 阿米娅 S1 R7 攻击间隔 | 基础间隔 1.6 s，基础 ASPD 100，技能 +60；原式 `1.6/(160/100)=1 s` | 同入口，术师阿米娅 S1 R7、无其他攻速加成，读取 interval_seconds / attack_speed | TapTap 后文误写“7级二技能”；Wiki 与固定档案均证明 +60 是 S1 R7。保留原文并明确纠错，不核对首击、攻击次数或完整技力周期 |

前三例来源为 [Arknights Terra Wiki Damage / Tips](https://arknights.wiki.gg/wiki/Damage#Tips)，页面实际 revision 为 [759599](https://arknights.wiki.gg/wiki/Damage?oldid=759599)。原 HTML 74,651 B，SHA `5d9de73c8e03d6c2e7c230450aefe196bcda8aec54aad4eb4029ad251b455425`，位于 `wiki-mechanics.html`；完整可读正文 `wiki-mechanics.txt`；候选 JSON 保存完整原文引用。该站是社区 Wiki，不是官方。

攻速例来源为 [TapTap：手把手教你学会方舟伤害计算](https://www.taptap.cn/moment/152911449218355181)，九龙湖咸鱼，页面标注修改于 2021/06/19。HTML 464,512 B，SHA `82a7b2a545dd2d639a41745c77a44b40c4e13e09d6954520c0c99a5e1bc1b1e2`，位于 `taptap-damage-guide.html`；正文 `taptap-damage-guide.txt`。

阿米娅 S1 R7 +60 的独立支撑为 [Wiki Amiya](https://arknights.wiki.gg/wiki/Amiya)，revision 706848，HTML 270,618 B，SHA `b47fad92c2be0a8413006aba7578631e758a6f6b514f500080df48d036ff4c52`。固定 `catalog.json` 的 char_002_amiya S1 R7 values.attack_speed 为 60，阶段攻击间隔为 1.6。现有合法入口要求正确的 elite/rank；建议 E1 Level1、R7、Pot1、Trust0，显式输入不等于该干员真实培养攻击。载体技能不加攻击。维荻 S1 只改 HP / RES，不改变本体攻击，故可直接输入网页 raw 值，不需要逆算攻击倍率。

## 第五个条件候选：真实公开截图的阿米娅真伤

[IS Central Damage Calculations / True damage](https://is-central.github.io/general-knowledge/damage-calculations/#true-damage)，页面标注 Last updated Oct 8, 2026。HTML 163,333 B，SHA `3633f01923d739fb74f2c28303d4468c10dbade6388958497ff27ed51fe61a4d`。

原文给出术师阿米娅 S3，base ATK 715，外部 ATK +30%（科技）+30%（Rise and Fall）+8%（Screaming Cherry gamma），技能 +230%，Triple Kings +150%，Civilight Eterna 真伤 +150%；目标 Theresis 二阶段，2500 DEF、60 RES。页面写 `715 * 1.68 * 4.8 = 5765`、`5765 * 2.5 = 14,412`，并附原游戏截图。

本 Source 角色实际查看这两张公开原图：`iscentral-amiya-final-atk.png` 显示 Amiya Level50 / ATK5765；`iscentral-amiya-damage-output.png` 红字显示 14412。它们是作者已经公开的例图，不是本项目实际游戏验证，不是当前用户游戏截图。原图获取 URL、字节 SHA 在 retrieval-v9.json。该例有真实外部数值观测，而非我们自编公式期望。

**必须先独立 Source 审阅再由 Root 执行。** 原文展示值是整数和中间取整书写，不能把 5765 当作精确未取整浮点期望。项目已有 rune 整数写入层和战斗加算层，候选 JSON 提供完全声明的手动外部 +30/+30/+8 rune、内部 +150% 与 true damage_taken +150% 参数；仅可核对这些已支持的数值核心。该例是 IS5，当前自动 run context 固定 IS6；不得把手动数值输入描述为 IS5 自动科技/分队/藏品读取已通过，也不能在未提供相应参数时声称已验证 Theresis 90% 减伤、Framework 20% 减伤的穿透、完整 Boss 时序或整场输出。潜能、信赖、模组具体等级和首击相位在正文未给全；候选 base_attack=715 是原文直接给定，不假造其培养来源。该候选 `apply_ready=false`，不会自动进入执行名单。

## 来源问题与明确不使用的资料

- PRTS “伤害”与“伤害计算”各一次公开请求均 HTTP403，未绕过代理或反复重试。错误在原 retrieval-v1.json 和合并 ledger 中，不能声称读取了 PRTS 正文。
- Google 普通搜索给出 redirect / 不含可用结果，Bing 搜索只返回主题首页；DuckDuckGo 正常结果帮助找到 TapTap、IS Central。搜索摘要不能独立作为具体预期值证明。
- GamePress 两个历史猜测路径 404，Fandom 402，Reddit JSON 403；没有当成已读证据，也没有发送任何外部消息。
- Coolchulainn 的 Ray 数值示例非常明确（6196.9248 / 5791.03668），但当前固定项目 catalog 的 32 个干员未含 Ray，且该文后续伤害计算使用展示取整值。保留检索快照，未作为已支持干员用例通过，也未新增 Ray 机制。
- Wiki Attack interval 页 ASPD 一些百分比叠乘描述带 `?`，本次不使用这些不确定描述建立新的机制。
- Wiki Damage Tips 的 A rating / 约800 DEF 与当前独立 DEF rating 页等级区间存在差异。本次仅使用其明示 800 / 50 名义输入，不引入全局评级换算。
- TapTap 文章另有明显简写/笔误，本次仅采用可由独立 Wiki 和固定 data 明确复核的一技能攻速算例，不把整篇文章概括为全部机制权威。

## Root 后续执行建议

1. 独立 Source 审阅全部候选及输入载体；第 115 节实际绑定 Source guard 后再执行公开 calculate_damage。
2. 对每个外部例保留原输入、输出定义、raw source 引用、原 HTML SHA、当前源码 SHA 与实际完整返回值，记录 caller 未变。
3. 先核对 raw 500 / 1200、敌方 DEF / RES、组件类型唯一、S1 的攻击倍率与技能攻速条件，再比较相应 per_hit 或 interval_seconds；不以 total_damage 代替外部单击例。
4. 原文约数的结果以“给定名义输入一致”报告；整数展示、未取整内部值分别处理。不得扩大容差来掩盖差异，不得为通过改写外部期望。
5. 第五例只有 Source 和输入映射足够时才加入，不足则明确留证。整个第 115 节仍是实际功能推进后附加此准确性检验，不把资料搜集本身算作完成一节。

`project-source-observation-pins.json` 是检索时只读源码观察，**不是未来第 115 节绑定**；未来实际 guard 仍 null。`project-input-carrier-source-extract.json` 为纯 JSON 固定档案摘录。所有实际 verdict 由 Root 唯一产生。

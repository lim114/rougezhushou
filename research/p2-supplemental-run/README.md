# 七名低星干员的稳定本局属性修正

对应 P2“补充低星干员的本局修正”。覆盖玫兰莎、芬、克洛丝、史都华德、卡缇、米格鲁、芙蓉；新增能力是将现有已证属性符文加入单次技能/声明次数工具，按当前干员筛选，保留不含本局修正的同培养对照及差值。不是完整技能时序或全部藏品计算。

## 依据与复用

- 培养、七级技能、候选天赋仍使用 `rouge/data/supplemental-skills.json`，原字段一致性已由 `verification/full-140/source-evidence.json` 核对，本批未重写该资料。
- 新选择器片段 `rouge/data/supplemental-run-selectors.json` 来自同一固定 [character_table](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/character_table.json)：SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。提取原职业、地块和 `subProfessionId`，不从中文分支名猜选择器。先尝试固定 URL 下载，未完成而中断；随后直接校验既有原件并提取，未将网络尝试记作成功。
- 藏品来源仍使用固定 [roguelike_topic_table](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json) 和既有 `relic-mechanics.json`。复用 `relics.prepare` 的职业、位置、分支、领取者、条件、完整性及局外范围保护。
- 属性层沿用 0.56 已核验链（`BATCH_0.56.md`、`CORE_0.56_VERIFICATION.json`；完整原件核验为本机忽略缓存中的 `relic-panel-056/REPORT.md`）及 0.65 攻速属性边界。直接复用 `relic_attributes.apply_attribute_runes`：符文加算/乘算/最终倍率、FP与float32、整数写回先于现有普通天赋与技能层；不另造乘区或取整规则。分队复用 `run_modifiers.prepare_run`，未确认效果阶段不套加成。

## 实现边界

输入只接受原始 `relic_ids/run_config/relic_context/inventory_status/operator_metadata`；拒绝已准备的 `effects/base_attack/_attribute_runes`，避免重复套用。界面快照只包含必要的强化字段，按干员 ID 隔离；“更新本局条件”保留编辑器当前干员及测试条件，不写入账户或本局。培养默认/账号参考仍是独立预览条件，不因为工具打开而确认为本局事实。

只消费 `is_attribute_rune` 已支持的生命、攻击、防御、法抗、攻速、再部署符文。其他已解析规则显示未计入；藏品清单不全、层数/领取者不明、分队未确认等显示部分参考。战斗回调类来源继续仅作资料。技力/费用/回费、普通战斗增益、持续回复及最终伤害修正尚未接入，不能将该工具当完整本局预测。指中狼禁止技能由既有解析器拒绝。

卡缇的回复用符文后、当前已解锁天赋后的最大生命；芙蓉的治疗与玫兰莎攻击、米格鲁防御保留既有天赋/技能加算。克洛丝二连射与天赋组合仍未知。声明生命缺口可在加成后合法而在无加成对照非法，此时对照不可测算，不用零补差值。

精零已培养公共技能5–7的肉鸽实际适用性仍未闭合。复查第118节检索回执后进行针对性查询，PRTS集成战略/机械师资料和原表训练门仍不能证明该实际使用规则；本批未改这个数值门，也未将旁证变为默认。

## 核验

31项必要检查通过：七名干员无修正兼容、符文与分队合并再计算天赋/技能、职业/地块筛选、缺层数、强化归属隔离、技能禁止、未覆盖费用、藏品不全、生命缺口、反重复准备、战斗回调排除、刷新保留编辑器及既有136–140直接相关行为。

原生 Windows Qt 临时状态验证七个实际主界面入口及一次保留编辑器更新；真实原项目窗口经 Windows-mcp 重启、打开新入口并点击更新按钮，图上输出可见且响应。没有操作游戏或发送聊天；5份既有私人状态/配置核对未变，哈希仅留忽略缓存。游戏实际面板、当前热更新、真实强化采样和完整时序未在本批验收。

首次29项检查中两处新测试条件写错（自身缺口3500超过实际最大生命、禁止技能提示文字匹配过窄）；仅按已证输入/提示修正测试，保留失败记录，不迎合测试改变机制。完整首次本机全量仍有12个旧断言缺口，未因本批局部通过销项；下次到期全量155。

重建选择器：`python research/p2-supplemental-run/extract_selectors.py --source <原始character_table.json>`。工具校验 SHA 后仅以独占创建方式写新片段；已有输出会拒绝覆盖。测试入口：`python verification/section-141/run_checks.py`；隔离界面：`python verification/section-141/check_window.py`（需要Windows原生依赖与Qt环境）。

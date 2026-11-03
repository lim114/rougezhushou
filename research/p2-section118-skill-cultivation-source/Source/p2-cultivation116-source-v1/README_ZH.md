# 计划118：技能等级读源选择与培养资格解释（Source候选）

这是一组实际产品功能候选，尚未应用或运行。Root应先按第117节实际源码复核，再应用局部transport，并执行计算、Wine窗口及保存读回检验。候选作者的项目/import/tests/Qt/Wine/native/helper/gzip/Git执行均为0，tracked和私人状态改写为0。compile-noexec与资料提取只证明Source可读，不能计作Runtime通过。

## 实际产品缺口与新流程

目前接口本来就接受精英0/1的公共等级1–7；本节不能把“再允许7级”当新修复。现有本局视图刻意不自动填账号技能等级；本局等级缺失时沿用7级预览，即使账号已读等级是3。界面只有通用“读取/预览”标签，缺少直接选取兼容已读来源的局外模拟流程，也没有把技能开放门、账号训练门与肉鸽招募上限分别说明。

新checkbox明确选择当前技能已读账号等级进行局外模拟，默认关闭。可用参考必须是该技能有效已读整数、1–10且不超过原levels长度，并通过现有技能开放/精英2专精门。账号专精10在精英0/1不可选，绝不自动截成7。账号缺失、masked、坏值或锁定技能不可选；已选参考后来不可用会清除选择并恢复原本局读取/原预览。取消选择立即恢复原值；更换技能、干员或新局会清除选择。仅在已选参考生效时调整scenario的skill_rank，并加入“所选技能等级（已选账号参考，局外模拟）”未确认提示；两个原始状态对象/文件均不改写。

新“技能培养来源与资格”区即时列出来源、本次等级、现有计算开放门、固定原始训练门和黑流树海招募阶段参数；账号参考永远不冒充本局确认。默认数值、原rank标签与报告口径保持；新说明本身不改运算。这里的明确选择不是手填等级，不改原技能等级只读标签。

## 原件与查询结果

复读固定Kengxxiao/ArknightsGameData提交`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。character_table实际14,975,251字节，SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`；roguelike_topic_table实际17,943,244字节，SHA256 `f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86`。路径与Hash在original-source-binding.json。复用早前资料下载，未把旧回执的路径当作当下存在证据。

- character_table：30个实际匹配计算档案、83技能的原skillId/unlockCond；各公共等级升级`allSkillLvlup[rank-2].unlockCond`以及所选技能专精`skills[skill-1].levelUpCostCond[rank-8].unlockCond`，每个原子子树按原类型与字段顺序提取。
- 公共等级2–4训练门为精英0 Lv1，5–7训练门为精英1 Lv1；它们是训练成本条件，不能新解释为受限形态使用条件。
- topic六主题`details.rogue_N.detailConst.charUpgradeTable`分别记阶段0 PHASE_1/skillLevel7/skillSpecializeLevel0、阶段1 PHASE_2/7/3。本节只列“原表招募阶段上限参考”，不据此填补账号/本局缺值，不推定临时/应急招募及未知事件行为。
- char_1001_amiya2和char_1037_amiya3的原始patch资料仍缺失；虽然现有计算档案有技能门，原训练资料状态必须是missing，不借用caster阿米娅。
- 公开搜索命中普通招募首次精英1满级/7级上限及低于上限按账号的论坛说明，但未证明精0限制形态已训练5–7的真实使用规则。原论坛片段不计权威闭合。
- Wiki.gg与PRTS正常HTTPS返回403，Fandom返回402，未绕过。第一次PRTS URL出现编码错误后，仅按正常URL编码修正一次，最终403保留。BWIKI公开页200，只有“最高进阶状态与局外同步”等一般介绍，不能证明技能使用规则；oldid345768见网页正文。完整查询页面/失败下载台账全部保留，不以搜索摘要冒充已读文章正文。

公开原始网址：

- https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/character_table.json
- https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json
- https://wiki.biligame.com/arknights/index.php?title=%E9%9B%86%E6%88%90%E6%88%98%E7%95%A5&oldid=345768

## 精确应用范围

新增`rouge/skill_cultivation.py`、`rouge/data/skill-cultivation-reference.json`和18方法tests；cloud-selector-local-transport.json只新增所选测试条目。app-local-transport.json有6个精确块：新增checkbox/解释区，rank读取改为纯选择helper及来源区更新方法，update_skill_options先更新来源区，保持默认rank标签的格式器调用，显式参考未确认提示，新局清除参考偏好。`candidate/rouge/app.py`只供Source阅读，**不要用完整app覆盖将来的116/117成果**。Root须重绑定实际源码后单匹配应用，保持CRLF与其余字节。

未修改damage.py、operator_engine.py、condition_cultivation.py、account_cache.py、RunState、原始培养记录的合并/优先级/磁盘策略、技能解锁门、等级预览默认值或任一数值公式。对账号参考不适用时，Source helper保留既有default rank，不把新分支校验扩展为旧读取记录的新schema。

## Root应完成的实际检验

18方法包含完整来源选择与取消、默认无自动继承、active/locked及masked边界、整数原型、30原件/83技能训练坐标、两个patch缺失、原件identity drift、招募参数不填事实、精0未知状态、两种时序的真实苏苏洛治疗级别与取消后的完整结果、三种默认等级/标签保持。测试Source已AST/compile-only，未执行。

实际窗口必须验证WINDOW_ACCEPTANCE.md所有成组状态，特别是checkbox会真正改变计算请求、取消完整恢复、重置选择时不连带改本局/账号、账号专精不兼容不截7、来源变化后不可用立即清除选择。选用真实项目MainWindow、public临时RunState/AccountCache及三种报告；分别留numeric调用前后、格式器后的完整原生图与原盘字节，关闭/重载读回并核实实际PNG可见内容。单纯select_rank单元测试不能替代窗口控制流，Source JSON/截图头不能替代实际图片查看。

原始116前app快照是115实际app，未来应用必须以Root实际117/后续Source为准。Source清单固定本包自身所有公开字节；不得用Source manifest或compile-only冒充运行通过。

## 仍未完成

“肉鸽受限精英形态的已培养公共技能等级可用性”只新增可见未知说明与明确参考选择，**不销项其原生机制问题**。精0公共5–7的实际使用、热更新一致性、临时/应急/未观察招募事件及真实激活仍未知。本节不自动继承账号技能/专精、不把升级训练门套到使用资格、不改变已接受精0公共5–7输入。

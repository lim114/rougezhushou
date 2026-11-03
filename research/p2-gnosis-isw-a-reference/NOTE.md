# 第48节审查草稿

基线：`codex/p2-development` / `04a9a3fbe3680dd221fc5254fadc9aeb050eb1cf`。生产仓库未编辑；全部修改在本目录的 `draft` 内，`baseline` 是冻结公开依赖。合入只用独立 hunk；不要覆盖整个旧文件。

`code.patch` 包含 `operator_engine.py` 的5处窄插入、`reporting.py` 的独立灵知段，以及新 `gnosis_module_reference.py`。`tests.patch` 为新测试文件；`section48.patch` 是两者合并。没有第49遥或第50友方报告改动。

精二60级及以上、选中 ISW-A 各等级时，原版坚冰的描述和完整黑板保留为条件参考。模组同 talentIndex 0 的 `#`、`1`、`10_root`、`11_root` 分别保留选中候选的 raw metadata；不合并黑板，不从 `max` 构造冻结倍率，不声称能力实际并存。资格未满足、普通模组和无模组保持原输出。

TRAIT 原描述“自身在场时，处于寒冷、冻结的敌人每0.5秒受到灵知攻击力50%的法术伤害”与 `.5 atk_scale / .5 interval` 保留。持续法术分项只有每跳条件参考，不排 tick；实际首跳、跳数、状态覆盖、攻击快照、刷新及技能后生命周期未知。初始 cold_state=0、本体无供靶和全程打断均不能证明没有后续/已有寒冷。所有资格满足的正观察输出实际总伤保持未知；明确零观察窗口或当前敌人零生命周期的实际伤害为0。

本体每击数值和原时钟流保留为孤立条件参考。所有原初动/SP/回转参数保持；S1实际结束仍未知。新增 `phase_clock_unbound=true` 和 `resource_and_damage_shared_clock=false`，避免把含未知状态/DOT的整段输出声称为与SP共享实际时钟。`unplaced_components` 相应记录条件本体；不从普通攻击循环绑定特殊时钟。

资料为固定同一游戏数据 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。四表与旧receipt哈希及对应原天赋/模组parts逐条匹配。复用相同commit的 `gamedata_const.termDescriptionDict["ba.frozen"].description`，明确证实敌方冻结法抗-15；这属于通用冻结状态，不能证明模组附着或实际状态时钟。没有改变无模组口径。新增DOT selectors、全部模组候选和通用冻结资料的独立核对记录见 `source-receipt.json`、`source-selector-audit.json`、`frozen-status-source-audit.json`。

验证：15项新增、总计106项相关测试全部通过；476个公开前后调用中116个控制逐项完全相同、144个正观察输出为未知、216个明确零案例为0。原152案例中的72个丢失原天赋案例均恢复完整描述/参数。全部入参、catalog、原时钟流及初动/SP/回转参数保持；生产五个关注文件哈希未变。`git apply --check section48.patch` 通过。早期复现的整份timing相等断言发现条件来源标记变化；最终按原clock/stream不变、3个明确未知metadata正确变化核验。

复现命令：

```bash
cd /tmp/p2-draft48
PYTHONPATH=/tmp/p2-draft48/draft /workspace/rougezhushou/.venv/bin/python -m unittest discover -s draft/tests -p 'test_*.py'
/workspace/rougezhushou/.venv/bin/python reproduce.py
```

`public-inputs.json`、`baseline-public-results.json`、`draft-public-results.json` 为本次公开输入及两份结果。Windows/Wine全量、实际测试窗口及提交由root负责；本草稿不声称原生Windows、游戏或桌面聊天已验证。未读私人状态，未操作游戏，未发送消息。

独立恢复条件：取得匹配版本的 `gnosis_equip_3_1_p1`、`gnosis_equip_3_2/3_p2/p3/p4` 能力/buff模板或独立事件证据后，再核对原天赋并存、隐藏附着、增长与重置顺序、首跳/刷新/退出和技能后DOT生命周期。当前参数或相邻普通攻击动画不满足这些恢复条件。

root合入后把默认界面中的prefab/索引术语改为能力并存/附着说明；原始技术身份仍在结构化来源资料中，数值与未知边界不变。最终相关和精选在最终文字上重跑。

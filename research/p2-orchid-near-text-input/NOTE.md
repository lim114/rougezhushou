# 第85节作者候选：梓兰near文本假确认

固定基线 `b5a40f30683bfc0945decaabbd4db5914c28427f`，720份公开`.py/.json`从git blob冻结，作者仅在外部目录修改。完整基线与候选均可由此提交和补丁重建；不创建worktree，不编辑tracked，不运行GUI/Wine。

问题：已选中“翔虫机动”时，`near_previous_deployment='false'`按Python非空文本真值给出位置附近加攻。真实Qt生产者是bool默认false的QCheckBox及`isChecked()`，不是文本解析。原E1L1/E2L1天赋分别atk10%/15%，原模组X2/X3在E2L60给同index1/prefab1的20%；原30秒参数及实际位置覆盖/技能时钟未知保持，不改加攻层或建立新事件。

补丁只有 `rouge/damage.py` 的6行late guard及 `tests/test_orchid_near_text_input.py`。在`_evaluate_damage_once`原build_report之后、return之前，仅Orchid且near值为str时，调用**原真实selected_talents**核对已选具名“翔虫机动”，选中才抛 `near_previous_deployment 不接受文本条件；请使用布尔值。`。保留E0inactive、其他owner、非str全部旧真值行为、缺省false、模组资格和隐藏再部署身份。`double_charge`不在此修复范围，S1旧缺省true与文本旧行为保留，S2/S3仍忽略。

late guard保留原培养/技能/模块/敌人/藏品/时序/finishers/报告错误先行。83/84将在同函数插入其他late guards；root合入85时只应用独立插入hunk并保留它们，不能用这份老完整damage文件覆盖。root还需把新测试module登记到verify_cloud。

源资料先独立封于 `source-only`：完整原character含具名/隐藏天赋、3skill×10ranks、模组元数据/三级parts、7个固定代码blob、真实selected helper源及Qt静态生产者。源封包0API/helper运行/测试/草案/GUI/Wine；这与作者随后计算分开。作者9项新测试实际核对helper选中及模块门槛，严格saved comparison另94次真实helper资格调用（不是公共calculate调用）。原未知附着/部署/箭矢/充能/结束与热更新边界不变。

作者验证：

- **9项新测试通过**，一次运行；其calculate调用未装计数器，不宣称包括它们的精确总调用数。
- **40项既有相关测试通过，0skip/失败/错误**，只运行旧orchid箭矢/再部署、培养类型、模组门槛、整数控件合同。计数器记录1328次公共calculate调用；没有重跑已成功9项新测试。
- **197对完整typed JSON及3文本**：94对仅从已有选中天赋文本成功结果改为明确类型错误；79对旧成功整份JSON/format_estimate/default/technical报告完全相同；24对旧错误类型/文字、原输入与caller不变。基线197次+候选197次=394次公共calculate调用；strict comparison0次重算。
- 覆盖E0无天赋、E1L1、E2L1、L59/L60模组1/2/3、技能最小与rank7/10边界、三技能/两模式、empty文本及未知文本、True/False/缺省/numeric/None/list/dict别名、零攻击/窗口/生命周期、其他owner、double_charge旧域和既有再部署符文。near矩阵潜能使用旧默认1；既有培养类型测试另检查原潜能合同。所有调用保持caller及cached catalog。
- 验证后基线720份与freeze逐字节相同，候选719份旧文件相同，damage唯一本体改动+1个新测试；CRLF保留。补丁在冻结baseline目录`git apply --check`通过。

不把静态源证明或作者Linux计算称为实际Qt、Wine、原生Windows/游戏验收；这些后续由root完成。49项测试通过只是上述相关范围，不是完整仓库测试。

旧ea7866b的两个Orchid公开观察（False攻击1000，文本false攻击1150）仅作为历史lead保存，0次计入当前matrix。初次全125源identity复用在engine正确拒绝，因为当前b5已有苏苏洛文本guard；原错误、唯一diff、旧完整JSON/3报告及124一致/1不一致证明全留在source-only。随后当前197对必要基线/候选从固定当前版本新算，没有冒充旧记录为新调用。

作者源/测试/matrix已经 `author-freeze085.json` 明确冻结，正式独审pending，`review079`接手保存资料复核及独立窄fresh验证。正式review之前不改冻结源或重跑成功matrix/测试；如发现缺陷，保留诊断后仅重验必要变化。root拥有tracked合入、完整回归、archive/commit/tag与批次UI。

# 第296节候选 · 无效验尸相关节点配置资料

这是缓存候选，尚未提升、集成或完成第296节。它只提供固定资料说明；不改变现有层数、节点候选、资格、事件入口或本局记忆。来源构建和缓存后端测试不替代产品/UI验收，也不包含其它代理正在准备的反向事件入口。

## 已证资料与边界

固定游戏表版本：`a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，完整原件SHA256 `f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86`，17943244字节。

四个完整FEATURE的中文用途分别明确写第3、第4、第5层普通作战及假层普通作战；各自完整buff均将`ro6_t_12`、`BATTLE_NORMAL`、`rogue_6_bubble_04`、精确zone和`not_hold_relic_id=rogue_6_relic_final_5`关联。`limit`原类型为float、原值1.0，仅保留配置参数，不当作实际数量或必出次数。

21个完整原对象以原始字节直接选取，不重新编码冒充原字节。每个文件的完整JSON路径、原表起止字节、长度和SHA均在`topic-selected-index.json`；完整原件SHA先通过builder才生成索引。对象包括：原stage、4个FEATURE item、4个FEATURE relic、4个zone、光明之末/湮没“光明”/怦然信标各自完整item和relic，以及后两者完整relicParams。光明之末没有独立relicParams记录，本包没有编造。

前三主层数字来自中文用途，不解析ID后缀。第四项原文称假层，其zone名称虽与第4层相同，`isHiddenZone=false`也仍不等于已证主层身份；单独列出，不称主层4或秘境。原stage是NORMAL且没有原linkedStageId/替代IDs，不增加紧急别名。

PRTS固定修订433770的完整HTML已有公开原件`research/p3-stage-context/community-main.html`，SHA256 `366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9`，954799字节。此候选复用并保留该完整原件，不改旧包；新包另选完整光明之末`<li>`的原字节及起止位置。该段支持未持有湮没“光明”时标记普通作战、完成无效验尸后可以选择获得该藏品，是社区说明，不能当作实际发放/服务器门槛或补回缺失脚本。完整HTML中的“抵达VI前找到”仅为流程说明，不当生成硬限制。

光明之末完整item明确提及持有怦然信标可获得削弱强敌的方法，但并不直接证明获得信标就给这四个FEATURE。固定主题表中排除各自id/iconId后未找到FEATURE ID的其它字面值引用；此审计不证明原生/服务端没有机制。实际FEATURE获得、附着、标记位置、执行、进入、奖励与完整入口池均未知。所有actual字段保持None，不提供当前持有/楼层输入，不自动排除或认证候选。

## API与集成合同

`rouge.stage_entry_reference.stage_entry_reference(stage_id)`：

- 非精确字符串`ro6_t_12`立即返回None，不扫描来源；同名/大小写/紧急/后缀等不扩张身份。
- 来源有效：`status=documented_reference`，`reference_kind=documented_stage_entry_configuration`，完整stage/rows/marker/not_hold_item/beacon_item/community_reference/upstream_reference/source及普通中文notice/unknowns。四行`main_floor_reference=[3,4,5,None]`只是本资料的层数描述，绝不能接到现floor资格筛选。
- 来源失效：`status=source_unavailable`，rows清空，marker/items/source清空，actual仍未知。UI必须清掉旧选择、旧说明和旧入口，不沿用缓存。
- `source_data()`：每次fresh核验后返回深复制原包；失效返回None。无公开data/evaluator覆盖参数。

每次调用都读并哈希data、固定SHA的manifest及其27项独立依据/构建器文件。可复用解析结果，但不缓存真实性；暖调用后原件、manifest、data或builder变化仍立即拒绝。运行时不读取17MB大表或完整HTML，不写入文件；builder重建才读取完整原件。

建议默认中文先显示：

> 资料中的相关节点配置：第3层、第4层、第5层普通作战，以及原资料另称的假层。标记名称为光明之末。配置另列“未持有湮没‘光明’”。这些说明不表示本局已挂上标记，也不保证每层出现一场。实际位置与进入条件仍未完整核实。

原ID、原float参数、完整对象与来源放资料详情。当前库存不用于校验过去状态。固定战斗详情/预览手动入口由root负责，不能改现source floors、21−6−15或25/57。

## 已实际执行的候选检查

- `first-source-build/`：首个纯文件来源构建真实exit0；原builder/data/manifest及原日志保留。首版本只在原输出位置构建，后续为隔离输出目录复制builder增加可移植支持；原数据及21个选定原件没有变化。
- `source-build-portable-output/`：修订builder的纯文件来源构建真实exit0；新manifest将修订builder的SHA绑定。
- `first-backend-necessary/`：15个缓存后端必要测试首次真实exit0，原model/test/manifest/stdout/stderr/process保留。涵盖严格身份、完整stage/21原件/6参数类型与指针、3主层/假层、关联物品、actual未知、PRTS说明范围、深复制、暖缓存篡改/缺失/恢复、不依赖大表与无写入。
- `portable-backend-necessary/`：同15个方法在仅复制明确31文件清单的隔离夹具上再次真实exit0；避免提升到完整项目后复制整棵研究目录。仍是15个不同方法，不重复累加成30。

没有运行Qt、窗口、游戏、聊天、live tests、Git，也没有读取/修改私人状态。下一步root应独立核验候选及来源、提升明确清单、集成中文显示，并在真实Windows界面验证默认/刷新/来源失效/恢复未选和父阅读状态。其它代理的未完成能力未计入上述结果。

## 纯文件重建

从项目根调用候选builder，输出到新的隔离目录：

```text
.venv/Scripts/python.exe -B -X utf8 .cache/p3-296-autopsy-entry-candidate/scripts/build_stage_entry_configuration_296.py --game-source .cache/p3-287-event-research/fixed-game-topic.json --community-source research/p3-stage-context/community-main.html --output-root <隔离输出目录>
```

调用缓存后端必要测试：

```text
.venv/Scripts/python.exe -B -X utf8 .cache/p3-296-autopsy-entry-candidate/tests/test_stage_entry_configuration_296.py
```

游戏材料版权属于鹰角网络及关联权利人；社区原文CC BY-NC-SA 4.0，保留版本、URL与许可说明。

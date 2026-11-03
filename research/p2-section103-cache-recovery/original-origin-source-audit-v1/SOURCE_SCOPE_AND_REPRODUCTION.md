# 第103节深层消费者资格：只读候选审计

本包只是公开输入和消费路径的 Source 证据，不是产品实现、实际复现或检验通过。主代理正在完成第100节五节全量，当前743维护源码不能应用本包。之后任何第103节产品必须重新绑定已完成第102节的真实基线。

## A. 重新读取明确招募来源时，旧来源证据叶子可能不可消费

当前 `rouge/run_state.py:61` 只要求干员 `sources` 为对象。`sources.recruitment_kind` 的值可以是合法JSON null、数组、字符串或数字；它们不会触发加载容器保护。干员ID、fields、skill_ranks、char_buff_ids均使用现有固定公开档案和 `tests/test_origin_discovery_055.py` 的OWNER/BUFFS，不涉及私有状态。

加载使用 `RunState(public_path)`。随后真实入口 `RunState.apply(observed, 1002)` 进入干员合并：上一记录来源为 null 或已知来源，当前读到合法 `non_emergency`；代码580检查旧证据 `.get('source')`，依赖该叶子为dict。Source预期非dict将产生AttributeError。是否加载接受、错误类别和位置、之前是否已有部分状态写入，只能以主代理原实现实际结果为准。

这个叶子被读取是为了判断旧 `{'source':'金色应急雇佣标记'}` 是否需要特殊classification_corrected。普通旧来源证据不会触发纠正；真实已知来源从emergency_hire到non_emergency仍要记录recruitment_changed、使旧培养失效并清空旧绑定。首次未知到已知的来源发现原本保留培养和强化。不能把所有旧坏值解释为旧金色标记，不能把unknown归零，也不能靠拒绝整份历史文件丢掉其它记录。

最小消费者方案（需真实复现后才运输）：先取旧叶子 `origin_source=previous.get('sources',{}).get('recruitment_kind',{})`；`corrected` 保持原 `origin is not None` 门，再要求 `isinstance(origin_source,dict)`，最后比较原source文字。其它来源、清空、培养、强化、数值API和保存语义均不变。不存在/空dict/有无效source叶子的dict维持原比较结果False。fresh合法marker仍按现有sources合并覆盖坏来源证据，正常保存、重启继续；未使用坏叶子不得因此拒收或清洗。

## 原实现 probe 与健康/未使用控制

14个独立saved/observed JSON在fixtures目录，审计审阅可核对 `audit-origin-provenance.json` 的当前源hash。

- 四种坏叶子null、[]、公开text、数字1，加fresh明确来源，属于待原实现实际复现候选。
- 来源证据缺失、空dict、合法v2marker，配首次来源发现，是健康对照。
- 原先已知emergency_hire配null坏证据、同条件真实v2marker，是错误/普通真实变化对照。
- 原先已知emergency_hire配旧金色markerdict，保留特殊classification_corrected对照。
- 坏来源证据配freshorigin缺失/None，旧短路安全；保存应保留坏来源原值而非清洗。输入没有fresh来源不会使缓存成为明确来源。
- 坏来源证据配stale1000时间，apply首先False，不得读该坏叶子或写盘。
- markerdict的source=None和opaqueextra=[]比较本身安全，应继续接受。

Root-only probe Source位于original-linux-probe-source-v1/probe103.py。它绑定原743文件map、RunState1b6f和CORE a75d，临时公开run.json及预存.tmp哨兵只在fresh --out/public-state写入。保留实际caller类型/值/顺序/别名、真实state、原disk/tmp bytes和flags；读取summary应无状态/磁盘修改。actual apply(True)标为合法observation/save新phase，不假称保存后仍是原磁盘；actual exceptions、restart、guard前后另存。product_pass始终False，primary0只是观察流程完成，不能代替产品PASS。截止120s，不接触Qt/game/chat。

启动建议（先由主代理审稿，作者没有执行）：

```
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/section103-nested-consumer-source-audit-v1/original-linux-probe-source-v1/probe103.py --root /workspace/rougezhushou --guard /workspace/.continuation/full100-completed-source-guard-v1.json --fixtures /workspace/.continuation/section103-nested-consumer-source-audit-v1/fixtures --out FRESH_OUT
```

必须外部保存真实primary exit/log。原schema拒收、import失败或probe本身失败只能保存为观察失败，不能计产品缺陷。

## B. 缓存分队ID在识别复用资格中作为hash key

独立只读审阅已定位 `config.squad.id=[]`：加载guard仅要求squad对象/name文字。`RunState.recognition_context()`返回深拷贝本局difficulty/squad，随后 `run_config.confirmed_config()` 在有合法run_id且squad.captured_at不为None时做 `config_data()['squads'].get(squad.get('id'))`。列表ID不能作hash key。正常公开分队ID `rogue_6_band_6` /name `矛头分队` 是健康对照；未知字符串ID应保持不复用；captured_at缺失/None及非法run_context.run_id原短路必须保留。

不能称窗口启动崩溃：数值 `prepare_run` 已有string资格ValueError，并由窗口calculate捕获；BattlePreview也把相应ValueError/KeyError转为pending。这是识别复用资格候选，需要Root先实际原实现复现。最小修复位置应在confirmed_config判断ID是str再查固定map，保留缓存原值、其它配置，以及缺/无效资格不复用。未知ID不能默认为健康分队；后续实际合法同局重新读取应能更新/复用。

## C. 资源缺value的边界必须区分保存文件和direct apply

保存文件资源value/captured_at在第98节guard79必填，缺value已拒收并保留原文件；不能再次当新缓存启动缺陷。

direct公开入口 `RunState.apply({'resources':{'gold':{}}},at)` 在fresh/no prior key或旧value=None时：record.get(value)与旧None相等，跳过history里的value索引，仍存只有captured_at的record，可能save/True；MainWindow.apply_run_observation随后summary索引value可能KeyError。旧value8时先history value索引KeyError，不覆盖那个resource。这个Source路径尚未实际复现。现有read_resources生成的资源均明确整数value，未确认就不产生key；没有证据证明真实OCR会产生{}。因此仅保留direct输入边界候选，不将它说成真实producer自然失败。

若Root确认并选入，最小方案仅在apply的资源消费者检查record为dict且有value，缺值视作本次未读，保留旧记录/时间、不填0或刷新确认证据。显式value=None/文本/list等目前numeric API的ValueError由calculate捕获，不能借本节泛化新值schema或宣称未处理崩溃；resource未知名称/history、101counter资格、102库存可信标记也不在本范围。

## 收口与未解决

本节可共同验证“已接受历史记录能够被新的合法观察继续补全/恢复”的消费资格边界。现阶段A/B是精确Source待实证，C还缺真实producer自然路径证据。Root原实现观察完成后才决定具体功能组，按真实已完成102基线运输。任意历史叶子/schema、缓存raw IDs数值含义、库存verified可信标记都不因本包而获认证。作者仅stdlib读JSON/hash、写本仓库外包、compile文本；项目/helper/codec/Qt/tests/Wine/Git/tracked writes执行数为0。

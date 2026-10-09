# coherent101 fresh v2 产品独立 Source 审阅

结论：指定 fresh v2 候选未发现新的 Source blocker。Root 已保存的原实现 Linux 复现与此次最小消费者资格相符；unknown buff Qt 原观察和最终候选 Runtime 仍需 Root 实际验证。本审不应用当前冻结743，不增加完成小节，不把 compile/Source 叫 Runtime PASS。所有项目/helper/codec/Qt/tests/Wine/Git 执行为0，tracked写入/私人读取为0；仅公开 Source/JSON、标准库哈希/AST/compile-only、内存运输预览和仓库外附证。

## 实际 fresh v2 pins

| 文件（相对本目录） | bytes | SHA256 |
|---|---:|---|
| `manifest.json` | 1433 | `0c9efcd491a0956544605b79b9bc3defb19dcbe65e07ff5808a629c738b13817` |
| `candidate/rouge/run_metadata_view.py` | 1483 | `96765f55f696815c44b9c3eb22b4e6247f4ffe1c9d3a064c5301cfdc33de7e3b` |
| `candidate/tests/test_cache_consumers_101.py` | 16712 | `cf8654a622f8c09d4ec41cbd1a857c9e1733c500c3fc9c93ecb495f9f36f18b8` |
| `exact-local-transports.json` | 3699 | `170c40b624fa607a42c8b456fbb9c2a56d819c48ac1091f21eb619680b978e8b` |

当前实际基线：run_state 53169 B / `1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9`；app 99596 B / `34f0c92061460b239fd0af80ec263673765a16753826f6151fde87a88b89a35b`；counter semantics 4765 B / `7ab327e3ebaa4a561f5d40abfa5e179dda4e3101fa3316ff5607b11cb9aa0473`；registry5220 B / `96f512af7555d2b170561e71cccceb8cad11308662abd4899df1a49121ec0063`。Root当前100 full未完，禁止借本Source结论提前运输；作者文档/manifest明确该条件。

## 独立运输与编译

标准库工具 `57bd6f` primary0实读5条 before，各自在当前维护文件中唯一；只在内存按列出的局部文本生成预览并 compile-only，不运行作者脚本或任何模块、不写预览。当前CRLF仅供Source预览转LF，原文件字节hash单独保留，不能冒称实际字节应用。

AST确认 RunState17方法只改apply/summary，其余15方法不变；MainWindow59方法只改sync_target_buffs，其余58方法不变。counter模块只有valid_counter_resource变化，原counter_resources AST不变。registry只注册新测试模块，未改执行器。99持久化/98guard/100training-view及calculate原数值和metadata运输不在改动范围。helper及测试Source均compile-only成功，计26个test_方法；没有运行其中任何方法。

独立附证 `independent-source-transport-audit-v2.json`：2088 B / `4e8ecfe424ac472f14399a0536884538eb7852ac9403809ad011a1315457d256`。

## 原件读取与资格结论

工具 `fde6a5` primary0实读两份Root实际JSON，`fdf2e9` primary0逐字节比较候选包副本与Root原件，完全相同：

- `Root-original-json-actual-linux-v2-observations.json`：12540 B / `23d01a180857b1a083a02bff8137ba460da2b33a65496b628bcbc565c2bd946c`，8项；stored text count的正比较TypeError、present text/null的sum TypeError、resource list ID哈希TypeError都有已接受JSON和同条件健康对照。source_drift空、product_pass=False。
- `Root-original-counter-source-actual-linux-v1.json`：5797 B / `6c06be67ea7e0e864fac28b1c697383e2782c669f72699a104ad35bfc8a91403`，4项；source None/[]/1各产生startswith AttributeError，原有效字符串proof仍可用。source_drift空、product_pass=False。

这些是Root的实际原实现观察，不是本审执行，不能证明候选已修复。最早缺必要dict的无效probe不作为产品错误，文档正确保留这个区别。

### 库存 count 能力门

只在原正数/完整移除分支前加 `isinstance(expected,(int,float))`。str/list/dict opaque saved count不再与0排序；没有parse、赋零、删持有、拒载或改原record。bool仍是int子类，因此保存bool、numeric/float和fresh0/float0原合同保留；incoming bool仍先走原None未读分支。明确定义 fresh count仍能按原观察更新/保存，并证明相应完整/空清单；未知保存值不能凭缺失一帧成为移除证据。

### 摘要 present

sum的输入改为bool真值，使每个成员按既有names/overview/current-run门贡献0或1，避免把任意JSON叶子直接相加。没有修改present原值，也未将未知存储值写成新departed/confirmed事实。missing/defaultTrue、boolean和int0/1旧控制保留；这是按成员计数的显示资格，不宣称所有任意numeric旧sum文本保持一致。

### opaque counter proof

valid_counter_resource仅对proof.id和proof.source加入str能力门，再调用原converter。默认缺source仍为原空字符串路径；安全未知string身份仍False，非字符串安全未知身份也保持False；list/dict身份与已知ID的非字符串source不再落入哈希/startswith异常。unsupported proof保留历史值/待确认，不生成0或已知层数，不改converter、binding表、数值API或原caller。

旧converter先检查value exact int/范围和title，再消费source。value=True/None或title不匹配原本会短路False，即使source坏值；新增测试明确这些同条件False/caller不变控制。有效每种既有binding及0/1/max、原来源/loss/reacquisition资格仍由原converter/reusable_resources处理。只有实际合法新观察可替换坏旧proof并正常save，不能把这种授权写盘误称view-only原盘不变。

### buff显示 helper 与 app 局部

healthy IDs/duplicates、empty complete/incomplete、pending positive-prefix和inactive scope的原文本逐段保持。unknown positive或pending字符串直接提示无法识别/暂不可确认，不伪装已核对无强化，不过滤成健康列表，也不修改complete/absence/pending/recruitment或caller。

app只把sync_target_buffs最后的unsafe name projection改为helper调用；仍从原current_run_operator_state取引用。calculate五项raw metadata和原relic resolver完全未改，unknown bound/pending、错误职业等仍由原API明确ValueError，在现有calculate异常护栏里产生无数值结果。helper不是新的收件人schema：活动列表shape仍依赖实际saved/app资格门；未使用的inactive metadata不消费。

## 26 方法的 Source 质量与尚待实际检查

测试load创建合法必要dict和原JSONbytes，明确RunState接受且不重写。view_unchanged前后比native类型/顺序/alias以及原盘bytes/tmp；apply则校核观察caller不变、真实返回True和tmp消失，允许正常save，并在关键控制重启后比较持有/计数/资源。测试使用的native只针对这些有限public JSON对象，未声称任意NaN payload/所有Python对象证据codec。

覆盖saved opaque count及未读/正向新持有/fresh0/float0、numeric旧count/incomingbool、present真值/missing、counter badID/安全unknown/五种有效binding与bounds/source坏值及旧value/title短路、合法新counter恢复、healthy/duplicate/empty/pending/inactive/unknown buff标签、raw API unknown/pending/职业拒绝和healthySNACK28。它们不是单纯重复gate实现：同时验证合法保存、后续消费、恢复、caller/盘和原数值拒绝等合同。纯helper标签控制仍不能替代真实Qt signals/窗口；Root须用actual baseline/candidate比较数值及三文本，保留真实退出码/记录/图。

目前unknown buff原Qt probe仍须Root实际原件；原probe Source认可不等于观察完成。候选实际26方法、相关旧套件、真实窗口、有效重读恢复及100 full完成后的实际Source重新绑定均尚未由本审完成。

Inventory verified真值问题、其它proof/history/config资源叶子及缓存sources.recruitment_kind等仍是范围外pending；不因这个coherent最小候选宣称全局缓存无损、完整schema、nativeWindows或P2/P3完成。此报告只解除指定Source阻断，v1历史未改，Root仍按已授权顺序处理实际验证。

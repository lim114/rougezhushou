# 第 97 节账户 IO 与 Unicode 边界恢复候选

本包仅 Source 准备。没有导入或运行项目、候选、测试、codec、窗口、Wine 或 Git，没有修改仓库。Root 负责实际应用与验收。采用原有已独审候选，未借恢复之名扩大账户输入或游戏机制范围。

## 输入与最小改动

实际读取当前 `rouge/account_cache.py`：10398 B，SHA256 `17250d93fa3932fc6233bc5b8dd8d1a17d76a283feee5fe694ffebe530ecb5d5`。与原候选 expected-old 全字节一致。恢复包的 `baseline/rouge/account_cache.py` 是这次实际读取的公开源码。

`candidate/rouge/account_cache.py` 11551 B / `29bf05d1c7fc111b2e74977be6ca413bb0a25c50cead69fe3a04237ef5a2768e`，与原独审核心全字节一致。完整差异见 `account-core.patch`。仅修改：

1. `__init__` 新建会话字段 `save_issue=None`，不加入账户记录或 JSON。
2. `notice` 在原 per-ID 损坏或 load_issue 提示后追加准确的保存失败说明，保留正常保护场景旧文本。
3. `save` 仍先全映射校核、检查永久保护；然后在任何目录/临时文件操作之前完成 JSON 序列化与可无损写出资格检查；合法路线保留 `mkdir→write_text→replace` 顺序、UTF-8、indent=2 和原平台换行策略；IO 的 OSError 只将保存标为失败并永久保护本会话，不自动重试。

`_integer/_timestamp/_record_issue/_merged_record/_protect/_screen_all/view/observe` 未改。原 `observe` 在 save 之前接受并存入内存；新 save=False 后 observe 继续返回 True，有效事实仍能显示和用于计算。本局状态、数值和优先顺序没有新增假设。

`candidate/tests/test_account_persistence.py` 16063 B / `f4194a4cdec9ec88a3fac1c21d1bb45546ee91ec7dc860d57cdd3799a646b08d` 与原 18 个测试方法全字节一致，尚未运行。旧测试开头的 SOURCE draft 是历史待验收说明，不表示实际已验证。

本包不提供旧 `verify_cloud.py` 覆盖件。第 96 节实际完成之后，Root 应在实际精选登记中新增 `tests.test_account_persistence`，保留全部已存在项与順序。不得将历史“未来 096”快照替换为当前基线。

## 不破坏原盘与内存的范围

真实 app 公开源码中目标是 `.local/operator-state.json`，临时路径由 `with_suffix('.tmp')` 生成，两个路径不同。本节公开测试也使用不同的 `account.json/account.tmp`。

- 相邻原生 high→low surrogate 资格拒写发生在 mkdir 之前。保存失败不能把 Python 中两个原生码点悄悄规范化为 emoji，不能改变已接受内存、原目标或既有临时文件，也不会为缺失路径建立父目录。
- 单独、分开的或 low→high surrogate 仅在 JSON quoting 后转换为 ASCII JSON 转义；普通中文、实际 supplementary scalar emoji 和字面反斜杠-u 不受改变。这里保留的是 CPython 接受的码点，不声称其为跨实现可互操作 Unicode。
- IO 失败不删除、回放或覆盖临时证据。写入阶段可能已经留下部分或完整临时文件；只保证不将失败写入发布到最终目标，不把临时存在误称为最终保存成功。原目标缺失时不声称“原文件已保留”。
- IO 失败保护不会禁用此前有效 view；后续有效读入仍按原 merge、时间和 changed 决定接收，永久保护门阻止进一步 IO。后续坏 ID 仍先显示其原不可用说明。健康原文件的一个新独立 AccountCache 会话可再次正常读取；不解除原失败对象的保护，更不清空本局状态。

## 错误优先级

1. `_screen_all` 和已有保护首先生效；读损坏/结构坏/ID 坏保护不被新保存流程解锁。
2. 原 JSON serializer 的非 IO 异常仍传播，不被伪装为成功或普通 IO 失败。为了资格拒写安全，序列化提前到 mkdir 前；因此“序列化非法且 mkdir 同时失败”的第一个异常与旧实现会不同，这是明确的改变。
3. 真正邻接 high→low 原生码点优先安全拒写，设置详细 save_issue 与保护，不进入 IO。正常 emoji 已是一个 scalar，不命中；跨字符串的 JSON 引号/标点也不命中。
4. 合格文本的 `mkdir/write_text/replace` 只捕获 OSError 家族，包括 PermissionError/FileExistsError。RuntimeError、ValueError 等非 IO 程序异常继续传播，load_issue 不被 save_issue 混用。
5. notice 先保留原每 ID 或 load 错误前缀，再追加会话保存失败；不以“有效记录仍可使用”把所有 ID 说成有效。

## 已有来源与未知边界

原资料：`/workspace/.continuation/p2-after096-account-metadata-source-survey-v1/source-survey-account-metadata.json`，已保留 Python JSON 官方文档及 RFC 8259 §8.2 原响应。原独审：`/workspace/.continuation/p2-account-persistence-independent-source-review-next-v1/formal-independent-source-review-account-persistence-next-v1.json`，20 项 Source 检查。原 stdlib 探针属于其实际作者，不是这次项目复现；没有为同一已回答问题再跑一轮探针。

原 Source 包把 full095 PASS 写为前置。当前事实是 full095 窗口三次未完成并搁置、已有成果实际提交推送；独立的第 96/97 节可以按用户最新继续指令推进。不得把旧 null 改填 PASS，旧历史包保持原状。实际第 96 节完成和当前源匹配仍由 Root 另验。

不扩展声称：目标已经以 `.tmp` 结尾的任意调用、目标/临时路径别名或符号链接攻击、同时多个写者、磁盘断电持久性、fsync、非 CPython JSON 互操作、非字符串映射键/NaN/循环/非 JSON 对象等旧输入接受与转换问题。新实现保持既有 serializer 政策，不宣称通用任意 Python 值无损持久化；同 ID 旧顶层 extra 的原丢弃行为仍保留。实际 root 权限下 chmod 不是可靠的权限失败夹具。

## Root 实际验收建议

- 先匹配 expected-old 完整字节，应用最小核心和测试，在完成 096 的真实 registry 登记。
- 运行 18 新方法；相关回归至少包含 account_cache_093、training_input_types、target_memory、run_modifiers、run_config_validation、known_recruitment_condition_label、emergency_recruitment_condition 与实际 096 的 condition_cultivation，再跑当前精选。只记录实际计数/原始退出码。
- 实际项目窗口在独立公开临时账户目录确认成功保存与健康重启、合法事实继续计算、两个可见消费者 training_status/operator_summary 的失败信息及本局优先开关。不要读私人 `.local` 内容。
- 真正 IO 失败使用不同 account.tmp 路径上的非空目录阻挡 `write_text`，留原目标和目录 sentinel 的前后字节；它证明实际 open/write OSError，不能被说成实际 mkdir/replace 权限失败。其他 IO 阶段是明确标注的单元注入控制。
- 实际原生 pair 输入使用两个 Python 码点构造；ASCII JSON escaped pair 会被 decoder 合成为正常 scalar，不能冒充该夹具。证据可用 ord-array 描述字符串边界；不要把 ensure_ascii=True 自动认为任意原生 pair 可无损往返。
- 留存完整接受内存、调用方、run state、三种计算报告、目标与临时路径 before/after；普通数据对应数值/文本不改，差异限新增失败状态和提示。截图应实际打开检查。Wine 仍为兼容验证，原生 Windows/游戏/聊天不在本节认证范围。
- 相关与实际窗口检验通过后，按用户本次每节保存指令归档、更新实际断点、commit/push 并查远端等号。本包没有提前计入完成、提交或运行通过。

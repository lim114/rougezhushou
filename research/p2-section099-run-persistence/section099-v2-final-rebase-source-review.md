# 第 99 节 v2 最终重基独立 Source 复核

结论：本次实际读取的最终 v2 基线、候选、组装源码、patch 和 23 方法测试，精确保留声明的第 98 节公开 `run_state.py` 来源，并只运输此前已审的第 99 节持久化增量，未发现新增 Source blocker。本结论只证明重基运输及已审增量一致；没有审称第 98 节整个 tree 合格，没有执行或验收项目、候选、测试、codec、Git、Wine 或窗口。

此前增量说明见 `/workspace/.continuation/section099-v2-increment-independent-source-review.md`（11652 B，SHA256 `8562246d84ea4232dab3d08256e7cb920b567bac201b1da287194d343d04b6c9`）。该历史报告如实保留当时 v2 尚未组装的状态；本报告补充真正生成件的读取复核，不改历史文件。

## 实际文件绑定

| 文件（相对 `/workspace/.continuation/`） | bytes | SHA256 |
|---|---:|---|
| `resume098-run-cache-v2/candidate/rouge/run_state.py` | 51094 | `ca338423cdce026293d0987365eefac7a16fe3769f6b2dff9d4e0faf1b956363` |
| `section099-run-persistence-v2/baseline/rouge/run_state.py` | 51094 | `ca338423cdce026293d0987365eefac7a16fe3769f6b2dff9d4e0faf1b956363` |
| `section099-run-persistence-v2/candidate/rouge/run_state.py` | 53169 | `1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9` |
| `section099-run-persistence-v2/candidate/tests/test_run_persistence_099.py` | 26468 | `e1d3d192811bb5317c5d31ff06466c6a21634e4d25a5494d1dfd7a2b97120eb0` |
| `section099-run-persistence-v2/build_candidate.py` | 8584 | `470358d5ddf40ba9b1843c22b70b5931be67cb0a8da30691c5ba641b8873baa6` |
| `section099-run-persistence-v2/build_candidate_after098.py` | 8584 | `0642513e487a7881632ef5e38c42508c8dcf724259563dfe39f15bf0e9fd55cd` |
| `section099-run-persistence-v2/run-persistence.patch` | 5171 | `3ca8784c0f015b4690832c80e27385cd4172a81d54e75118e8c10997d716b856` |

这些 pins 从真实 bytes 独立计算，未把 `SOURCE_AST_CHECK.json` 的布尔字段当证明。该文件仅作为待核对的作者声明阅读。

## 本次独立实际 Source 检查

实际标准库只读检查工具 chunk `304aa1`，primary exit 0；追加构造函数比较工具 chunk `3f8cf2`，primary exit 0。这两个 0 是 Source 检查返回码，不是项目测试通过或第 99 节运行回执。标准库读取/UTF-8 Source 编解码、AST、difflib、hashlib 和纯字符串操作未导入 rouge，也没有执行两份 assembler。

1. 最终 99 baseline 与声明的最终 98 v2 `run_state.py` 全字节相等；双方长度和 SHA 与上表匹配。没有凭相似方法或文件名宣称等号。
2. 已审 prepared assembler 与 after098 assembler 全字节比较，唯一差异为一次 BASE 路径 `resume098-run-cache-v1/candidate/rouge/run_state.py` → `resume098-run-cache-v2/candidate/rouge/run_state.py`；prepared 文件原 hash 保持不变。
3. 通过 AST 只读取 after098 源中的七个 `change()` literal 字符串对，不执行 assembler、模块或调用目标 helper；每个旧模板在其相应阶段恰好出现一次。把已审纯文本替换重放于实际 baseline，结果全字节精确等于实际 candidate。这证明生成件没有夹带额外改动，不能称为目标运行。
4. RunState 的 existing 方法 AST 差异严格为 `__init__`、`save`、`summary`；唯一新增方法为 `persistence_notice`。其余 13 个原有方法不仅 AST 相同，各自完整函数 Source bytes 也相同，包括 `reset`、`apply` 及所有原本局处理方法。
5. module 的其他顶层 AST 节点相同；`class RunState` 之前整个 raw prefix 全字节相等，涵盖 imports 和最终 98 `_validate_saved_containers` guard。只是运输保留其既有 bytes/AST，没有认证 guard 的全部语义或第 98 节其他文件。
6. 最终 `save`、`summary`、`persistence_notice` 与此前已审 v1 实际 candidate 的对应方法 AST 完全相同。把此前 v1 `__init__` 的 FileNotFoundError handler 换成已审 v2 handler 后，构造函数整体 AST 精确相同；因此 constructor 仅新增已经审过的 lstat 入口分辨，没有另一处变化。
7. source 的基线和候选每一个 LF 都有相应 CRLF；原平台 Source 换行保留。独立生成标准库 unified diff 的结果与实际 patch 全字节相等。
8. 测试文件 bytes/SHA 与先前已审 e1d3d192 pin 相等；AST 仍为 23 个 test_ 方法，测试内容没有重基过程中新增或丢失。没有导入或执行这些测试；符号链接能力不足的明确 skip 仍属于未执行，不得计为真实成功。

## 已审行为和剩余资格

已审增量仍为：独立会话 save_issue；读取坏文件保护与保存失败区分；构造修复 save 移出读错误 handler；OSError 后保持 accepted memory/UI 调用连续、temp 证据不删除；原生 high→low 拒写资格；明确手动新局已改变内存而失败会话 sticky 不自动重试；summary 展示内存与持久化差异；FileNotFoundError 后仅 lstat 确认真不存在才视为新路径，否则保护入口。

serializer 和非 IO 程序错误仍传播；lstat 的非 IO 程序异常传播仍只是静态控制流确认，没有专门运行注入回执。普通数据、孤立 surrogate、native 两码点/scalar/literal 边界的项目验收和真正 IO 故障/窗口验收仍由 Root 实测。账户 97 结果不能替代本节测试。完整保护语义、范围和 23 方法逐项静态观察保留在此前增量报告，不改写成 Runtime。

本次项目 imports/API/测试/fixture codec/Qt/Wine/Git/私人状态读取/仓库写入均为 0；唯一写入是仓库外本报告。没有提前计为第 99 节完成、commit、push、原生 Windows 验证或全量通过。第 95 节窗口搁置状态未改变。

# 第107节 Root 局部应用器 Source

本包为 Source-only。作者只做标准库读取、哈希、JSON/AST、局部字节组合/逆向与 compile(code object)，不 import/exec 产品、helper/codec、测试、Qt、Wine、Git；不运行应用器，不写 tracked 仓库。Source 编译成功不等于测试、Gold 或小节完成。

入口 `root-section107-apply-v1.py` 沿 Root 的 `root-section106-apply-v2.py`（8340B / SHA `0139800132d031597daa2538738325476b233401406088d123f09d8d3fcbcde1`）的执行流程准备。仅 Root 可在独立 Source 审阅与实际107 Gold完成后调用。必须提供三项真实 Linux 路径：`--gold-dir`（含receipt.json）、`--gold-exit`（真实退出码文件）和 `--runner`（该实际 Gold 所用冻结 Source）。未知未来 Gold 文件、runner 或 receipt SHA 不预填、不编造；运行时对实际bytes计算SHA并要求 Gold.runner_sha256 对应，且实际源仍749+CORE。当前窗口契约为13行（8 crossing）；Gold本来没有旧Gold，行内Gold比较标志False不作失败或虚构True。

应用前要求：分支 codex/p2-development，Git本地干净、当前HEAD匹配实际106 publication 的local/remote且commit/push均0；CP completed106/next107/dueFalse；last_full_validation和current_full105_checkpoint完整等于已归档105 closure，真实两次GUI、闭合105、下次110。106完整749 Source图和CORE实际字节必须一致。原107观察保留实际748，不改记为749：固定SHA `0a38276dda0ee3e6640f203cc61397686b6e83c365656578b6896dc461563d00`、raw0、14caller/2preview、74explicit+1loader、89native、0error/blocked与CORE原样。原观测是observations，不是product PASS。

Root授权的唯一写入集合为 `rouge/operator_engine.py` 的既有anchor局部变更、新 `tests/test_aglna_gravity_weight_107.py`、`scripts/verify_cloud.py` 单selector prepend。引擎前SHA `f50e6b992525da0cb3daedb16a3cd4cd45f80052b063007224bd63ac8de93f50` 后 `ff2f1ef07a2df415edb688f6db28916100d912eb79b51faa9d531068f72bff04`；CRLF exact old/new一次、整bytes可逆。AST删除唯一新增weight AugAssign后整个引擎AST必须等于原AST，所有旧函数/断言和原base validator保留。新test SHA `62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c` /13845B/11methods，只编译不执行。

精选注册保持117项原顺序，仅prepend107成为118；其AST除MODULES值外必须相同。**不改**full helper及其NEW_MODULES41：真实 `verify_full_available.py:133–136` 从CORE历史项、NEW_MODULES与cloud MODULES去重union，故新增cloud就覆盖本节，原union240变241且去掉新selector后仍逐项等于旧240顺序。候选 packet 的 full append 提议为此前一般Source建议，Root依据真实 union 流程明确选择无需追加，不机械复制更多改动、不重写该历史候选计划。

应用器逐项验证冻结候选6payload/MF `7e8e213b…`、local `6066dce8…`、consumer独审 `6365cd63…` 与 preview独审 `e53b520b…`；先所有真实receipt/raw/source门、局部完整编译与最后全749+CORE重核，然后Root执行三文件写入。实际应用后的完整维护Source图必须750且只新增测试；旧路径改动只能engine/cloud，full helper与CORE仍全字节相同。它只会生成仓库外 `resume107-applied-source-v1.json`，状态明确 ACTUALLY_APPLIED_RUNTIME_PENDING，记录实际输入Gold/runner SHA和真实新Source图，不宣称后续运行通过、原生Windows、游戏时序、signed floor/clamp或新堆叠机制。

本应用器沿既有Root模式逐文件写入，不新增全局回滚或事务机制；若Root实际写入/后置门失败，真实非零与已有状态须保留、复查，不归档为PASS。Source作者未执行任何该路径，后续产品/窗口/测试/保存/commit/push均仍由Root实际完成。

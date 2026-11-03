# 新测试的未就绪等待边界补充

首次 8 methods 全部通过，产品字节和 60 对矩阵不改。原 tests/log/count/runner 另存 first-eight-pass 原件。为覆盖根要求的 native_attack==0、wait_next_attack=True 但 readyNone 资格，唯一第 8 个方法增加 rate=0＋明确空 initial callback 的 helper 控制；必须保持返回 secondsNone 而不拒绝文本。不是原生时钟证明。

前 7 方法 AST 完全不改；只重跑该新增边界所属方法一次。该方法没有 public API；预算原已授权最多32显式 test-context/helper 请求。原8计23，加该目标方法的9请求刚好32，若实际超限即记录而不隐藏。旧8的19public和60矩阵120public不重复。

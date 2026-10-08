# 尾端实际到达资格（取代上一个 supplement 的 OR 提案）

前一个静态 OR 方案没有执行 API。首 get 已执行不代表 `ready is not None and wait_next_attack` 必然成立，故 native_attack==0、wait_next_attack=True 而未就绪的旧路径应继续 inactive。根独立静核指出此过门禁风险，保留早期方案和原 byte receipt 作准备诊断。

正式方案首 get 仍只按 native_attack>0 记录；在原末端分支内、原 `if attacks` 判断处，对已有原始 value 加 private observer，返回同一个 value 后继续原判断。该 observer 不增加 scenario get，也不评新的 readiness/clock；原 ready/wait 分支实际到达即资格。helper 无 scope 时返回值/短路完全相同。源码 get 清点仍是 12，不把此 observer 命名成第 13 个 get。

固定 60 输入/120 公共调用上限不改。原来源 16 次复现和两个冻结 proposal/supplement 保留。全部时钟及数学原样，旧 error 在成功 core 返回之前优先，finally reset。

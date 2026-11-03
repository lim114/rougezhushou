# 第290节修复后完整复验：独立attempt2准备包

本目录只准备第二次执行工具，尚未freeze、全量或GUI。第一次实际freeze与双archive原字节不改：`verification/full-290/source-freeze.json`、`execution-attempt1`、`p3-supplementary-attempt1`。第一次离线1200秒超时124，没有最终offline JSON；不能从F位置推断具体失败或称全量通过。第一次旧52状态/typed审计、29可用窗口和P3五窗通过只保留其原范围，当前30的实际权限1314不算通过。

attempt2维护同一完整430选择器、1221源路径、42补充公开输入，保留原862断言/552主流程、52typed状态/4283runtime records/156requests/42projection/exact10bridge/26realemptytrace和原current30＋单独29。七份原始proof在draft前已纳入83项legacy工具映射；current工具17项。最终源码SHA由root修复后fresh freeze生成，不沿用第一次源码当修后验收。

只修改本新cache下的执行工具：Windows owned supervisor允许每个作业1800秒，外层controller1890秒；保留真实Popen/job终态/失败归档/不按PID复用猜结束。两个runner没有全局互斥，root必须严格串行、一次执行；前一个全部owned作业终态后才能启动下一个。1800秒仍不是结果保证，若再次超时保留真实失败，不能改成pass。

## root实际执行（生产/测试修复结束且相关必要检查通过后）

保持分支`codex/p2-development`和当前HEAD。执行期间不得修改maintained源码/tests/scripts、四个公开research包、两份prior源或这9个controller。root须先给`verify_full_available.py`增加可选`--verbosity`，默认1不变；attempt2 wrapper显式用`--verbosity 2`。freeze producer会拒绝未提供该选项的源码，不自行修生产。

```powershell
$full290RepairParent = (git rev-parse HEAD).Trim()
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/produce_final_freeze_290.py --declare-root-final290 --expected-parent-commit $full290RepairParent
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/run_full290_orchestration.py --execute --activate --expected-parent-commit $full290RepairParent
```

producer只生成`verification/full-290/source-freeze-repair.json`，其中actual_validation_attempt=2，绑定A1来源SHA、全新源码/selector集合、额外公开输入和9个执行器SHA。其后依次完整离线、旧52状态、current30、单独current29。第二条stdout给出真实`rouge-full290-repair-<uuid>`路径，保存为`$full290RepairOut`。不要猜路径，不要因工具yield重复启动；保留实际shell会话继续读取。controller退出0只表示四作业均终态，不表示全部测试通过。

四主完全终态后再执行五个额外canonical实际窗口：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/run_p3_supplementary_windows_290.py --execute --expected-parent-commit $full290RepairParent
```

记录其真实`rouge-full290-repair-p3-<uuid>`路径为`$full290RepairP3Out`。286/288/289/290保留15秒可见时限与脚本最低步骤时限，287保留30秒。检查286–290所有实际raw结果及新截图；不能用A1截图/通过数替代A2。两runner每步骤前后验证新freeze、controller、bound supervisor工具、完整资料输入；不替代旧52/current30＋29。

## 原完整typed审计与双归档

旧typed审计工具原字节不改，显式读取A2实际namespace；保存实际stdout/stderr/readback.exit与真实process信息：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/legacy/audit_full261_saved_readback.py --root 'C:\Users\李娜\Desktop\lcn\rouge' --container (Join-Path $full290RepairOut 'legacy') --bundle 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-repair-prep\legacy' --freeze 'C:\Users\李娜\Desktop\lcn\rouge\verification\full-290\source-freeze-repair.json'
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/archive_full290_outputs.py --seal-actual-outputs --container $full290RepairOut --expected-parent-commit $full290RepairParent
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-repair-prep/archive_p3_supplementary_290.py --seal-actual-outputs --container $full290RepairP3Out --expected-parent-commit $full290RepairParent
```

新归档目的地只能为`verification/full-290/execution-attempt2`与`p3-supplementary-attempt2`，不覆盖attempt1。归档成功不自动产生PASS总结；actual source、退出、失败详情、typed52、当前30权限/29范围、五窗与实际新PNG目视全部核实后才能形成最终summary。

当前Windows准备期inventory实际WSL退出1、无wine/wine64、用户权限symlink WinError1314；Linux/Wine、原历史Windows/私有样本/真实符号链接、游戏/聊天均不得计通过。当前原生窗口只证明其隔离公开数据与实际Windows UI范围，私人局记录/配置/聊天绑定不读不改。

290是定期全量而不是新数字停止目标。此attempt2不增加功能节数，不自动授权后续工作；用户最新要求/根代理控制后续范围。

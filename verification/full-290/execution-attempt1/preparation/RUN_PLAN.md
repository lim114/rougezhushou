# 第290节完整可用范围验收：准备就绪，尚未执行

此目录是全新的独立290执行命名空间。full285的实际回执不可改名作290通过。285包含离线/当前窗口第一次与旧窗口第二次的组合验收，不是一次全绿。原275执行工具仍是旧窗口断言和流程的历史准据；本目录只重新绑定当前源码、完整选择器、补充公开输入及当前原生执行权限。没有启动全量、GUI、游戏、聊天或读取私人状态。两个执行器没有全局互斥锁；root必须严格串行、只启动一次，并在前一个执行器全部owned job终态后才启动后一个。

当前预检：保留full285全部419个选择器及1193个源路径，增加286–290的11个模块，观察到430选择器/1221个维护源文件/42个补充公开输入。最终数量由root冻结时重新读取，准备数量不是测试执行数量。七份expected-map原始proof在draft前已逐字复制并纳入legacy83个工具的SHA映射；current17个工具，862条断言、552条主流程、原生成器/观察函数与30/29窗口断言均保留。

本机只验证当前Windows。环境预检实际WSL退出1、Wine/wine64缺失，用户权限符号链接实际WinError1314。不得转换成Linux/Wine/原Windows历史/私有样本/真实符号链接通过；30项仍须实际尝试，29项单独完整执行。旧游戏或聊天历史不在当前原生窗口通过的证据中。

## root执行入口

仅在290生产、全部新增测试、五个canonical窗口脚本及全部公开资料稳定后，使用当前项目的原生Python。不要重复执行`--prepare`，不要对本目录再次覆盖draft。Root必须保持当前分支与HEAD，执行期间不能修改生产、tests、scripts、四个资料包或两个prior源文件。

```powershell
$full290Parent = (git rev-parse HEAD).Trim()
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/produce_final_freeze_290.py --declare-root-final290 --expected-parent-commit $full290Parent
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/run_full290_orchestration.py --execute --activate --expected-parent-commit $full290Parent
```

第一条只生成`verification/full-290/source-freeze.json`，不启动测试。第二条只绑定一次，然后依次执行：完整维护离线union → 原52状态旧窗口 → 原30项当前窗口 → 单独29项当前窗口。每一步保留实际Popen、Windows owned-job终态、stdout/stderr及真实退出文件。已经终态的非零结果会保留并继续独立步骤；可能仍运行的job会阻止后续或重复启动。运行器退出0只表示四步骤已终态，不是四项全过。

其stdout第一行提供实际临时路径`$full290Out`，例如`C:\Users\...\Temp\rouge-full290-真实随机值`。不要手工编造路径、PID或退出结果。长任务需保留shell会话并继续读取，不要因一次工具yield而重启。

补充286–290五个实际窗口，与上述同一freeze顺序执行：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/run_p3_supplementary_windows_290.py --execute --expected-parent-commit $full290Parent
```

其stdout给出独立真实临时路径`$full290P3Out`。五个canonical脚本分别验证普通/技术详情与阅读状态、恶笼草等级奖励边界、三关固定格中心与三尺寸/刷新/未知不画、沉寂之屋两具名奖励资源边界、临时中介所四种招募结果卡与条件分类。它们不替代52状态或30/29。286/288/289/290使用15秒可见时限并保留各自原步骤/最低时限；287保留原30秒时限。新截图必须实际检查，不以历史图像替代。

## 原始完整typed readback与归档

四主步骤终态后，原审计工具使用明确参数读取新actual，不改工具/源结果。必须保持真实stdout/stderr/退出码：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/legacy/audit_full261_saved_readback.py --root 'C:\Users\李娜\Desktop\lcn\rouge' --container (Join-Path $full290Out 'legacy') --bundle 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-prep\legacy' --freeze 'C:\Users\李娜\Desktop\lcn\rouge\verification\full-290\source-freeze.json'
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/archive_full290_outputs.py --seal-actual-outputs --container $full290Out --expected-parent-commit $full290Parent
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-prep/archive_p3_supplementary_290.py --seal-actual-outputs --container $full290P3Out --expected-parent-commit $full290Parent
```

实际archive目的地分别为`verification/full-290/execution-attempt1`和`verification/full-290/p3-supplementary-attempt1`。默认要求所有步骤真实终态；非零原始失败也可归档，但不自动声称通过。若需要重试，先保留实际失败与源码并准备独立新attempt，不覆盖此目录。

原auditor历史261标签保持不改，需另加当前290来源/冻结/原生执行的标签解释。应核对52typed状态/156请求/4283条记录=4281通过标志+2元数据、42投影、准确10个bridge索引18/19/20/21/38/39/40/41/44/45及26条真实空trace，且862/552原范围不变。当前30的1314不可计pass；29独立pass只能证明其可用范围。离线实际parent/subcase/pass/skip/U/fail/error需以新回执读取，旧4684/4605/73/16/6不是290应达到的硬编码结果。

额外公开输入包括四个指定research目录所有regular文件及两个原prior源文件，独立于维护API source_sha256保存在`supplemental_public_inputs_sha256`。producer、controller每步前后、native/offline闭合和archive校验它们；源档案同时封存这些原字节。不得把它们混进维护选择器或掩盖原维护source范围。

## 准备期原始记录

`orchestration-preparation-check-290-ready.json`是最终静态准备检查，不是全量通过。此前两个通过的准备回执各自保留其当时controller pins，不与最终pins混用。`static-check-observed.*`与`check_preparation_290-first.py`保留准备器首次可观察失败：错误地将原完整method selector当模块文件路径；已改为静态逐层解析原模块/类/方法，完整选择器字符串未改。另一次初始工具yield未保留终端尾声，不冒称其原始退出或输出。没有因此运行/删减任何产品测试。

`environment-inventory-290.json`、`game-window-prerequisite-290.json`和`draft-preservation-290.json`只证明准备期事实。桌面或权限变更后需要重新检查适用条件，不能推断游戏已关闭或授予权限。

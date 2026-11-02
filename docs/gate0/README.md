# Gate 0 本地记录

先关闭上一份助手，再使用本项目虚拟环境运行：

```powershell
.venv\Scripts\python.exe -B -X utf8 scripts/run_gate0_session.py --scenario normal --auto-sample
```

`normal`、`transitions`、`resize`分别记录正常流程、转场动画、缩放遮挡；默认600秒，结束后助手继续运行。一次只启动一份助手。游戏由玩家正常操作；不需填写游戏数值。录屏由玩家使用现有工具完成，保留同一会话的起止时间，录像与日志只留本机。采集前核对难度、分队和当前局；未读字段按原有记忆规则处理。

文件位于`.local/gate0/时间-场景-随机号/events.jsonl`。运行结束后生成摘要：

```powershell
.venv\Scripts\python.exe -B -X utf8 scripts/gate0_report.py .local/gate0/对应目录
```

| 记录 | 字段与用途 |
| --- | --- |
| session_start/end | 场景、起止时间、版本口径；确认记录是否完整 |
| state_baseline | 本局配置、资源、队伍、藏品、战术道具的初始可用字段 |
| sample | 采样序号/代次、页面、帧时间、是否应用及原因、上述状态变化、地图/作战身份、现有识别分段耗时与界面更新时间 |
| sample_failure | 采样或识别失败原因；不记录聊天错误 |
| overlay | 当前判定原因、参考/新帧年龄、锚点数、当前显示状态、判定耗时；变化时及每秒记录，未接候选算法时would_show为空 |
| surfaces | 助手可见顶层界面、Qt类型、归属、窗口位置、缩放比、焦点属性、当前工作区类型；变化时记录 |

不保存画面、原始OCR、笔记、聊天、密钥。当前选项仅显式启动时生效，不改私人设置或清空本局。日志本地保留至Gate 0复核后由用户手动清理。开发用合成数据在临时目录验证，真实记录不进入公开验收或Git。

录像对照需标注：时间点、实际页面/关卡/节点、对应日志序号、读对/漏读/误标、更新与撤下时间。程序摘要只统计观察，不自行生成准确率或宣布门禁通过。

定向场景：静态停留60秒；少节点页面；窗口缩放后恢复。记录当前表现，不在Gate 0里提前修改显示门槛。入口清单以运行时可见窗口为准，不按源码文件或标题调用数推算。

同一输入的记录开销复放：

```powershell
.venv\Scripts\python.exe -B -X utf8 scripts/benchmark_gate0_recording.py .local/gate0/对应目录/events.jsonl
```

结果测量记录路径的格式化、入队与队列排空；捕获和OCR耗时由原会话另行核对。预热后交替开启/关闭记录，输出中位数和p95。

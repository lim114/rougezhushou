# 第290节最终A3组合回执与收尾：仅准备

本方案未执行summary builder或收尾helper，没有写正式summary、CP、要求或索引，没有启动测试、GUI、冻结或新尝试。root拥有所有实际执行与正式接纳。

## 固定输入与差异

- 最终冻结：`verification/full-290/source-freeze-final-A3.json`，SHA `ad3842c95c4a4eadb6779611a337fbeb26c2682a25d6ed83945dcf7a0a8d65f7`。
- preparation：`cb31c0b40cf6c51a530df369c43ea56ee63040ecb301102d832a319206975852`；activation：`4004536750136cf95748a41f20ab8354833b6db96c12457f8e354595ba3b075b`。
- 与A2 source75有**两处**精确非生产差异：第6个测试3523d3…→0eb99b…（默认玩家文案及额外technical断言）；完整离线runner857339…→bb66e4…（仅最终报告在Windows使用sys.platform映射，仍输出Windows）。其余1219完整源码、430有序选择器、42补充输入不变。
- legacy native1221路径集合仍单独包含offline_scope_retirement而非CORE；additional86补充输入完整保留。current窗口的历史map是A2 full1221。不可把相等数量当相同路径集合。
- 最终工具18、immutable template84、actual bound84全部按实际freeze/activation逐个核对。计时与可选非WMI元数据属于验收工具维护，862断言、552原maintry、数值/资格/选择器范围保持，不是旧崩溃根因证明。

新offline3和legacy4/原typed共享最终冻结；A2 current/P3保留A2真实冻结。没有一个实际单次进程执行了所有历史范围，不能写“同一次同源全绿”或“A2运行最终完整源码”。A2 GUI完整map记录了两处旧非生产文件，但其GUI入口并未执行完整离线报告入口；复用需要这两处精确变动与调用入口边界，不能仅凭哈希推断任意方法未执行。

## 最终真实结果门槛

以下全部必需；未齐或失败就拒绝生成candidate，不能用进度、准备1575、旧A1/A2/retry3结果代替：

1. `offline-attempt3`和`legacy-retry-attempt4`成功归档，manifest为`FULL290_FINAL_A3_EXACT_SEGMENT_ARCHIVE`，与实际新namespace/owned process/freeze/activation绑定。
2. 新offline实际Popen/child/supervisor0、3600秒deadline无超时、job关闭、完整430选择器JSON与closure一致、失败错误0，QT实际清理。通过/跳过/不可用父项与子项分开，从实际JSON读数。
3. 新legacy4实际Popen/child/supervisor0、3690秒deadline无超时、job关闭；52状态/4283记录/862断言/552maintry/42原投影/精确10/26真空trace/52伤害与156文本请求的完整原范围。
4. 原未改字节typed auditor在独立120秒job实际0，输入是该次legacy4和finalA3 freeze。结果在`legacy/independent-saved-readback-audit.json`，进程原件在`readback/*`，不能借旧A1/A2或不存在的legacy/readback.exit。
5. A2 current30的真实1314保持不可用，独立current29实际29通过；五P3仍用真实A2回执。其实际数字从各自schema读取，不把独特标签与重复断言执行相加。
6. fresh最终源15方法必要检查使用`290-necessary-final-A3/process.json`真实4607e752…及日志。它覆盖356声明源码，并非全部1221；不把旧15再加一遍。历史46、展示69、fresh15、全量和各窗口计数各自保留。
7. A1/A2超时、A2内部1200旧窗口超时、retry3原生失败、追加更正都保留原件和manifest；retry3最终栈在1329复合调用，不能误写finally/WMI为最终根因。

## root人工PNG审核

已存在的A2审核直接读取：
`verification/sections/290-preparation/root-A2-p3-current-visual-review.json`，SHA `a8e08cbac02ec97610157eb0b71fc3325d74d25d713d17f7ff0de1ec6f00af7c`。31实际路径、24独立直接查看图与7完全同SHA复用分开；current30图片审核不改变其失败。

未来final legacy4四张实际PNG需root另存人工审核。当前reader约定：

```json
{
  "kind": "root_manual_visual_review_not_test_execution",
  "validation_segment": "legacy",
  "actual_legacy_execution_ordinal": 4,
  "source_freeze_sha256": "ad3842c95c4a4eadb6779611a337fbeb26c2682a25d6ed83945dcf7a0a8d65f7",
  "full_validation_pass_claimed": false,
  "images": [
    {"relative_path": "legacy/actual/<实际PNG文件名>", "sha256": "<实际SHA>", "review": "<root实际观察>"}
  ]
}
```

必须恰好四张该次图，不填A1/A2图。准备脚本不会自动创建人工结论。如果root实际采用不同schema，仅适配读取真实记录，不要求重新制造观察。

## 实际证据齐全后才可由root运行

下面命令仍未运行，placeholder必须换为真实已审核路径：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-summary-prep/build_final_A3_summary_candidate.py --A2-visual-review 'C:\Users\李娜\Desktop\lcn\rouge\verification\sections\290-preparation\root-A2-p3-current-visual-review.json' --legacy-visual-review '<root实际legacy4审核JSON绝对路径>' --output 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-summary-prep\summary-final-A3-candidate.json' --proof-output 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-summary-prep\proof-final-A3-candidate.json'
```

只准写cache新文件且不覆盖。root审查后，proof原字节保存到`verification/full-290/composite-admissibility.json`；summary移除cache-only candidate标记后保存到`verification/full-290/summary.json`，proof SHA及其余事实保持。

原项目测试窗口正常更新打开、真实可见响应/置前回执和5私人路径只比较哈希且未变/未恢复内容齐全后，root才能调用新helper：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/close_section_290_final_A3.py
# 先审查严格gate和preview，再显式写入：
.\.venv\Scripts\python.exe -X utf8 .cache/close_section_290_final_A3.py --apply
```

helper重新核正式proof、冻结/工具/归档SHA、fresh15及历史必要证据，再构造所有文本；采用UTF8二进制字节写入，不以Windows换行转换制造整文件diff。旧helper及旧严格草案均保留，不执行。

功能收尾仍是第290节：四种替代招募职业结果，不是4份同时领取；直升已查证为初招已进阶，实际选择/费用/培养/领取/原入口仍未知，25/57原入口缺口不减。P3/P2/P1未完成，识别最后，只提供路线节点信息。下一291未启动，下一定期全量305（125锚点每15节），没有新数字终点。完整repository、真实1314、Linux/Wine、历史原Windows私样本及游戏聊天不冒充通过。索引、普通提交/推送和远端核对由root完成。

# Root人工截图审核输入合同

由root在A2新截图实际逐张目视后另存JSON；构建器不会生成或填充审核事实。将文件路径传给`--root-visual-review`。

必需顶层字段：`kind="ROOT_FULL290_ATTEMPT2_PNG_REVIEW"`、`reviewer="root"`、`actual_validation_attempt=2`、`source_freeze_sha256`为repair freeze真实SHA、`all_actual_images_individually_reviewed=true`。

`images`必须是数组，恰好覆盖两个attempt2 archive的所有`*/actual/*.png`（四张legacy、全部五P3截图，以及实际存在的current图片）。每项需`file`为项目相对A2归档路径、`sha256`、`reviewed=true`、`acceptable=true`、非空`observation`。不能用A1路径，即使新旧图片字节相同也要确认新A2实际归档图片。

在四主/五补充终态、typed审计和双archive封存且人工review完成后，root才可显式运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 .cache/p3-full290-summary-prep/build_summary_candidate.py --root-visual-review 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-summary-prep\root-visual-review.json' --output 'C:\Users\李娜\Desktop\lcn\rouge\.cache\p3-full290-summary-prep\summary-candidate.json'
```

此命令现在只作计划，准备代理没有执行它。缺文件、原始失败、来源/退出/typed/人工审核缺口会拒绝生成；输出只允许本cache目录且不可覆盖。生成candidate也不写public、CP、docs或index，最终发布仍由root审查授权。

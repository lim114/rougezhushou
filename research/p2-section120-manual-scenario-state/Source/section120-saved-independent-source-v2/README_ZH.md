# 第120节 Saved v2 独立 Source 审阅

绑定作者 Saved v2 MANIFEST：1269 B，SHA256 `bb00de42fd661c3f6d11f23c422ae333b492d430efc48baaf0be5fcd44b8c4e5`。同时复核完整窗口v1和未修改的Saved v1封存。

Source未发现剩余实质阻塞。v2修正了显式calculate区间误排后续重算、原始profile截图错绑修改前editor状态、API/GUI逐字段比较漏掉跨字段alias、API formatter前后input/result图分拆四项问题。38个快照、14组窗口流程、6个公开API和6个合法GUI原/新对照仍绑定真实窗口Source；未改产品或窗口runner。

本审阅逐项核对8+6+6项有效负载哈希、完整清单、固定runner/helper/formatter Source和公开API字典。仅std Source读取、AST和compile-noexec，未运行或导入项目、Saved、helper、Qt/Wine/native，未读取或解码gzip、未读私态、未调用Git或改tracked文件。

Root仍须实际执行Saved v2并单独观看PNG。原始phase的观察完成和process0不构成产品PASS；候选真实验收完成后才能报告PASS。Saved不核像素，不虚构缺失的timing父viewport几何或第二次MainWindow重启。

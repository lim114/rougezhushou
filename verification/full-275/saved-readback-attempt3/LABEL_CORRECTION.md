# A3 审计标签更正

原 `independent-full275-saved-readback-summary.json` 的 `kind` 字符串误沿用 A2 模板；正确标签为 `INDEPENDENT_FULL275_NATIVE_ATTEMPT3_SAVED_READBACK`。原回执 `actual_native_attempt` 已明确为 3，实际输入来自 A3，可信读回工具真实退出 0，未复用 A2 通过结果。

原 summary SHA256：`7756177db3eaac979879d6cdf85f75b55b5f2d4ee95e1155d8ca23d2130f4f50`。完整 A3 输入 SHA、1160 源冻结和实际进程退出依据见 `label-correction.json`。该补充仅更正标签说明，原回执及实际输入/输出字节均未改动；当前 30 项中的 WinError1314 权限失败仍保留，未计为通过。

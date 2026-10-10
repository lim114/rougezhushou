# 第122节 Saved 独立 Source 审阅

结论：封存提案无剩余 Source 阻塞，可由 Root 执行实际验证。本审阅只读公开源码和 JSON，使用 stdlib 文件/hash/AST/compile-noexec；项目、API、tests、Qt、Wine、native/helper、Saved、gzip 解码和 Git 执行均为 0，私态读取和 tracked 修改均为 0。所有后述核验均是源码协议核验，不代表第122节 Runtime 已通过。

精确作者包为 /workspace/.continuation/section122-saved-source-v1/MANIFEST.json，2106 B，SHA256 1e9edcc9ff2c816794e257261283cfd808c4191ff8b6563be59b28a396af63cd。9 payload 与实际物理目录逐项 hash/长度及 0444 权限核对一致；全读的审计源码共 882 行、53728 B，SHA256 e95622dbcd57dc8089b6cf4819d8ad1d746c496011d552365a038fa7b600516b，独立保存快照与封存作者源码原 bytes 完全相同。

审阅所绑定的窗口 Source MF 为 6e3d3d1e4843a82087b8fdc12b9ac6245d53ab25b6210d45167f2050d3bc5736；runner 为 83e96b323101d93d70c24a04f2e6519f3659ccac5f04f6475e88709ef41c54e7，cases 为 ba420ec06d02f9476814a4b3da0b2b353a1703cfaa9885f464164c41be7af6e1，native helper 为 f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a。Saved 的 cases、完整公开机制引用、helper 和复制窗口 MF 均与封存窗口原件 bytes 一致。Source 绑定没有未来 HEAD、执行路径、Source count 或预填 PASS。

## 核验内容

1. **原始记录账本。** NativeLedger 检查严格完整 refs 字段、类型、顺序文件名、实际 records 文件集合、每个压缩原件 hash/长度、解码 hash/长度/protocol 和 kind/context/case/phase 回显。get 使用整个 ref 的 native 等价，不仅比较 path。Root 实际执行时复制原始压缩 bytes，保留完整证据；独审没有解码记录。f040 源码的 exact builtins、dict/list 顺序、float bits/负零和双向 container alias 校验已纳入协议。

2. **完整计算与报告图。** 42 个快照各绑定七个相邻完整记录。numeric 原调用前后、原返回值、GUI wrapper、scenario caller、public state/raw disks 与 fresh API 完整图联合比较，保留跨字段 alias。fresh API caller/result 图与原 GUI 图精确对应。三种 formatter 的整个 caller/result/state 图及全部 126 个文本一起核验，普通显示全文与正常 formatter 字符串相同；所有普通路径 state/raw disks 不变。技术切换前后完整图及普通恢复全文有独立记录；技术中间 QTextEdit 字符串没有另存，文档与 receipt 明确只由精确 producer 的运行断言和原始 0 退出码绑定该显示，不夸大 Saved 覆盖。

3. **明确 mutation 与 ordinary 读取分离。** current joint 只能在 13 个 actual_ingress_begin/end 对之间推进。每对完整 public caller 前后不变、before 与此前 joint 完全相同、账号内存及原盘不变；区间内只允许该次更新产生的 reentrant numeric 记录，且其 joint 必须等于 end.after。没有按 phase/case 广泛豁免。所有区间外 UI、API、formatter、snapshot、PNG 和 close 均守当前完整 joint。磁盘只有公开 run/account，保存 run 原 bytes 与现有 JSON producer 的换行/编码格式精确对应，不把 JSON 原盘当作保留 native alias 的证据。

4. **资格边界与保留事实。** 公开初始输入从 cases 独立推导六组 constructor 后 run/account、完整 extras、原 -0.0/None 及 raw disks。unknown held/present 排除自动 held、recruited 和已招募总览，但保留原始 member/held/培养/来源/强化/计数事实。未知或 False 时真实 MainWindow 仍保留旧手动 catalog 默认 kaltsit。identity-only 确认只恢复身份，不让旧 rank/source/advanced/recipient buffs/counter 复活。fresh level、培养字段、rank、origin、advanced、partial popup、完整空 popup、fresh counter 分别核验；资格历史的 previous_record 与对应完整旧记录一致，不伪造 recruit/departure/held loss/classification/promotion。healthy exact True/False 和缺失 flags 按现有契约作负控。

5. **等级与计数精度。** 初始 unknown 得到账号已知 rank3，默认 account_reference3；identity-only 的本局 rank 被遮罩时，默认 preview_unconfirmed10，账号 checkbox 为 manual_account_reference3，取消回到 10。健康 True/missing 保持 rank7。旧完整 altar proof 留在原盘但不进入 qualified projection；fresh counter 的完整 value/source/title/rune/box/evidence/at 从封存 observation 独立推导并与新原盘记录核验，各快照 projection 与 stored 完整 proof 相同，计算 caller 只接收 value 标量。没有只核数值而忽略原证据。

6. **重载与截图。** 六次实际 close 不改变当前完整 joint，并绑定 RunState 与 AccountCache 直接重载。restart 独立从精确持久化 JSON 与 constructor 的 RUN_KEYS 顺序/restore notice 推导；JSON 会打断 live alias，因此不对 reload 伪造 live alias 保留。六个账号完整图及原始文件均检查。两幅 PNG 绑定实际连续快照 full ref、完整 joint/result、原 bytes/hash/IHDR 尺寸和有界 QLabel 或连续报告 metric 几何。仅声明被命名区域，Root 需另行查看原图像素。

7. **Source 原件、时限与封档。** 审计器先核自己的整个封包及实际 producer 的整个封包，再核本次 Root guard 的 section/count/完整 Source map 和 CORE。窗口原始 exit 必须为 bytes 0\n，receipt 必须 actual passed/workflow、无错误/漂移且 900 秒内完成。Saved 有 180 秒 watchdog，组级 checkpoint flush/fsync；异常保留 false/原异常，最后重新读取全部输入并核 Source/CORE 稳定。输出位于 checkout、Source 提案和实际窗口原件目录之外。两个 Python 原件 AST/compile-noexec 通过，13 个 import 仅 stdlib 与固定 native helper，独审未执行任何所生成 code object。

8. **公开资料准确性。** 实际 public operator-profiles.json 1592209 B/82b870fa4a780d626f57a18aa12f8a5bf6626c5a350b4a83499fd12518f8c957，relic-mechanics.json 500847 B/6ee8d52cbaffdb0ec79a1ab44689e0bd1ef43364f6ddb3b2e4f2c80afbfe6f47 已核原 bytes。完整 relic/recipient dictionary 以及 S3 rank7/rank10 引文逐节点 exact JSON type/order/float bits 与原件一致。rank10 原 SP35、rank7 原 SP41；零食盒现有 0.8 因子产生 28.0，相关断言以有限 numeric 值核公式输入、整图核实际返回类型，没有发明新游戏 stacking 或来源机制。

## 审阅中已修正的 Source 问题

- caller、GUI wrapper.scenario 与 joint/result 的跨字段关系改为完整图比较，防止独立字段等值掩盖 alias 差异。
- 初始 unknown/False 的 kaltsit 手动 catalog 默认与真实 constructor 一致，不再错误要求没有 operator。
- fresh counter 检查整份重新确认记录以及其进入各 snapshot 的 qualified projection，而非只核资源 scalar。
- UI 记录 key order 是 joint→damage_result，formatter 是 damage_result→joint，分别建立相符 expected 图，再使用共同顺序的完整 joint projection 比较；没有强行抹除类型/顺序差异。
- JSON reload 预期由实际持久化解析推导，Source rank erratum 与初始账号分支明确保存，SP28.0 的实际 float 不改写为 int。

这些修正已包含在当前 e95622… 完整审阅源码内。最后首封只更改 README/source-checks 的封存状态，代码和其他原件未变；最终 MF 与全 payload 已重新回核。

Root 下一步：按当前实际 Source 重新绑定应用第122节并生成本次 guard/count，运行固定窗口 runner，保存原始 exit/receipt/native records，再在这些原件上运行固定 Saved 审计器并查看两幅原图。实际测试、批次全量、commit 与 push 的结果由 Root 分别报告。当前独审不声称上述实际操作已完成。

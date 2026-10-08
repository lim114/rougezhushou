# 古米 Back · 公开来源读取（087 前置研究）

本包是外部 source operation，没有产品补丁、产品草稿、应用计算、应用 helper、测试、Qt、Wine 或 tracked 改动；不作为本代理完成的编号小节。

固定资源提交 `d0b5af0b004b044d322397ce5ae79632b6d9fcdd`。标准 Git HTTPS 的 `blob:none` 获取了目录及提交信息，随后仅取得 Front、Back 两个 blob。Front 为 90,939 字节，SHA-256 `7bf9d7e014bf3402043639d4c348ca2409e89c7ab4cb0d794c52f4278d5c9d04`，与现存生产记录一致。Back 为 32,563 字节，SHA-256 `09526db9b53f6fa54ac51219ce31e6cd3903e618d9a47781f230bf68de3edfb2`，Git blob `473df5c69d7e3552f6937f749bd42dd9e974ca01`；路径、对象大小及本地 blob 重算均一致。这是新获取的文件，不是恢复旧 cache。

两文件实际头部都是 Spine `3.8.99`。官方 Spine Runtimes `3.8` ref 固定为 `8b4844bd4b193ba9e54487ed397a777993cbad56`，官方 README、LICENSE、reader、接口及自带 `spine-core.js` 均保留来源与 hash。官方 README 声明 3.8.xx 的 core bundle 自包含，无需编译。本研究未修改 reader。AttachmentLoader 创建六类官方对象，Region/Mesh 使用官方默认 TextureRegion，仅支持读取资料；未获取 atlas 或图像，UV、offset、纹理和渲染不作验收。LICENSE 与源码原始许可头完整保留；本包没有把 runtime 集成进产品。

恰好调用官方 `readSkeletonData` 两次，均首次成功：Front 47 骨骼、49 槽位、9 动画；Back 34 骨骼、28 槽位、5 动画。Front 的版本、原始时长、事件名/秒数、来源 bytes/SHA/blob 与旧 9 条生产记录逐项精确一致，完成保存结果控制比较后才读取 Back。两个输入内存及资源文件在读取前后的 SHA-256 不变。

Back 实际只有 `Attack`、`Default`、`Idle`、`Skill`、`Start`。Attack、Skill 各有一个 OnAttack，可满足现有 source builder 的保守资料条件，形成两个有来源的候选。保留 literal `Skill`：它没有技能编号，现有 `choices` 正则不会因此开放某个技能选项，不能绑到 S1/S2。Attack 也只是可选局外动作参考，实际普攻绑定未知。两个候选与实际 UI 开放数量分开；本研究没有运行 choices 或 UI，没有测 UI 数量。Back 没有 Die 或 Skill_2_*，没有借 Front 补位。

历史可见失败下界为 1，生产记录是 `Error: boneData cannot be null.`。旧 timing-048 缓存、reader 和实际尝试日志没有迁入，旧总次数、reader 身份及报错根因仍未知。新的成功不能证明旧错误为何发生。官方 SlotData 的报错入口已按源码保留，只证明这个错误文本对应的官方入口，不宣称旧调用一定走了该版本。

未证明最终读取偏移/EOF、atlas/render、当前热更新、皮肤、normal/skill 原生绑定、碰撞、首伤/受疗、实际结束、回转、SP、空转、周期或 native 事件顺序。输出的秒数是源动画事件资料。

网络沿用当前 proxy/CA 和正常 TLS。Git 的 sslVerify 未设为 false，GIT_SSL_NO_VERIFY 不启用。当前环境 running/connected，network policy 状态观测为 unknown，不声称 enforced。主资源 GitHub API 的一次 CONNECT 403 与官方 API 的一次 CONNECT 403 均属于准备拒绝，未取得资源且未解析；停止该 host 后使用独立允许的 Git HTTPS，不修改网络策略。官方 source 路径 404 和一次 acquire patch 格式准备错误分别保留，均没有消耗解析失败预算。两次 optional 本地路径查询非零及未执行 runner 的接口预审修正也单列；没有产品失败。

断点：保存结果已足够交根代理审查。无需再下载或解析，也不需要全 64 文件重跑。后续产品阶段只能由根代理另行启动，以原始 5 条 Back 资料和两个保守候选为依据，继续保留上述未知。新的同一解析问题如达到 3 次失败必须 defer；本包新的失败数为 0。

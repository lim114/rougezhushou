# 古米 Back 官方读取器来源与研究加载方法

官方仓库 `https://github.com/EsotericSoftware/spine-runtimes` 的 `refs/heads/3.8` 经标准Git HTTPS固定到 `8b4844bd4b193ba9e54487ed397a777993cbad56`。所有下载都使用该完整SHA的原始文件地址及标准TLS，保留代理；没有第三方bundle、git缓存重建或产品改动。

`spine-ts/README.md` 明确“spine-ts works with data exported from Spine 3.8.xx”，并说明 `build/spine-core.js` 自包含core、无需渲染backend。已取得该官方bundle，299442字节，SHA `f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1`。本代理没有执行bundle、编译或完整骨骼解析。父资源header回执确认新Front和Back均为3.8.99；这闭合版本家族来源，不证明Back载荷有效或解析成功。

官方 `SkeletonBinary.ts` 先从真实二进制读取hash/version，然后按载荷创建BoneData，SlotData使用载荷中的骨索引。官方SlotData构造器在骨对象为空时原样抛出 `boneData cannot be null.`。不更换、增补或排列骨/slot，不改二进制reader，不拦截该错误。私有BinaryInput以 `DataView(data.buffer)` 读取，父应将文件Buffer转换为独立的 `Uint8Array.from(buffer)`，避免把有byteOffset的Buffer池前缀当载荷；原文件字节与reader保持不变。

3.8 core中未发现名为HeadlessAttachmentLoader的对象。官方真实接口在 `core/src/attachments/AttachmentLoader.ts`，允许实现自定义factory。本目录 `research_attachment_factory087.js` 导出 `createLoader(spine)`，六个方法全部创建官方附件对象，不返回null或跳过附件。Region使用官方 `setRegion(new TextureRegion())`，Mesh使用官方默认TextureRegion，其零字段不改成虚构尺寸或texture。

默认region仅使reader可以消费整个附件payload。Region派生offset可能非有限值，Mesh派生UV不代表图谱数据；这些不是提取或发布的结果。没有texture、atlas、视觉几何、渲染有效性证明。动画时长/事件读取使用实际timeline frames和eventData；deform使用真实载荷的attachment bones/vertices，不依赖region UV/offset。本方法既不调用动画apply、world-transform或renderer，也不把文件内事件时刻当实际游戏绑定或技能时钟。

建议父统一执行：先核官方bundle/factory/两resource SHA，再加载未修改官方core和上述factory，以独立Uint8Array调用原 `new spine.SkeletonBinary(createLoader(spine)).readSkeletonData(bytes)`。先Front一次与旧9条时长/事件精确比对；仅在Front通过后才Back一次。保存全部异常与提取值、调用计数、版本和资源身份；reader返回不等于已验证EOF、视觉或当前客户端。解析预算由父维护，历史同问题次数未闭合前不启动。

许可是自定义Spine Runtimes License，不是MIT。已保存root LICENSE（2019-05-01）及reader源文件头的2020-01-01全文；README允许免费评估，同时给出涉及产品集成/再分发的Spine Editor许可条件。本轮只在仓库外保存研究材料，没有把runtime集成进产品或作许可资格推断。

准备诊断各自保存：api.github.com的标准TLS元数据403一次后停止该host，allowed官方Git获取ref成功；错误猜测interface在core/src根路径404一次后按实际attachments目录取得；patch新增行前缀格式错误一次后修复。它们均不是Back解析失败，本代理完整parse、compile、应用API、项目helper、tests、formatter、Qt、Wine与tracked改动全部为0。

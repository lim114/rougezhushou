# 第90候选：可迁移的离线动画来源校核

状态：只读来源提案，尚无产品草稿或 tracked 改动。基准为实际提交 `1ce970fd30aa3b42d8ef787cde02513f05682b66`。

存在可复查性维护缺口。第87节公开归档的生成器读取固定 `/workspace/.continuation/p2-gummy-back-parser-source087`，还读取归档内并不存在的 `baseline/rouge/data/original-animation-references.json`。原第48节源完整性测试读取有意未迁移的 timing-048 cache。归档内 `root_current_source087.py` 校验的是第86节注册表及当时源码字节，后续正常添加测试登记后不能作为长期来源入口。这些历史工具应保持原样，不能修改历史证据使其看起来可重放。

此外，两个第87节 manifest 已列明的公开原件仍仅在工作树：`source-packet087/official-reader/official-source/spine-ts/build/spine-core.js`（299442B，SHA256 `f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1`）及 `spine-core.d.ts`（41999B，SHA256 `7bd72659db0bf1b58abede695ebc1ca3c163cb2beed72384c141616582817c10`）。实际 Git 对象查询均返回128，`git check-ignore -v` 均指向根 `.gitignore:5:build/`；二者现存字节仍匹配原 source manifest。初次冻结因此停止，未把工作树存在升级为已提交。建议精确 force-add 这两个已封来源原件，保留旧 manifest/hash/许可证；不要扩大 `.gitignore` 例外，也不要下载或生成替代物。

真实历史基线并未丢失：committed `source-packet087/history/original-animation-references.json.gz` 解压为1283952B/SHA256 `28d9be1dd6fe6f91dc5773b1c685ea78fb0bb403d25c4f26d933adcfcbad3f9e`，正是原 generation receipt 记录的923条数据。它是已有公开历史证据，不能称重建的 fixture。当前928条数据为1291928B/SHA256 `390deaa49bb353cface07b555c65a970b15a7ff1b58002008664e7872793ef53`。

建议的最小实现是独立 stdlib 只读维护 CLI，例如 `scripts/verify_original_animation_provenance.py`。默认根路径由脚本位置推导；允许 `--repository-root`、`--references` 和 `--evidence-dir` 显式覆盖，以便迁移后的 checkout 与临时验证目录使用。stdout 只返回 JSON 校核回执，成功退出0；缺失/损坏/范围不符退出1并给确定的简短 JSON 原因，不能把缺失资料计为成功或自动下载。CLI 不 import `rouge`、Qt、任何 Spine runtime，不读取当前个人设置，不修改输入，不运行旧生成器，不写产品数据。此入口属于维护工具，不进入产品流程或报告。

校核范围严格限定第87节古米 Back 的公开来源链与已提交的数据加法：

1. 核对 source manifest 的固定 SHA（`db2679793321d9d4a0f817757c53d93f88a16c4d4261f65f54223f69fb8b5265`）和 v1 结构。读取路径只取安全的相对 `archive_path`，历史 `source_path` 仅作标签。仅需要6个叶子：Back extraction、parse operation、真实 Back skeleton、真实历史 JSON.gz、固定官方 reader 的 js 与 d.ts。核对每项字节数/SHA；对 skeleton 另验 Git blob SHA1 `473df5c69d7e3552f6937f749bd42dd9e974ca01`。不用重新校核整个301/102清单，输出明确 verified-leaf 数量及名称。
2. 校核已封 extraction 的 SHA `2b3785b65d526bf74329f249b90bf2034c02eb79708e25ec12bdebe73709dd77`、固定 resource commit/URL/hash/bytes、官方 commit `8b4844bd4b193ba9e54487ed397a777993cbad56` 与 bundle hash。operation 仅证明已有读源记录：其 rendering、atlas/texture、game clock、EOF 的 false 边界必须保留，不能把校核回执写成新的 readSkeletonData 验证。
3. 按现有 builder 的30Hz表示归一化政策，逐项重新推导5条 Back JSON 记录。保留原 float 秒数、raw_frames、strict ceil、epsilon `1e-5`、representation normalized ceil、保守 OnAttack/reasons/preview 等全部字段。不得从头造新的读取器或游戏帧率规则。Attack 与 Skill 两个记录满足元资料筛选，但 Skill 的名称无技能编号，必须仍不匹配现有 `^Skill_?(\d+)(?:_|$)` 规则；不能变成 S1/S2 动作。所有 runtime_binding_verified 与 source_additions.runtime_binding_inferred 为严格 bool False。
4. 对照当前数据与 source_additions 的5个 id、来源链和 metadata；统计928/162/766/64/0。剔除确切新增项、恢复旧 counts/missing_sources 后，以既有 CRLF serializer 得到完整原923数据，要求与真实历史 gzip 解压字节精确相同。这个 inverse 是 JSON 校核，不是再跑923个计算矩阵。任何未来合法数据增量若超出此固定范围，应明确报告不在本校核版本范围内，而不是自动视为损坏或擅自补新来源。

建议6项有意义的维护回归（只用 committed 公开输入的临时复制；不运行 app API）：

1. 完整必要文件迁移至含空格的临时 checkout，从无关 cwd 调 CLI，默认脚本根与显式路径入口均可校核；输入hash前后相同，没有依赖旧绝对路径或 cache。
2. 单独改动真实 skeleton/官方 bundle/d.ts 的一个字节，分别明确来源hash错误；不进行解析或下载，保存独立错误路径。
3. 单独损坏或替换已封 extraction 的事件秒数/动画名，明确 extraction hash/来源链错误，不能从生产记录反推补造 source。
4. 改动生产 Back 的 duration/event normalized frame/preview、删掉一个真实动画或增加并不存在的 Die，明确派生记录/count校核失败；不能靠仅比较整文件hash掩盖缺少语义校核。
5. 将 runtime binding false 改成 true，或将泛称 Skill 改成带编号动作，明确边界/来源不一致；保持 metadata eligible 与实际技能选择规则的区别。
6. 分别缺失任一必需公开叶子、损坏manifest、改动旧Front/其它旧记录，分别明确缺失/manifest/inverse错误；缺失时不跳过、不重建历史 cache、不输出成功。

可登记一项 stdlib-only unittest 模块到精选入口；必要的 README 命令说明只讲使用与校核范围。原生产数值、动画选择、Qt 行为、未知友方时钟及个人状态无需改变。验收需实际 root fresh CLI/新回归与常规精选，节末全量依 root 统一调度，不由此来源审查运行。

来源审查本身读取301/102 manifest 的 metadata，只逐hash核对6个必要叶子。21个来源文件外置冻结，其中19个为实际 Git 字节，2个严格标记未提交工作树公开原件。没有新解析、下载、API、project helper、formatter、test、Qt、Wine 或产品草稿。初次冻结失败与可选错误路径发现保留在 diagnostics。渲染、纹理几何、EOF、真实客户端技能/普攻/皮肤绑定、旧解析器身份与故障根因继续未知。

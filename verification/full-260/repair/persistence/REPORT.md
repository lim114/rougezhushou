# 245 Wine 路径与 CJK 维护候选（已封存）

生产文件、原 Wine10 环境及 verification/full-245 历史回执未由本代理修改。此候选是260后维护，不增加功能节数。真实 Windows 尚不可用；Wine 兼容验收与 Native Windows 验收明确分开。

## 已证明的两个路径问题

1. 245 原3个 symlink 失败发生在产品调用之前。Wine10.0完整原件 kernelbase/file.c:980–986 中 CreateSymbolicLinkW 为 stub，直接 return TRUE；本次 ctypes 与 pathlib 实跑同样“成功但不创建”。完整探针为 wine-api-probe.json。
2. 公开 Linux 宿主 dangling link 对 Wine10 的 read/lstat/readlink/父目录枚举同时不可见。原 RunState/AccountCache 会当成缺失并 replace，真实覆盖该链接。reproduce_public_host_check.py 由宿主创建自己的公开 work 夹具、实际运行 Windows Python、再由宿主独立比对；host-independent-verification.json 证明原两类覆盖与候选两类保留。未读取、替换任何私人档案。

## 窄产品修复

首次加载缺失的记录，完整 .tmp 内容写完后用同目录 os.link 发布，原子拒绝已存在目录项；成功后删除 .tmp，后续已加载文件仍沿用原 replace。并发普通文件、Linux host dangling link 和 Wine11 NT dangling link 均不能被首存覆盖。不支持硬链接的文件系统报告保存失败、保留原件，不回退覆盖。

显式开始新局只对已判不可读的普通文件/符号链接先归档：同父目录、唯一 preserved-UUID 名、Windows不替换rename/Linux renameat2(RENAME_NOREPLACE)。保留相对 link text、解析目录与目标字节。目录/特殊条目不会被归档搬移。归档后原名首次保存继续 no-clobber，归档碰撞、后置并发新文件、归档/首存失败均保留证据且锁存失败。此前已失败 session 不因开始新局重试磁盘。

归档与首存是两次操作，不声称整个 reset 原子。若归档后中断，重新打开缺失原路径会发现该路径 retained originals，禁止自动保存并提示再次显式开始新局；不自动恢复/选择某个历史档案。成功新局 notice 显示归档名。

这同时避免 Wine11.19 的 ordinary .tmp → 已存在 NT reparse basename? replace 问题。完整同版原件链：kernelbase/file.c:2679 打开源 FILE_OPEN_REPARSE_POINT；ntdll/unix/file.c:3652 解析末段 reparse 物理槽；server/fd.c:2775 对源 reparse 向空归档目标保留 ?、2860 同 inode rename。原件完整文件及 SHA256 在 source/source-11.19-manifest.json。未采纳、编译任何 Wine C 修改；runtime-source-review 为封存的未运行备选。

## 正式验收

- candidate-linux-final.json/log：76 tests，0 failure/error/skip，进程 exit0。
- candidate-wine11-final-clean.json/log：同76 tests，0 failure/error/skip，进程 exit0。含原3例与14新增行为方法；损坏目录拒绝在现有失败归档方法内另作断言。
- 原始 CJK OCR 例，Linux、原Wine10、候选Wine11.19各1 PASS，0 skip，exit0；原语义断言未改。font/ 记录真实 NotoSansCJK-Regular.ttc SHA256 b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a 与真实 Qt Noto Sans CJK SC family。现有 Wine wrapper 已正确配置此字体；Linux全量需给 ROUGE_TEST_CJK_FONT。
- git apply --check product-candidate.patch 已通过。candidate-manifest.json 记录4个目标、原件及候选哈希。

早期 Wine11 的成功用例之后 exit1 是候选 launcher 漏配真实 Xvfb 的 PATH，strace证明确切是 Xvfb 子进程127及cleanup覆盖返回值。已补 /workspace/.compat/wine/usr/bin；exit-zero-complete-path.log、launcher-integration.log 与最终正式回执均 exit0。bootstrap 中缺32bit syswow64/rundll32 警告不能作为当前 exit1 原因。64bit Python/Qt 已验收；32bit应用及真实Windows未验收。

## 交接与迁移

1. Root 完成260后审核并应用 product-candidate.patch（4目标；不复制整个 work）。tests/test_persistence_initial_install.py 为新14个方法；另外两个旧模块保持原断言。
2. 可复用且已chmod可执行 launcher 绝对路径：/workspace/rougezhushou/work/wine-persistence-audit/runtime11/run-python11-devel.sh。此 launcher 使用隔离 prefix-devel 与独立 runtime-devel.lock，保留原 /workspace/.compat Wine10。
3. 使用 ROUGE_WINE_PYTHON_LAUNCHER 指向该脚本，经现有 bash scripts/wine_python.sh 运行所需完整维护范围/旧窗口/当前 MainWindow；launcher-integration.log 已实测双层不同锁兼容、exit0。执行大回归前继续用该同一 Python及真实字体，不借另一平台回执。
4. runtime11/migration-manifest.json：WineHQ 签名APT来源、版本11.19~trixie-1、两包 SHA256/索引一致、native UCRT原始SDK SHA、原件链。以后迁至稳定 /workspace/.compat/wine11 需按此manifest独立解包/新prefix，先同版目标回归再切默认launcher；不混Wine10/11 server或NTDLL，不复制私人文件或旧账户状态。
5. prefix/、prefix-devel/、root/、root-devel/、包deb及二进制不进仓库。只归档产品patch、验证脚本/日志/JSON、源码证据与迁移说明。原245回执保留，并将修复后的完整维护验收作为新回执。

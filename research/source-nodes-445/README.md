# 第445节 + 藏品来源节点分组、图标与准确地图入口

基线91fd3ce5481bc149902dc40cd47d6a8e064b6f64。项目原片158秒的物品卡用图标区分取得节点。本节把原先同列的地图节点与其它来源分开：只有已核对的枚举/中文名对应才列入“对应地图节点”，林间代步、流窜的居民及仅有来源名称的记录保留在“其它取得来源”。不猜图标或地图位置，不删原来源、池、统计、条件或资料范围。

明确节点卡可点击或键盘直接打开助手地图并筛选对应类型；有同类记录时标在对应位置，未记录不补造。原查池、展开条件、独立地图按钮、清除筛选和刷新保持。来源失效拒绝旧身份跳转；打开地图关闭挡住它的物品目录。不操作游戏、不自动选路、不将来源当本局实际掉落。

地图与来源卡共用原图集裁切，缓存从每个地图实例移到共享图像入口，图集每进程解码一次，所有原节点图片逐像素保持；无新模型、图片、依赖或应用模块进入生产，不称全部提速或净减代码。最终70项不同相关检查通过，25项当前/18项旧436原生范围分别通过；当前两张及旧436图逐张查看。第一张地图附图在恢复临时状态后重新打开而为空，已改为状态恢复前捕获真实地图，原图与脚本保留。动态旧源码测试遗漏__file__的夹具失败保留，产品资格未放宽。

用户明确“优先复用外部成熟方案”，已写入AGENTS、项目要求与实现路线，原“内部整合首选”判断已修正。下面的外部试验与本节产品功能分开，不以内部组件复用冒充已采用他人方案。

## 外部成熟方案核查与实际试验

先克隆并读README/许可，再定向读源码。MaaFramework固定b176dd8883c19fa1a46e1aa3cb553b0808176347：[README](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/README.md)、[许可](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/LICENSE.md)、[识别协议](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/docs/en_us/3.1-PipelineProtocol.md)。实际读Python Tasker/Context/Resource/Controller、类型和协议；提供直接对已有图像识别的接口，适合进一步比较替换手写分流/定位流程。主分支源码与下述发布二进制独立固定，不假定同一次构建。

MaaFw5.14.3 Windows轮子及StrEnum0.4.15只解压到.cache隔离目录，未改项目虚拟环境或打包第三方库。首轮缺StrEnum，补齐后发现发布轮子没有MaaDbgControlUnit.dll；按其CustomController接口只提供静态公开图像，所有输入方法拒绝，实际识别跑通。自己两处启动脚本的复用目录和不存在帧名错误也分别保留，不能称外部库故障。没有绑定真实游戏或执行action/post_task。

默认SIFT按Horizontal选取位置，原图选中了错误候选；按官方协议改为Score排序及20匹配点候选参数后，原图、0.75倍缩放图、另一张无目标公开页面与空白四例符合预期。AKAZE缩放正例漏检，ORB两个正例漏检。该阈值使用过先前同图证据，不是独立训练/验收；两张公开视频和派生图不代表全面准确率。SIFT单次约278–510ms、AKAZE127–209ms、ORB22–69ms，只属此次CPU单模板调用，不与现有完整页面流程作等价速度比较。更快不等于适用，不直接替换生产。

PyQt-Fluent-Widgets固定6b9c646ce107660f66d20cec8af967c2c8d79764：[README](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/README.md)、[许可](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/LICENSE)、[布局实现](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/qfluentwidgets/components/layout/flow_layout.py)。实际读自适应布局示例与实现，README列PySide6包；本次源码默认分支为PyQt5。README采用GPLv3/商业授权安排，不能把可读源码当任意可复制；Fluent整套风格也不自动等于参考视频。未安装或复制到生产；保留后续明确许可与视频组件适配比较，不因内部已有控件就认定外部方案无价值。

下一步优先对MaaFramework的多页面、文字/数字、实际连续输入和资源/识别耗时进行与原流程等条件比较，再决定替换范围。当前仅试验，OCR未完成替换；729选择器登记保留前728次序，未跑全量，下次完整455。测试小窗更新，启动时可见响应并由Windows-mcp实际查看，启动六私人路径保持；随后绑定不活跃、工具条隐藏，符合既有跟随逻辑，不冒称收尾时仍可见，也不操作游戏强行还原。整批摘要另存，不回滚或上传私人内容。完整视频/程序、其余密度/滚动条外观及P3/P2/P1仍未完成。

[本节回执](../../verification/sections/445.json)。

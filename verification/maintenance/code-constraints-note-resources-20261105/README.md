# D32资源加载与笔记预览模块整改

已按用户确认范围开放本机及HTTP/HTTPS图片、HTML富文本、CSS。相对路径以笔记目录为准；编辑器、近期笔记、笔记目录和上级笔记四处都传入同一目录。HTML使用Qt富文本语义，网页链接仍交默认浏览器；音视频/字体/附件保持链接，不嵌入执行或安装。

删除NoExternalResources文档类及浏览器到该文档的重复转发，统一在NotePreview.loadResource核对类型和协议。复用Qt异步网络加载，file也经同一入口；同一URL在完成或进行中时复用，图片完成后重新排版当前正文并恢复阅读位置。临时失败提示放在悬停说明，不捕获内部异常、不自动重试。资源缓存随预览对象存在；同URL失败后本次对象不反复请求，重新创建预览才再次加载。没有磁盘缓存、系统证书修改或私人内容上传。

## 验证

Windows原生29项定向检查通过，另补1项设置目录后的真实页内链接点击通过。实际图片像素、本机和HTTP CSS文字颜色、中文HTML资源、四处目录绑定、HTTP重复请求、HTTPS真实TLS、慢请求下界面事件与切换后的正文/选择/滚动位置、404结束、脚本/媒体无自动执行、既有D33/D34均已核对。TLS夹具只在单次测试请求信任临时证书，不忽略证书错误。没有全量检查。

初轮6项中1项出错：测试在等待结束后才触发Qt懒加载，断言失败并留下尚未结束的文件读取；调整触发顺序后6通过。资源初轮7项中2失败：CSS测试缺少Qt接受的head/type声明，且等待早于绘制请求；修正后剩1个错误像素落点断言，改为全视口像素计数后通过。原日志保留.local/code-constraints-review-22/，未改写历史证据。

原项目测试窗口已更新、可见且响应；隔离笔记图片/样式实际窗口已查看。截图和原始日志只留本机。浏览器打开请求仍用替换调用验证，真实第三方网页加载不计通过。

## 三条逐函数审查

| 入口 | 本次结论 |
| --- | --- |
| NotebookHTML.task_list_item | Mistune回调，保留任务状态转换，不是单次包装 |
| NotePreview.__init__ | 初始化缓存、进行中请求与Qt管理器；真实笔记入口传入目录 |
| _anchor | D33授权的网页点击、本页锚点及非网页手动处理保持 |
| loadResource | D32范围只在入口核对一次；完成缓存和进行中请求分别处理 |
| _resource_finished | Qt完成信号处理；正常成功/失败收口并释放reply，不重试、不兜内部错误 |
| read_markdown | D34成功后更新缓存；未变正文只在入口跳过，资源到达时显式重绘 |

player_note_preview.py本模块三条审查完成；依赖框架和另外四个模块其余路径不扩大为完成。[当前进度](PROGRESS.md)。

## 复用与使用示例

使用现有PySide6 6.11.2，无新增库、未复制外部源码。官方依据：[QNetworkAccessManager异步接口](https://doc.qt.io/qt-6.11/qnetworkaccessmanager.html)、[QTextDocument资源与基础目录](https://doc.qt.io/qt-6.11/qtextdocument.html)、[Qt支持的HTML/CSS](https://doc.qt.io/qt-6.11/richtext-html-subset.html)。

图片可直接写 `![说明](图片.png)`。外链样式使用Qt支持的声明：

```html
<html><head><link rel="stylesheet" type="text/css" href="theme.css"></head>
<body><p>笔记正文</p><img src="图片.png"></body></html>
```

CSS限Qt富文本子集；网络图片打开时访问源站。功能编号保持472完成、473在制。

# Qt 文字布局适配

`rouge/enemy_overview.py` 中 `MechanismDelegate.sizeHint` 的逐行排版循环和文字边距规则，改编自 QtBase v6.11.2 的 `QCommonStylePrivate::viewItemTextLayout` 与 `viewItemDrawText`：

- 原始源码：https://github.com/qt/qtbase/blob/v6.11.2/src/widgets/styles/qcommonstyle.cpp
- Copyright (C) 2016 The Qt Company Ltd.
- 本适配选择原作者多重许可中的 **LGPL-3.0-only**；许可全文见 [Qt-LGPL-3.0-only.txt](Qt-LGPL-3.0-only.txt)，其引用的 GPLv3 全文见 [Qt-GPL-3.0-only.txt](Qt-GPL-3.0-only.txt)。

本机修改：C++ 改为 PySide6；保留 Qt 原生 `QTextLayout`、`QTextOption` 和样式边距；仅计算完整高度，去掉用于截断显示的 `maxHeight`、最后可见行和宽度统计分支；高度向上取整并加入实际样式空间。没有复制或编译整个 QtBase，没有修改或替换现有 PySide6/Qt 运行库。原项目条目、分类、头像、数值和准确引用继续由本项目提供。

适配代码随仓库以可修改 Python 源码分发；来源版本、原文件摘要及本机验证记录见 `research/enemy-table-reading-20261101/`。

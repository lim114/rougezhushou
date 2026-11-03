"""Full-height Qt v6.11.2 text layout; LGPL-3.0-only, see Qt notice in licenses/."""
from math import ceil
from PySide6.QtCore import QSize,QRect,QPointF
from PySide6.QtGui import QTextLayout,QTextOption
from PySide6.QtWidgets import QStyledItemDelegate,QStyleOptionViewItem,QStyle,QTreeView


class WrappedItemDelegate(QStyledItemDelegate):
    """Copyright (C) 2016 The Qt Company Ltd. LGPL-3.0-only.

    viewItemTextLayout port: full-height measurement omits early elision.
    """
    def __init__(self,parent,columns):
        super().__init__(parent);self.columns=columns

    def sizeHint(self,option,index):
        size=super().sizeHint(option,index)
        if index.column()not in self.columns:return size
        opt=QStyleOptionViewItem(option);self.initStyleOption(opt,index)
        tree=self.parent();width=tree.columnWidth(index.column())if isinstance(tree,QTreeView)else tree.viewport().width()
        opt.rect=QRect(0,0,width,size.height())
        rect=tree.style().subElementRect(QStyle.SubElement.SE_ItemViewItemText,opt,tree)
        margin=tree.style().pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin,None,tree)+1
        text_option=QTextOption();text_option.setWrapMode(QTextOption.WrapMode.WordWrap);text_option.setTextDirection(opt.direction);text_option.setAlignment(QStyle.visualAlignment(opt.direction,opt.displayAlignment))
        layout=QTextLayout(opt.text,opt.font);layout.setTextOption(text_option);height=0;layout.beginLayout()
        while True:
            line=layout.createLine()
            if not line.isValid():break
            line.setLineWidth(rect.width()-2*margin);line.setPosition(QPointF(0,height));height+=line.height()
        layout.endLayout()
        return QSize(size.width(),max(size.height(),ceil(height)+opt.rect.height()-rect.height()))

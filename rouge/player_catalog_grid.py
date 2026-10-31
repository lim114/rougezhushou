"""Qt-native adaptive icon catalogue; source identity stays on the list item."""
from PySide6.QtCore import Qt,QSize,QRect,QPointF
from PySide6.QtGui import QColor,QPen,QIcon,QTextLayout,QTextOption
from PySide6.QtWidgets import QListWidget,QListView,QStyledItemDelegate

INVENTORY_STYLE='''
#inventoryWindow{background:#101214;border:1px solid #3b4245;border-radius:14px;}
#inventoryWindow QWidget{background:transparent;}
#inventoryWindow QLabel{color:#d7dcdb;background:transparent;}
#inventoryWindow QTabWidget::pane{background:#101214;border:0;}
#inventoryWindow QTabBar::tab{background:#282d30;color:#d6dcda;border:0;border-radius:14px;padding:7px 16px;margin:3px;}
#inventoryWindow QTabBar::tab:selected{background:#e7ecea;color:#1d2926;}
#inventoryWindow QLineEdit,#inventoryWindow QComboBox{background:#23292b;color:#e3e9e6;border:1px solid #3d4648;border-radius:12px;padding:6px;}
#inventoryWindow QComboBox QAbstractItemView{background:#23292b;color:#e3e9e6;selection-background-color:#3d5e55;}
#inventoryWindow QPushButton{background:#292f31;color:#d6dfdc;border:0;border-radius:13px;padding:6px 12px;}
#inventoryWindow QPushButton:checked{background:#e6ece9;color:#17241e;}
#inventoryWindow QPushButton:hover{background:#3d5e55;color:white;}
#inventoryWindow QCheckBox{color:#b6c2bc;}
#inventoryWindow QPlainTextEdit{background:#1b2322;color:#d9e6de;border:1px solid #43514b;border-radius:12px;padding:10px;}
#inventoryWindow QListWidget{background:#101214;color:#8bd3b9;border:0;outline:none;}
'''

class IconTile(QStyledItemDelegate):
    def sizeHint(self,option,index):
        if self.parent().descriptions and self.parent().tile_icon<=56:
            width=self.parent().viewport().width();return QSize(max(180,width//max(1,width//320)-6),108)
        return self.parent().gridSize()

    def paint(self,painter,option,index):
        painter.save();rect=option.rect.adjusted(3,3,-3,-3)
        selected=index.data(Qt.ItemDataRole.UserRole)==getattr(self.parent(),'selected_identity',None)
        if selected:
            painter.setPen(QPen(QColor('#81cdb6'),1));painter.setBrush(QColor('#23322e'));painter.drawRoundedRect(rect,10,10)
        icon=index.data(Qt.ItemDataRole.DecorationRole);size=self.parent().tile_icon
        if self.parent().descriptions and size<=56:
            picture=QRect(rect.left()+7,rect.top()+14,size,size)
            if isinstance(icon,QIcon)and not icon.isNull():icon.paint(painter,picture)
            else:painter.setPen(QColor('#a4b1ac'));painter.drawText(picture,Qt.AlignmentFlag.AlignCenter,'暂无图片')
            x=picture.right()+12;width=rect.right()-x-8;painter.setFont(option.font);metrics=painter.fontMetrics()
            title=index.data(Qt.ItemDataRole.DisplayRole)or'';title_height=metrics.lineSpacing()*(2 if '\n'in title else 1)
            painter.setPen(QColor('#8bd3b9'))
            for number,line_text in enumerate(title.split('\n')):painter.drawText(QRect(x,rect.top()+8+number*metrics.lineSpacing(),width,metrics.lineSpacing()),Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,metrics.elidedText(line_text,Qt.TextElideMode.ElideRight,width))
            description=index.data(Qt.ItemDataRole.UserRole+2)or'暂无效果说明'
            layout=QTextLayout(description,option.font);text_option=QTextOption();text_option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere);layout.setTextOption(text_option)
            y=rect.top()+title_height+14;bottom=rect.bottom()-7;painter.setPen(QColor('#d7e2dd'));layout.beginLayout()
            while True:
                line=layout.createLine()
                if not line.isValid():break
                line.setLineWidth(width)
                if y+2*metrics.lineSpacing()>bottom:
                    text=description[line.textStart():].replace('\n',' ');painter.drawText(QRect(x,y,width,metrics.lineSpacing()),Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,metrics.elidedText(text,Qt.TextElideMode.ElideRight,width));break
                line.draw(painter,QPointF(x,y));y+=metrics.lineSpacing()
            layout.endLayout();painter.restore();return
        picture=QRect(rect.center().x()-size//2,rect.top()+6,size,size)
        if isinstance(icon,QIcon)and not icon.isNull():icon.paint(painter,picture)
        else:
            painter.setPen(QColor('#a4b1ac')if selected else option.palette.text().color());painter.drawText(picture,Qt.AlignmentFlag.AlignCenter,'暂无图片')
        painter.setPen(QColor('#8bd3b9')if selected else option.palette.text().color())
        text_rect=QRect(rect.left()+4,picture.bottom()+6,rect.width()-8,42)
        painter.drawText(text_rect,Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop|Qt.TextFlag.TextWordWrap,index.data(Qt.ItemDataRole.DisplayRole)or'')
        painter.restore()

class CatalogGrid(QListWidget):
    def __init__(self,parent=None,*,descriptions=False):
        super().__init__(parent);self.tile_icon=72;self.selected_identity=None;self.descriptions=descriptions
        self.setViewMode(QListView.ViewMode.IconMode);self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static);self.setWrapping(True);self.setWordWrap(True)
        self.setSpacing(3);self.setDragEnabled(False);self.setUniformItemSizes(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setItemDelegate(IconTile(self));self.set_tile_size(72)
        self.currentItemChanged.connect(self._selected)
    def _selected(self,item,*_):
        self.selected_identity=item.data(Qt.ItemDataRole.UserRole)if item else None;self.viewport().update()
    def set_tile_size(self,size):
        size=max(48,min(104,int(size)));self.tile_icon=size
        self.setIconSize(QSize(size,size));self.setGridSize(QSize()if self.descriptions and size<=56 else QSize(max(92,size+28),size+60));self.doItemsLayout();self.viewport().update()
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.descriptions and self.tile_icon<=56:self.doItemsLayout()

def add_catalog_controls(body,grid,detail,*,notice,actions=()):
    from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QWidget,QSplitter,QLabel,QSlider,QPushButton
    position=body.indexOf(grid);body.removeWidget(grid);body.removeWidget(detail)
    reader=QWidget();reading=QVBoxLayout(reader);reading.setContentsMargins(8,0,0,0);reading.addWidget(detail,1)
    for action in actions:reading.addWidget(action)
    split=QSplitter(Qt.Orientation.Horizontal);split.addWidget(grid);split.addWidget(reader);split.setSizes([700,320]);body.insertWidget(position,split,1)
    body.setContentsMargins(8,4,8,4);body.setSpacing(5)
    bar=QHBoxLayout();button=QPushButton('效果说明');button.setCheckable(True);button.toggled.connect(reader.setVisible);bar.addWidget(button)
    scope=QPushButton('资料说明');scope.setCheckable(True);scope.toggled.connect(notice.setVisible);bar.addWidget(scope);notice.hide();bar.addStretch();bar.addWidget(QLabel('显示大小'))
    scale=QSlider(Qt.Orientation.Horizontal);scale.setRange(48,104);scale.setValue(60);grid.set_tile_size(60);scale.setMaximumWidth(180);scale.valueChanged.connect(grid.set_tile_size);bar.addWidget(scale);body.addLayout(bar);reader.hide()
    scale.setToolTip('缩到左侧显示图文效果卡片，向右显示图标网格；选择条目可读完整说明。')
    grid.currentItemChanged.connect(lambda item:button.setChecked(item is not None))
    return button,scale,scope

"""Qt-native adaptive icon catalogue; source identity stays on the list item."""
from PySide6.QtCore import Qt,QSize,QRect
from PySide6.QtGui import QColor,QPen,QIcon
from PySide6.QtWidgets import QListWidget,QListView,QStyledItemDelegate

INVENTORY_STYLE='''
#inventoryWindow{background:#101214;border:1px solid #3b4245;border-radius:14px;}
#inventoryWindow QLabel{color:#d7dcdb;background:transparent;}
#inventoryWindow QTabWidget::pane{border:0;}
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
        return self.parent().gridSize()

    def paint(self,painter,option,index):
        painter.save();rect=option.rect.adjusted(3,3,-3,-3)
        selected=index.data(Qt.ItemDataRole.UserRole)==getattr(self.parent(),'selected_identity',None)
        if selected:
            painter.setPen(QPen(QColor('#81cdb6'),1));painter.setBrush(QColor('#23322e'));painter.drawRoundedRect(rect,10,10)
        icon=index.data(Qt.ItemDataRole.DecorationRole);size=self.parent().tile_icon
        picture=QRect(rect.center().x()-size//2,rect.top()+6,size,size)
        if isinstance(icon,QIcon)and not icon.isNull():icon.paint(painter,picture)
        else:
            painter.setPen(QColor('#a4b1ac')if selected else option.palette.text().color());painter.drawText(picture,Qt.AlignmentFlag.AlignCenter,'暂无图片')
        painter.setPen(QColor('#8bd3b9')if selected else option.palette.text().color())
        text_rect=QRect(rect.left()+4,picture.bottom()+6,rect.width()-8,42)
        painter.drawText(text_rect,Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop|Qt.TextFlag.TextWordWrap,index.data(Qt.ItemDataRole.DisplayRole)or'')
        painter.restore()

class CatalogGrid(QListWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.tile_icon=72;self.selected_identity=None
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
        self.setIconSize(QSize(size,size));self.setGridSize(QSize(max(104,size+46),size+66));self.doItemsLayout();self.viewport().update()

def add_catalog_controls(body,grid,detail):
    from PySide6.QtWidgets import QHBoxLayout,QLabel,QSlider,QPushButton
    bar=QHBoxLayout();button=QPushButton('效果说明');button.setCheckable(True);button.toggled.connect(detail.setVisible);bar.addWidget(button);bar.addStretch();bar.addWidget(QLabel('图标大小'))
    scale=QSlider(Qt.Orientation.Horizontal);scale.setRange(48,104);scale.setValue(72);scale.setMaximumWidth(180);scale.valueChanged.connect(grid.set_tile_size);bar.addWidget(scale);body.addLayout(bar);detail.hide()
    grid.currentItemChanged.connect(lambda item:button.setChecked(item is not None))
    return button,scale

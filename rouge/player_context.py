"""Recent confirmed content stays a reading shortcut, never a current-position claim."""
from PySide6.QtWidgets import QToolBar,QLabel,QPushButton,QWidget,QVBoxLayout,QToolButton
from PySide6.QtCore import Qt

def recent_content(state):
    row=state.get('last_node_content')or{}
    return row.get('title')if isinstance(row.get('title'),str)else''

class ContextBar(QToolBar):
    def __init__(self,run,open_content,parent=None):
        super().__init__('本局快捷查询',parent);self.run=run;self.setMovable(False)
        self.label=QLabel();self.label.setWordWrap(True);self.addWidget(self.label)
        self.open_button=QPushButton('查看相关内容');self.open_button.clicked.connect(open_content);self.addWidget(self.open_button)
        self.refresh()
    def refresh(self):
        title=recent_content(self.run.state)
        self.label.setText('最近读取：'+title if title else'尚未读取节点详情；可先从地图或资料查询查看。')
        self.open_button.setEnabled(bool(title))
        self.label.setToolTip('本局最近读取的内容，可能来自已走过的节点；不表示当前位置或本次一定出现。')

class Fold(QWidget):
    def __init__(self,title,content,parent=None):
        super().__init__(parent);body=QVBoxLayout(self);body.setContentsMargins(0,0,0,0)
        self.toggle=QToolButton();self.toggle.setText(title);self.toggle.setCheckable(True)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon);body.addWidget(self.toggle)
        self.content=content;body.addWidget(content);content.hide()
        self.toggle.toggled.connect(self._toggle);self._toggle(False)
    def _toggle(self,value):
        self.content.setVisible(value);self.toggle.setArrowType(Qt.ArrowType.DownArrow if value else Qt.ArrowType.RightArrow)

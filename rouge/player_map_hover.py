"""A hoverable, pinnable map card using local references, never a game overlay hook."""
from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtWidgets import (QDialog,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QPushButton,QToolButton,QScrollArea,QSizePolicy)
from . import player_map_reference as model

class NodeHoverCard(QDialog):
    entryRequested=Signal(str,str,str)
    entered=Signal()
    left=Signal()
    def __init__(self,parent):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.setWindowTitle('节点速览');self.resize(380,490)
        self.binding=None;self.content_key=None;self.pinned=False
        self.setObjectName('nodeHoverCard');self.setStyleSheet('#nodeHoverCard{background:#203334;border:1px solid #769490;border-radius:12px;} #nodeHoverCard QLabel{color:#e7f5f0;} QToolButton{background:#293f3f;color:#eef8f5;border:1px solid #486261;border-radius:7px;padding:4px;} QToolButton:hover{background:#3c5a58;} QPushButton{color:#e7f5f0;background:#304746;border:1px solid #617b77;border-radius:7px;padding:4px;}')
        body=QVBoxLayout(self);head=QHBoxLayout();self.title=QLabel();head.addWidget(self.title,1)
        self.pin=QPushButton('固定');self.pin.setCheckable(True);self.pin.toggled.connect(self.set_pinned);head.addWidget(self.pin)
        close=QPushButton('×');close.setFixedWidth(27);close.clicked.connect(self.dismiss);head.addWidget(close);body.addLayout(head)
        self.notice=QLabel('');self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);body.addWidget(self.scroll,1)
    def set_pinned(self,value):self.pinned=value;self.pin.setText('取消固定'if value else'固定')
    def enterEvent(self,event):self.entered.emit();super().enterEvent(event)
    def leaveEvent(self,event):self.left.emit();super().leaveEvent(event)
    def dismiss(self):self.pin.setChecked(False);self.hide()
    def install(self,binding,graph,node_id,config,view,*,force=False):
        if self.pinned and self.binding!=binding and not force:return False
        node=next((n for n in graph['nodes']if n['id']==node_id),None)
        if node is None:self.dismiss();return False
        key=(binding,repr(node),repr(config),view.historical)
        if key==self.content_key:return True
        offset=self.scroll.verticalScrollBar().value()if self.binding==binding else 0;self.binding=binding;self.content_key=key
        from .map_reporting import location
        self.title.setText(location(node,graph['grid']['rows'])+' · 节点速览')
        self.notice.setText(('历史地图记录；'if view.historical else'最近确认地图；')+'历史节点比例供参考，不是本局概率；未核验当前DLC与本图条件。事件仍需满足前置。')
        content=QWidget();body=QVBoxLayout(content);types=model.candidate_types(node)
        body.addWidget(QLabel('已读类型'if node.get('observed_type')in types else'模板固定类型'if node.get('template_type')else'可能的节点类型'))
        grid=QGridLayout();body.addLayout(grid);self.type_values={}
        for i,kind in enumerate(types):
            cell=QWidget();layout=QVBoxLayout(cell);layout.setContentsMargins(3,3,3,3);picture=QLabel();image=view.sprite_for(kind)
            if not image.isNull():picture.setPixmap(QPixmap.fromImage(image).scaled(40,40,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            picture.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(picture);label=QLabel(kind);label.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(label)
            row=model.historical_frequency(graph,node,kind);known=model.type_match(node,kind)
            value='已读'if known=='observed'else'模板固定'if known=='template'else f"历史 {row['frequency']:.2%}"if row else'无对应样本'
            self.type_values[kind]=value;rate=QLabel(value);rate.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(rate)
            if row:cell.setToolTip(f"同层、距入口相同步数：{row['count']} / {row['total']}个节点记录。分母未按本图候选重新归一化。")
            grid.addWidget(cell,i//3,i%3)
        if not types:body.addWidget(QLabel('类型尚未确认；不把全目录当作此处候选。'))
        try:dossier=model.node_dossier(graph,node_id,config)
        except(ValueError,TypeError,KeyError):dossier=None
        self.entry_buttons=[]
        for label,kind,rows in [('事件候选','event',(dossier or{}).get('rows',[])),('作战候选','battle',(dossier or{}).get('battle_rows',[]))]:
            if not rows:continue
            heading=QLabel(label+f' · {len(rows)}项');body.addWidget(heading);cards=QGridLayout();body.addLayout(cards)
            for i,row in enumerate(rows):
                button=QToolButton();button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon);button.setText(row.get('title')or'名称未确认');button.setMinimumHeight(114);button.setIconSize(QSize(145,75));button.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
                path=model.event_picture(row['id'])if kind=='event'else None
                if path:button.setIcon(QIcon(str(path)))
                else:
                    button.setIcon(QIcon(QPixmap.fromImage(view.sprite_for('作战'if kind=='battle'else'不期而遇'))))
                    if kind=='event':button.setText(button.text()+'\n暂无对应插图');button.setMinimumHeight(135)
                button.setToolTip('点击在地图侧栏阅读。资料候选不等于本局实际出现；发生概率未核验。')
                button.clicked.connect(lambda checked=False,k=kind,identity=row['id']:self.entryRequested.emit(node_id,k,identity));cards.addWidget(button,i//2,i%2);self.entry_buttons.append((kind,row['id'],button))
        body.addStretch();old=self.scroll.takeWidget();self.scroll.setWidget(content)
        if old:old.deleteLater()
        self.scroll.verticalScrollBar().setValue(offset);return True

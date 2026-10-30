"""A hoverable, pinnable map card using local references, never a game overlay hook."""
from PySide6.QtCore import Qt,Signal,QSize,QRectF
from datetime import datetime
from PySide6.QtGui import QIcon,QPixmap,QPainter,QPainterPath,QColor,QLinearGradient,QPen
from PySide6.QtWidgets import (QDialog,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QPushButton,QToolButton,QScrollArea,QSizePolicy)
from . import player_map_reference as model

class NodeEntryButton(QToolButton):
    """Keep Qt button input/accessibility; draw the reference image with its caption."""
    def __init__(self,title,artwork,icon,parent=None):
        super().__init__(parent);self.artwork=QPixmap(str(artwork))if artwork else QPixmap()
        self.setText(title);self.setAccessibleName(title);self.setIcon(icon);self.setIconSize(QSize(40,40))
        self.setMinimumHeight(96);self.setMinimumWidth(0);self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    def sizeHint(self):return QSize(166,96)
    def caption_rect(self):return self.rect().adjusted(7,self.height()-30,-7,-5)
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect=QRectF(self.rect()).adjusted(.5,.5,-.5,-.5);clip=QPainterPath();clip.addRoundedRect(rect,7,7);p.setClipPath(clip)
        p.fillRect(rect,QColor('#30413f'))
        if not self.artwork.isNull():
            scale=max(rect.width()/self.artwork.width(),rect.height()/self.artwork.height())
            w,h=rect.width()/scale,rect.height()/scale
            source=QRectF((self.artwork.width()-w)/2,(self.artwork.height()-h)/2,w,h)
            p.drawPixmap(rect,self.artwork,source)
        else:
            self.icon().paint(p,self.rect().adjusted(0,8,0,-33),Qt.AlignmentFlag.AlignCenter)
        shade=QLinearGradient(0,self.height()*.5,0,self.height());shade.setColorAt(0,QColor(6,16,15,0));shade.setColorAt(1,QColor(6,16,15,240));p.fillRect(rect,shade)
        if self.underMouse()or self.isDown():p.fillRect(rect,QColor(163,217,202,30))
        if self.artwork.isNull():
            p.setPen(QColor('#d4e3de'));p.drawText(self.rect().adjusted(6,0,-6,-29),Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignBottom,'暂无对应插图')
        p.setPen(QColor('#f1f7f5'));font=self.font();font.setBold(True);p.setFont(font)
        text=p.fontMetrics().elidedText(self.text(),Qt.TextElideMode.ElideRight,self.caption_rect().width())
        p.drawText(self.caption_rect(),Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,text)
        p.setClipping(False);p.setBrush(Qt.BrushStyle.NoBrush);p.setPen(QPen(QColor('#b4e5d6'if self.hasFocus()else'#49625c'),2 if self.hasFocus()else 1));p.drawRoundedRect(rect,7,7)

class NodeHoverCard(QDialog):
    entryRequested=Signal(str,str,str)
    entered=Signal()
    left=Signal()
    def __init__(self,parent):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.setWindowTitle('节点速览');self.resize(self.sizeHint())
        self.binding=None;self.content_key=None;self.pinned=False
        self.setObjectName('nodeHoverCard');self.setStyleSheet('#nodeHoverCard{background:#263535;border:1px solid #769490;border-radius:12px;} #nodeHoverCard QLabel{color:#e7f5f0;background:transparent;} #nodeHoverCard QScrollArea,#nodeHoverBody{background:#263535;border:0;} #nodeHoverCard QScrollBar:vertical{background:#263535;width:7px;margin:0;} #nodeHoverCard QScrollBar::handle:vertical{background:#81918d;border-radius:3px;min-height:25px;} #nodeHoverCard QScrollBar::add-line:vertical,#nodeHoverCard QScrollBar::sub-line:vertical{height:0;} #nodeHoverCard QScrollBar::add-page:vertical,#nodeHoverCard QScrollBar::sub-page:vertical{background:transparent;} QPushButton{color:#e7f5f0;background:#304746;border:1px solid #617b77;border-radius:7px;padding:4px;}')
        body=QVBoxLayout(self);head=QHBoxLayout();self.title=QLabel();head.addWidget(self.title,1)
        self.pin=QPushButton('固定');self.pin.setCheckable(True);self.pin.toggled.connect(self.set_pinned);head.addWidget(self.pin)
        close=QPushButton('×');close.setFixedWidth(27);close.clicked.connect(self.dismiss);head.addWidget(close);body.addLayout(head)
        info=QHBoxLayout();self.summary=QLabel('历史比例不是本局概率；当前版本适用性待核验。');self.summary.setWordWrap(True);info.addWidget(self.summary,1)
        self.source_toggle=QPushButton('说明');self.source_toggle.setCheckable(True);self.source_toggle.setAccessibleName('展开统计来源与适用范围');info.addWidget(self.source_toggle);body.addLayout(info)
        self.notice=QLabel('');self.notice.setWordWrap(True);body.addWidget(self.notice);self.notice.hide();self.source_toggle.toggled.connect(self.notice.setVisible)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setFrameShape(QScrollArea.Shape.NoFrame);self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);body.addWidget(self.scroll,1)
    def sizeHint(self):return QSize(380,600)
    def set_pinned(self,value):self.pinned=value;self.pin.setText('取消固定'if value else'固定')
    def enterEvent(self,event):self.entered.emit();super().enterEvent(event)
    def leaveEvent(self,event):self.left.emit();super().leaveEvent(event)
    def dismiss(self):self.pin.setChecked(False);self.hide()
    def install(self,binding,graph,node_id,config,view,*,force=False):
        if self.pinned and self.binding!=binding and not force:return False
        node=next((n for n in graph['nodes']if n['id']==node_id),None)
        if node is None:self.dismiss();return False
        frequencies=model.default_frequencies()if view.frequencies is None else view.frequencies
        key=(binding,repr(node),repr(config),view.historical,graph['grid']['rows'],frequencies.identity)
        if key==self.content_key:return True
        offset=self.scroll.verticalScrollBar().value()if self.binding==binding else 0;self.binding=binding;self.content_key=key
        from .map_reporting import location
        self.title.setText(location(node,graph['grid']['rows'])+' · 节点速览')
        stamp=(frequencies.metadata or{}).get('updatedAt')
        date=datetime.fromisoformat(stamp.replace('Z','+00:00')).astimezone().strftime('%Y-%m-%d')if stamp else''
        source='路标统计更新 '+date+'。'if date else'暂无可核对统计。'
        self.summary.setText(('历史地图 · 'if view.historical else'')+'历史比例不是本局概率；当前版本适用性待核验。')
        self.notice.setText(('历史地图记录；'if view.historical else'最近确认地图；')+'历史比例不是本局概率；未核验当前DLC与本图条件。'+source)
        content=QWidget();content.setObjectName('nodeHoverBody');body=QVBoxLayout(content);body.setContentsMargins(0,3,8,6);body.setSpacing(7);types=model.candidate_types(node)
        body.addWidget(QLabel('已读类型'if node.get('observed_type')in types else'模板固定类型'if node.get('template_type')else'可能的节点类型'))
        previous=node.get('remembered_type')
        if previous and previous!=node.get('observed_type'):body.addWidget(QLabel('原为'+previous+' · 本局已保存记录，不是当前候选。'))
        grid=QGridLayout();grid.setSpacing(5)
        for col in range(3):grid.setColumnStretch(col,1)
        body.addLayout(grid);self.type_values={}
        for i,kind in enumerate(types):
            cell=QWidget();layout=QVBoxLayout(cell);layout.setContentsMargins(3,3,3,3);picture=QLabel();image=view.sprite_for(kind)
            if not image.isNull():picture.setPixmap(QPixmap.fromImage(image).scaled(40,40,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:picture.hide()
            picture.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(picture);label=QLabel(kind);label.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(label)
            row=model.historical_frequency(graph,node,kind,frequencies);known=model.type_match(node,kind)
            value='已读'if known=='observed'else'模板固定'if known=='template'else f"历史 {row['frequency']:.2%}"if row else'无对应样本'
            self.type_values[kind]=value;rate=QLabel(value);rate.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(rate)
            if row:cell.setToolTip(f"同层、距入口相同步数：{row['count']} / {row['total']}个节点记录。分母未按本图候选重新归一化。")
            grid.addWidget(cell,i//3,i%3)
        if not types:body.addWidget(QLabel('类型尚未确认；不把全目录当作此处候选。'))
        try:dossier=model.node_dossier(graph,node_id,config)
        except(ValueError,TypeError,KeyError):dossier=None
        self.entry_buttons=[]
        for label,kind,rows in [('事件候选','event',(dossier or{}).get('rows',[])),('作战候选','battle',(dossier or{}).get('battle_rows',[])),('已读历史事件','event',(dossier or{}).get('history_observed_event_rows',[])),('已读历史作战','battle',(dossier or{}).get('history_observed_battle_rows',[]))]:
            if not rows:continue
            heading=QLabel(label+f' · {len(rows)}项');body.addWidget(heading);cards=QGridLayout();cards.setColumnStretch(0,1);cards.setColumnStretch(1,1);body.addLayout(cards)
            for i,row in enumerate(rows):
                path=model.event_picture(row['id'])if kind=='event'else None
                title=row.get('title')or'名称未确认';icon=QIcon(str(path))if path else QIcon(QPixmap.fromImage(view.sprite_for('作战'if kind=='battle'else'不期而遇')))
                button=NodeEntryButton(title,path,icon)
                historical=label.startswith('已读历史');button.setProperty('referenceScope','history'if historical else'candidate')
                button.setToolTip(title+'\n'+('本局曾读到的内容，仅供回看；不表示现在再次发生，不计入当前候选或出现次数。点击在地图侧栏阅读。'if historical else'点击在地图侧栏阅读。资料候选不等于本局实际出现；发生概率未核验。'))
                button.clicked.connect(lambda checked=False,k=kind,identity=row['id']:self.entryRequested.emit(node_id,k,identity));cards.addWidget(button,i//2,i%2);self.entry_buttons.append((kind,row['id'],button))
        body.addStretch();old=self.scroll.takeWidget();self.scroll.setWidget(content)
        if old:old.deleteLater()
        self.scroll.verticalScrollBar().setValue(offset);return True

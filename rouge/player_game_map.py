"""One verified exploration overlay owns drawing, input regions and node cards."""
import time,math
import cv2
import numpy as np
from PySide6.QtCore import QObject,QTimer,Qt,QPointF,QPoint,QRect,QSize,QEvent,Signal
from PySide6.QtGui import QPainter,QColor,QPen,QRegion,QPixmap,QIcon
from PySide6.QtWidgets import QWidget,QApplication,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QToolButton,QPushButton,QScrollArea

def payload(reference,current,snapshot,run_id,now=None,*,diagnostics=None):
    def reject(reason):
        if diagnostics is not None:diagnostics["reason"]=reason
        return None
    now=time.time()if now is None else now
    if diagnostics is not None:diagnostics['evaluated_at']=now
    if not reference or not current or not snapshot or not snapshot.get('active')or not snapshot.get('foreground_on_game'):return reject('window_not_eligible')
    if reference.get('run_id')!=run_id:return reject('run_changed')
    observation=reference['observation'];graph=observation.get('map')or{}
    if graph.get('status')!='matched'or observation.get('page')not in('exploration','node_detail'):return reject('page_or_map_unmatched')
    if diagnostics is not None:
        diagnostics.update(run_id=run_id,zone_id=graph.get('zone_id'),template_id=graph.get('template_id'))
    for frame,label,limit in ((reference,'reference',30),(current,'current',2)):
        if type(frame.get('captured_at'))not in(int,float):return reject(label+'_timestamp_invalid')
        age=now-frame['captured_at']
        if diagnostics is not None:diagnostics.update({label+'_age_s':age,label+'_captured_at':frame['captured_at']})
        if not 0<=age<=limit:return reject(label+'_expired' if label=='reference' else 'current_frame_expired')
        if tuple(frame.get('target',{}).get(k)for k in('hwnd','pid'))!=tuple(snapshot['key']):return reject('window_changed')
    source=reference['image'];image=current['image'];rect=reference.get('client_rect')
    if rect is None or rect!=current.get('client_rect')or source.shape!=image.shape:return reject('geometry_changed')
    x0,y0,x1,y1=rect;h,w=source.shape[:2]
    if not 0<=x0<x1<=w or not 0<=y0<y1<=h or(x1-x0,y1-y0)!=tuple(snapshot['physical_client'][2:]):return reject('client_bounds_invalid')
    from .run_config import config_data
    title=config_data()['zones'].get(graph.get('zone_id'),{}).get('name')
    header=next((t for t in observation.get('texts',[])if t.get('text')==title and t.get('confidence',0)>=.85),None)
    if not header:return reject('title_missing')
    anchors=[];box=header['box'];anchors.append((int(min(p[0]for p in box)*w),int(min(p[1]for p in box)*h),int(max(p[0]for p in box)*w)+1,int(max(p[1]for p in box)*h)+1,False))
    labels=[node for node in graph.get('nodes',[])if node.get('visible')is True and node.get('label_box')]
    label_anchors=len(labels)>=3
    points=[]
    area=snapshot['logical_client']
    for node in graph.get('nodes',[]):
        center=node.get('center')
        if not isinstance(center,(list,tuple))or len(center)!=2 or any(type(v)not in(int,float)or not math.isfinite(v)for v in center):continue
        x,y=center[0]*w,center[1]*h
        if not x0<=x<x1 or not y0<=y<y1:continue
        points.append((node['id'],(x-x0)*area.width()/(x1-x0),(y-y0)*area.height()/(y1-y0)))
        if label_anchors and node.get('visible')is True and node.get('label_box'):
            box=node['label_box'];anchors.append((int(min(p[0]for p in box)*w),int(min(p[1]for p in box)*h),int(max(p[0]for p in box)*w)+1,int(max(p[1]for p in box)*h)+1,True))
        elif not label_anchors and node.get('visible')is True:anchors.append((round(x)-12,round(y)-12,round(x)+13,round(y)+13,False))
    pointer_boxes=[frame['pointer_bounds']for frame in(reference,current)if frame.get('pointer_bounds')is not None]
    occluded=[a for a in anchors[1:]if any(a[0]<b[2]and b[0]<a[2]and a[1]<b[3]and b[1]<a[3]for b in pointer_boxes)]
    anchors=[anchors[0]]+[a for a in anchors[1:]if a not in occluded]
    if diagnostics is not None:diagnostics.update(anchor_count=len(anchors),cursor_occluded_anchors=len(occluded),anchor_strategy='node_labels'if label_anchors else'exact_legacy_centers')
    if len(anchors)<4:return reject('anchors_insufficient')
    for x,y,u,v,label in anchors:
        if not 0<=x<u<=w or not 0<=y<v<=h:return reject('anchor_pixels_changed')
        before,after=source[y:v,x:u],image[y:v,x:u]
        if np.array_equal(before,after):continue
        if not label:return reject('anchor_pixels_changed')
        # Only current OCR-confirmed labels use structural matching. Animated
        # icon centers are not static controls. Position, title, window and the
        # original30s/2s freshness limits still have to agree independently.
        a=cv2.cvtColor(before,cv2.COLOR_BGR2GRAY).astype(np.float32);b=cv2.cvtColor(after,cv2.COLOR_BGR2GRAY).astype(np.float32)
        # Remove slow background glow while retaining same-position lettering.
        a-=cv2.GaussianBlur(a,(0,0),2);b-=cv2.GaussianBlur(b,(0,0),2)
        correlation=float(cv2.matchTemplate(b,a,cv2.TM_CCOEFF_NORMED)[0,0])
        contrast=float(b.std()/max(1.,a.std()))
        if diagnostics is not None:diagnostics['label_min_correlation']=min(diagnostics.get('label_min_correlation',1.),correlation)
        if not math.isfinite(correlation)or correlation<.99 or not .9<=contrast<=1.1:
            return reject('anchor_pixels_changed')
    if diagnostics is not None:diagnostics['reason']='eligible'
    return {'graph':graph,'points':points,'rect':area,'scope':'fresh_pixels_registered_map'}

TYPE_KINDS=('秘境行商','诡意行商','误入奇境','狭路相逢','不期而遇','作战','紧急作战','险路恶敌','得偿所愿','安全的角落','应急助力','失与得','先行一步','“居民”据点','命运所指','曲折密道','险路小径','险路尽头','羽瞰点')

def registered_rows(graph,kind,frequencies):
    """Bind a public floor/distance bucket to one confirmed template position."""
    from .player_map_reference import overlay_rows
    from .map_recognition import map_data
    rows=overlay_rows(graph,kind,frequencies)
    template=next((t for t in map_data()['templates']if t['id']==graph.get('template_id')and t['zone_id']==graph.get('zone_id')),None)
    positions={n['id']:n for n in template['nodes']}if template else{}
    for node in graph['nodes']:
        fixed=positions.get(node['id']);mapped=bool(graph.get('status')=='matched'and fixed and
            (node.get('row'),node.get('col'),node.get('distance'))==(fixed['row'],fixed['col'],fixed['distance'])and
            sum(n['id']==node['id']for n in graph['nodes'])==1)
        rows[node['id']]['position_mapped']=mapped
        if not mapped:rows[node['id']]['frequency']=None
    return rows

def frequency_text(row):
    return '—'if row is None else '0%'if row['frequency']==0 else f"{row['frequency']:.2%}"

def battle_targets(node):
    """A node kind is not a stage identity; only its bound title/variant opens URLs."""
    from urllib.parse import quote
    from .catalog import catalog
    from .tomimi_reference import target
    content=node.get('content')or node.get('remembered_content')or{}
    if content.get('kind')!='battle' or content.get('source')!='same_frame_selected_node':return {}
    sid=content.get('variant_id');stage=catalog()['stages'].get(sid)
    if not stage or stage['name']!=content.get('title'):return {}
    result={'enemy':{'stage_id':sid,'name':stage['name'],'provider':'PRTS',
        'url':'https://prts.wiki/w/'+quote(stage['code']+'_'+stage['name'],safe='_')+'#'+quote('敌方情报')}}
    tomimi=target({'id':sid,'stage':stage})
    if tomimi:result['map']=tomimi
    return result

class OverlaySurface(QWidget):
    def __init__(self,parent,controller):
        flags=Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.WindowTransparentForInput|Qt.WindowType.WindowDoesNotAcceptFocus
        super().__init__(parent,flags);self.controller=controller;self.data=None;self.rows={};self.kind=None;self.frequencies=None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground);self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setProperty('playerVisibility','ephemeral');self.setWindowTitle('地图历史频率')
    def paintEvent(self,event):
        if not self.data:return
        from .player_map import node_sprite
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        label_font=self.font();label_font.setPixelSize(11);p.setFont(label_font);p.setPen(QColor('#e5eeee'));strip=self.controller.interaction.strip.geometry()
        p.drawText(QRect(strip.left()-4,strip.top()-22,strip.width()+8,18),Qt.AlignmentFlag.AlignCenter,'历史频率')
        font=self.font();font.setBold(True);font.setPointSizeF(12);p.setFont(font);count=0
        for identity,x,y in self.data['points']:
            row=self.rows.get(identity)
            if not row or row['match']!='candidate' or row['frequency']is None:continue
            size=max(24,min(44,self.height()*.055));icon=node_sprite(self.kind)
            if not icon.isNull():
                p.setOpacity(.85);p.drawImage(QRect(round(x-size/2),round(y-size/2),round(size),round(size)),icon);p.setOpacity(1)
            text=frequency_text(row['frequency']);caption=self.data['label_rects'].get(identity,QRect(round(x-max(80,p.fontMetrics().horizontalAdvance(text)+12)/2),round(y+size/2+3),max(80,p.fontMetrics().horizontalAdvance(text)+12),p.fontMetrics().height()+4))
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor(13,22,25,245));p.drawRoundedRect(caption.adjusted(-4,-2,4,2),8,8)
            tx=caption.center().x()-p.fontMetrics().horizontalAdvance(text)/2;ty=caption.center().y()+(p.fontMetrics().ascent()-p.fontMetrics().descent())/2
            p.setPen(QColor(0,0,0,190));p.drawText(QPointF(tx+1.5,ty+1.5),text)
            p.setPen(QColor(255,255,255));p.drawText(QPointF(tx,ty),text);count+=1
        self.controller.painted(count)

class RoundPanel(QWidget):
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setBrush(QColor(35,48,54,225));p.setPen(QPen(QColor(166,185,188,140),1));radius=self.width()/2 if self.width()<80 else 14;p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1),radius,radius)

class NodeCard(RoundPanel):
    def __init__(self,parent,controller):
        super().__init__(parent);self.controller=controller;self.binding=None;self.content_key=None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setObjectName('gameNodeCard');self.setStyleSheet('#gameNodeCard QLabel{color:#f4f7f7;background:transparent;border:0;} #gameNodeCard QPushButton,#gameNodeCard QToolButton{color:#eef5f5;background:rgba(255,255,255,15);border:1px solid rgba(205,225,225,50);border-radius:7px;padding:7px;} #gameNodeCard QPushButton:hover,#gameNodeCard QToolButton:hover{background:rgba(255,255,255,40);} #gameNodeCard QPushButton:disabled{color:#849093;}')
        self.body=QVBoxLayout(self);self.body.setContentsMargins(18,16,18,16);self.body.setSpacing(14)
        self.heading=QLabel('历史频率 · 路标Wiki');self.heading.setStyleSheet('font-size:12pt;font-weight:600;')
        heading=QHBoxLayout();heading.addWidget(self.heading,1)
        self.close_button=QToolButton();self.close_button.setText('×');self.close_button.setToolTip('关闭节点卡');self.close_button.setAccessibleName('关闭节点卡')
        self.close_button.clicked.connect(lambda:controller.dismiss_card('close_button'));heading.addWidget(self.close_button);self.body.addLayout(heading)
        self.date=QLabel();self.body.addWidget(self.date);self.evidence=QLabel();self.evidence.setWordWrap(True);self.body.addWidget(self.evidence)
        self.cells=QWidget();self.grid=QGridLayout(self.cells);self.grid.setContentsMargins(0,4,0,4);self.grid.setHorizontalSpacing(20);self.grid.setVerticalSpacing(18)
        for i in range(3):self.grid.setColumnStretch(i,1)
        self.types_scroll=QScrollArea();self.types_scroll.setWidgetResizable(True);self.types_scroll.setFrameShape(QScrollArea.Shape.NoFrame);self.types_scroll.setWidget(self.cells)
        self.types_scroll.setStyleSheet('QScrollArea,QWidget{background:transparent;border:0;} QScrollBar:vertical{background:transparent;width:4px;} QScrollBar::handle:vertical{background:#67777c;border-radius:2px;min-height:24px;} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}');self.body.addWidget(self.types_scroll);self.values={}
        self.buttons=QWidget();row=QHBoxLayout(self.buttons);row.setContentsMargins(0,0,0,0);self.enemy=QPushButton('敌方情报');self.map=QPushButton('地图');row.addWidget(self.enemy);row.addWidget(self.map);self.body.addWidget(self.buttons)
        self.enemy.clicked.connect(lambda:controller.open_web('enemy'));self.map.clicked.connect(lambda:controller.open_web('map'))
        self.stage_notice=QLabel();self.body.addWidget(self.stage_notice)
        bottom=QHBoxLayout();self.source=QToolButton();self.source.setText('来源');self.source.setCheckable(True);bottom.addWidget(self.source);bottom.addStretch();self.more=QPushButton('更多');bottom.addWidget(self.more);self.body.addLayout(bottom)
        self.details=QLabel();self.details.setWordWrap(True);self.details.hide();self.body.addWidget(self.details)
        self.source.toggled.connect(self.show_source);self.more.clicked.connect(controller.open_more);self.hide()
    def paintEvent(self,event):
        super().paintEvent(event)
        if self.controller.pending_card is not None:
            self.controller.record('card_painted',node_id=self.controller.card_node,latency_ms=(time.perf_counter()-self.controller.pending_card)*1000);self.controller.pending_card=None
    def show_source(self,value):
        self.details.setVisible(value);self.adjustSize();self.controller.place_card();self.controller.record('source_expanded',expanded=value)
    def install(self,binding,graph,node,frequencies):
        from .player_map_reference import candidate_types,type_match
        from .player_map import node_sprite
        types=candidate_types(node);rows={kind:registered_rows(graph,kind,frequencies)[node['id']]for kind in types};targets=battle_targets(node)
        key=(binding,types,repr(rows),node.get('observed_type'),node.get('template_type'),node.get('remembered_type'),repr(targets),frequencies.identity)
        self.binding=binding
        if key==self.content_key:return
        self.content_key=key;self.values={}
        while self.grid.count():self.grid.takeAt(0).widget().deleteLater()
        evidence='已读类型'if node.get('observed_type')in types else'模板固定'if node.get('template_type')else'候选类型'
        if node.get('remembered_type'):evidence+=' · 原为'+node['remembered_type']
        self.evidence.setText(evidence)
        for i,kind in enumerate(types):
            row=rows[kind];value=frequency_text(row['frequency'])
            if row['match']=='candidate'and not row['position_mapped']:value='暂无资料'
            elif row['match']!='candidate':value='已读'if row['match']=='observed'else'模板固定'if row['match']=='template'else'本局记录'
            cell=QWidget();layout=QVBoxLayout(cell);layout.setContentsMargins(0,0,0,0);layout.setSpacing(6)
            picture=QLabel();picture.setAlignment(Qt.AlignmentFlag.AlignCenter);image=node_sprite(kind)
            if not image.isNull():picture.setPixmap(QPixmap.fromImage(image).scaled(34,34,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:picture.hide()
            layout.addWidget(picture)
            label=QLabel(kind);label.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(label);rate=QLabel(value);rate.setAlignment(Qt.AlignmentFlag.AlignCenter);rate.setStyleSheet('font-size:12pt;font-weight:700;');layout.addWidget(rate);self.grid.addWidget(cell,i//3,i%3);cell.show();self.values[kind]=value
        if not types:self.grid.addWidget(QLabel('暂无资料'),0,0)
        self.grid.invalidate();self.grid.activate();self.types_scroll.setFixedHeight(min(280,self.grid.sizeHint().height()+4))
        meta=frequencies.metadata or{};self.date.setText('统计更新 '+meta.get('updatedAt','—')[:10]);self.details.setText('路标Wiki · '+meta.get('sourceSchemaVersion','—')+'\n同层、距入口最短步数相同的全部节点记录；不按本局候选重新分配。')
        self.targets=targets;battle=any('作战'in kind or kind in('险路恶敌','险路尽头')for kind in types)
        self.buttons.setVisible(battle)
        self.enemy.setEnabled('enemy'in self.targets);self.map.setEnabled('map'in self.targets)
        tip=''if self.targets else'关卡待确认：请先在游戏中查看该节点详情'
        self.enemy.setToolTip(tip);self.map.setToolTip(tip or('暂无对应地图网页'if'map'not in self.targets else''))
        self.stage_notice.setText('关卡待确认'if battle and not self.targets else'地图暂无资料'if battle and'map'not in self.targets else'');self.stage_notice.setVisible(bool(self.stage_notice.text()))
        self.setFixedWidth(max(280,min(380,round(self.parentWidget().width()*.205))));self.adjustSize()

class InteractionSurface(QWidget):
    def __init__(self,parent,controller):
        flags=Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint
        super().__init__(parent,flags);self.controller=controller;self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground);self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.setWindowTitle('地图节点交互');self.setProperty('playerVisibility','ephemeral')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.strip=RoundPanel(self);layout=QVBoxLayout(self.strip);layout.setContentsMargins(5,12,5,12)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QScrollArea.Shape.NoFrame);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet('QScrollArea,QWidget{background:transparent;border:0;} QToolButton{background:transparent;border:0;border-radius:22px;} QToolButton:checked{background:rgba(210,240,225,45);} QToolButton:hover{background:rgba(210,240,225,25);}')
        body=QWidget();buttons=QVBoxLayout(body);buttons.setContentsMargins(0,0,0,0);buttons.setSpacing(12);self.buttons={}
        from .player_map import node_sprite
        for kind in TYPE_KINDS:
            button=QToolButton();button.setFixedSize(44,44);button.setIcon(QIcon(QPixmap.fromImage(node_sprite(kind))));button.setIconSize(QSize(38,38));button.setCheckable(True);button.setToolTip(kind+' · 历史频率');button.setAccessibleName('叠加类型：'+kind);button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(lambda checked=False,k=kind:controller.set_kind(k if checked else None));buttons.addWidget(button);self.buttons[kind]=button
        buttons.addStretch();scroll.setWidget(body);layout.addWidget(scroll);self.card=NodeCard(self,controller)
    def paintEvent(self,event):
        if not self.controller.current:return
        p=QPainter(self);p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor(0,0,0,1))
        for rect in self.controller.current['label_rects'].values():p.drawRect(rect.adjusted(-4,-4,4,4))
    def register(self,data):
        self.setGeometry(data['rect']);self.strip.setGeometry(round(self.width()*.014),round(self.height()*.24),54,min(360,round(self.height()*.4)))
        region=QRegion(self.strip.geometry())
        for rect in data['label_rects'].values():region|=QRegion(rect.adjusted(-4,-4,4,4))
        if self.card.isVisible():
            region|=QRegion(self.card.geometry())
        if self.mask()!=region:self.setMask(region)
        self.show();self.update()
    def mousePressEvent(self,event):
        # Presses ignored by the card or type strip bubble here; they must not
        # open a node caption hidden underneath.
        if event.button()==Qt.MouseButton.LeftButton and self.childAt(event.position().toPoint())is None:
            identity=self.controller.hit(event.position())
            self.controller.record('node_pressed',x=event.position().x(),y=event.position().y(),hit=identity)
            if identity:self.controller.open_node(identity)

class GameMapOverlay(QObject):
    """One interface owns registration, pixels, input regions, card and navigation."""
    kindChanged=Signal(object)
    mousePressed=Signal(object)
    def __init__(self,companion,owner,*,statistics_source=None):
        super().__init__(companion);self.companion=companion;self.owner=owner;self.statistics_source=statistics_source;self.enabled=False;self.kind=None;self.current=None;self.pending_paint=None;self.pending_card=None;self.card_node=None;self.view=None
        self.surface=OverlaySurface(companion,self);self.interaction=InteractionSurface(companion,self);self.card=self.interaction.card
        from .player_map_reference import default_frequencies
        self.frequencies=statistics_source.index if statistics_source is not None else default_frequencies();self.surface.frequencies=self.frequencies
        if statistics_source is not None:statistics_source.changed.connect(self.refresh_statistics)
        self.timer=QTimer(self);self.timer.setInterval(500);self.timer.timeout.connect(self.tick);self.timer.start()
        self.focus_return_timer=QTimer(self);self.focus_return_timer.setSingleShot(True);self.focus_return_timer.setInterval(80);self.focus_return_timer.timeout.connect(self.return_game_focus)
        self.mouse_listener=None;self.mousePressed.connect(self.outside_click,Qt.ConnectionType.QueuedConnection)
        QApplication.instance().installEventFilter(self)
    def record(self,action,**fields):
        audit=self.owner.session_recorder
        if audit is not None:audit.event('map_overlay_interaction',action=action,**fields)
    def refresh_statistics(self):
        self.frequencies=self.statistics_source.index;self.surface.frequencies=self.frequencies;self.card.content_key=None;self.tick()
    def set_enabled(self,value):self.enabled=bool(value);self.tick()
    def set_kind(self,value):
        if value==self.kind:return
        self.kind=value;self.pending_paint=time.perf_counter();self.kindChanged.emit(value)
        for name,button in self.interaction.buttons.items():button.setChecked(name==value)
        self.record('type_selected',kind=value);self.tick()
    def painted(self,count):
        if self.pending_paint is not None:
            self.record('percentages_painted',kind=self.kind,latency_ms=(time.perf_counter()-self.pending_paint)*1000,count=count);self.pending_paint=None
    def tick(self):
        self.current=None;c=self.companion;reference=self.owner.map_overlay_reference
        audit=self.owner.session_recorder;started=time.perf_counter();decision={'reason':'disabled'if not self.enabled else'reference_or_companion_unavailable'}
        if self.enabled and reference and not self.owner.closing and c.hidden_windows is None:
            snapshot=c.game_binding.api.read(c.game_binding.target())
            # A user's click may activate this overlay; showing it never does.
            if snapshot and snapshot.get('foreground_hwnd')==int(self.interaction.winId()):
                snapshot={**snapshot,'foreground_on_game':True}
                decision['foreground_scope']='overlay_interaction'
            self.current=payload(reference,self.owner.capture.buffer.latest(),snapshot,self.owner.run.state['id'],diagnostics=decision)
        if not self.current:
            self.surface.hide();self.surface.data=None;self.dismiss_card(decision['reason']);self.interaction.hide()
        else:
            self.snapshot=snapshot
            graph=self.current['graph'];saved=self.owner.run.state.get('maps',{}).get(graph['zone_id'])or{}
            if saved.get('template_id')==graph['template_id']and saved.get('captured_at')==reference['captured_at']:self.current['graph']=saved
            graph=self.current['graph'];h,w=reference['image'].shape[:2];x0,y0,x1,y1=reference['client_rect'];area=self.current['rect'];labels={}
            visible={n['id']for n in reference['observation']['map']['nodes']if n.get('visible')is True}
            self.current['points']=[p for p in self.current['points']if p[0]in visible]
            visible.intersection_update(p[0]for p in self.current['points'])
            for node in graph['nodes']:
                box=node.get('label_box')
                if box and node['id']in visible:
                    x=round((min(p[0]for p in box)*w-x0)*area.width()/(x1-x0));y=round((min(p[1]for p in box)*h-y0)*area.height()/(y1-y0))
                    u=round((max(p[0]for p in box)*w-x0)*area.width()/(x1-x0));v=round((max(p[1]for p in box)*h-y0)*area.height()/(y1-y0));labels[node['id']]=QRect(x,y,u-x,v-y)
            self.current['label_rects']=labels;self.surface.data=self.current;self.surface.kind=self.kind
            self.surface.rows=registered_rows(graph,self.kind,self.frequencies)if self.kind else{}
            self.surface.setGeometry(self.current['rect']);self.surface.show();self.surface.update()
            if self.card_node:
                key=(self.owner.run.state['id'],graph['zone_id'],graph['template_id'],self.card_node)
                node=next((n for n in graph['nodes']if n['id']==self.card_node),None)
                if node and self.card.binding==key and any(p[0]==self.card_node for p in self.current['points']):self.card.install(key,graph,node,self.frequencies);self.place_card()
                else:self.dismiss_card('node_scope_changed')
            self.interaction.register(self.current)
        if audit is not None:audit.overlay({**decision,'evaluation_ms':(time.perf_counter()-started)*1000},did_show=self.surface.isVisible(),enabled=self.enabled,kind=self.kind)
    def hit(self,point):
        # Only captions are input regions; node icons stay with the game.
        position=QPoint(round(point.x()),round(point.y()))
        labels=[key for key,rect in self.current['label_rects'].items()if rect.adjusted(-4,-4,4,4).contains(position)]if self.current else[]
        return labels[0]if len(labels)==1 else None
    def open_node(self,identity):
        started=time.perf_counter();self.tick()
        if not self.current:return
        self.pending_card=started
        graph=self.current['graph'];node=next(n for n in graph['nodes']if n['id']==identity)
        self.card_node=identity;binding=(self.owner.run.state['id'],graph['zone_id'],graph['template_id'],identity)
        self.card.install(binding,graph,node,self.frequencies);self.card.show();self.place_card();self.interaction.register(self.current)
        if self.mouse_listener is None and QApplication.platformName()=='windows':
            from pynput.mouse import Listener,Button
            def click(x,y,button,pressed,injected):
                if pressed and button==Button.left and self.card.binding is not None:self.mousePressed.emit((self.card.binding,x,y))
            self.mouse_listener=Listener(on_click=click,suppress=False);self.mouse_listener.start();self.mouse_listener.wait()
            self.record('mouse_listener_started',listener_id=id(self.mouse_listener))
        self.record('card_shown',node_id=identity,latency_ms=(time.perf_counter()-started)*1000)
    def place_card(self):
        if not self.current or not self.card_node:return
        _,x,y=next(p for p in self.current['points']if p[0]==self.card_node)
        self.card.move(max(78,min(round(x)+40,self.interaction.width()-self.card.width()-12)),max(12,min(round(y)-80,self.interaction.height()-self.card.height()-12)))
        self.interaction.register(self.current)
    def dismiss_card(self,reason='dismissed'):
        if self.card.isVisible():self.record('card_dismissed',reason=reason,node_id=self.card_node)
        self.card.hide();self.card_node=None;self.card.binding=None;self.pending_card=None
        if self.mouse_listener is not None:
            listener=self.mouse_listener;self.mouse_listener=None;listener.stop();listener.join()
            self.record('mouse_listener_stopped',listener_id=id(listener),reason=reason)
        if self.current is not None:self.interaction.register(self.current)
    def outside_click(self,reading):
        binding,x,y=reading
        if not self.card.isVisible()or binding!=self.card.binding:return
        client=self.current['rect'];physical=self.snapshot['physical_client'];point=QPoint(round((x-physical[0])*client.width()/physical[2]),round((y-physical[1])*client.height()/physical[3]))
        caption=any(rect.adjusted(-4,-4,4,4).contains(point)for rect in self.current['label_rects'].values())
        if not self.card.geometry().contains(point)and not self.interaction.strip.geometry().contains(point)and not caption:
            self.dismiss_card('outside_click')
    def return_game_focus(self):
        snapshot=self.companion.game_binding.api.read(self.companion.game_binding.target())
        if (not snapshot or not snapshot.get('cursor_on_game')
                or snapshot.get('foreground_hwnd')!=int(self.interaction.winId())
                or QApplication.platformName()!='windows'):
            return
        from ctypes import windll
        from ctypes.wintypes import HWND
        accepted=bool(windll.user32.SetForegroundWindow(HWND(snapshot['key'][0])))
        self.record('game_focus_returned',accepted=accepted,reason='pointer_returned_to_game')
    def eventFilter(self,widget,event):
        if widget is self.interaction and event.type()==QEvent.Type.Leave:
            self.focus_return_timer.start()
        elif widget is self.interaction and event.type()==QEvent.Type.Enter:
            self.focus_return_timer.stop()
        if event.type()==QEvent.Type.KeyPress and event.key()==Qt.Key.Key_Escape and self.card.isVisible()and isinstance(widget,QWidget)and widget.window()in QApplication.topLevelWidgets():
            if widget is self.interaction or self.interaction.isAncestorOf(widget)or widget is self.companion or self.companion.isAncestorOf(widget):
                self.dismiss_card('escape');return True
        return False
    def open_web(self,kind):
        if not self.current or not self.card_node:return
        target=self.card.targets.get(kind)
        if target:
            from .player_reference_links import open_overlay_web
            self.record('web_open',provider=target.get('provider','Tomimi'));open_overlay_web(self.companion,target,self.current['rect'])
    def open_more(self):
        if not self.current or not self.card_node:return
        graph=self.current['graph'];identity=self.card_node
        from .player_map_hover import NodeHoverCard
        from .player_map import node_sprite
        from types import SimpleNamespace
        if self.view is None:
            self.view=SimpleNamespace(sprite_for=node_sprite,historical=False,frequencies=self.frequencies);self.more_card=NodeHoverCard(self.companion);self.more_card.entryRequested.connect(self.open_entry)
        self.more_binding=self.card.binding
        self.view.frequencies=self.frequencies;self.view.historical=False
        self.more_card.install(self.card.binding,graph,identity,self.owner.run.state.get('config',{}),self.view)
        self.more_card.show();self.more_card.move(self.card.mapToGlobal(QPoint(0,0)))
    def open_entry(self,node_id,kind,identity):
        if self.owner.run.state['id']!=self.more_binding[0]:return False
        self.companion.open_map();panel=self.companion.map_popup.panel
        for i in range(panel.floors.count()):
            zone=panel.floors.tabData(i)
            if zone==self.more_binding[1]and panel.graphs[zone].get('template_id')==self.more_binding[2]:
                panel.floors.setCurrentIndex(i);return panel.open_hover_entry(node_id,kind,identity)
        return False
    def close(self):
        self.timer.stop();self.focus_return_timer.stop();self.current=None;self.dismiss_card('window_closed')
        QApplication.instance().removeEventFilter(self);self.surface.close();self.interaction.close()
        if self.view:self.more_card.close()

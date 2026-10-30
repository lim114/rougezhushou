"""Whole-floor player map: game artwork, recorded floors and local node dossiers."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import json
from PySide6.QtCore import Qt,QRectF,QPointF,QPoint,Signal,QTimer,QSize
from PySide6.QtGui import QColor,QPainter,QPen,QImage,QPainterPath,QIcon,QPixmap
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QTabBar,
    QPushButton,QScrollArea,QSplitter,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QComboBox,QToolButton,QLineEdit)
from .map_view import MapView
from .run_config import config_data

ART=Path(__file__).with_name('data')/'map-art'
ICONS={'起点':'start','作战':'combat','紧急作战':'emergency-combat','险路恶敌':'danger-enemy',
 '不期而遇':'encounter','得偿所愿':'wish','失与得':'gain-loss','先行一步':'first-step',
 '狭路相逢':'narrow-meet','羽瞰点':'overlook','曲折密道':'winding-path',
 '诡意行商':'rogue-trader','秘境行商':'secret-trader','安全的角落':'safe-corner',
 '应急助力':'emergency-aid','“居民”据点':'settlement','居民据点':'settlement',
 '误入奇境':'wrong-turn','命运所指':'fate-choice','险路小径':'danger-path',
 '险路尽头':'danger-end','未知的诡秘':'unknown-mystery','未知的凶戾':'unknown-ferocity'}

def zone_info(graph):
    zone=config_data()['zones'].get((graph or {}).get('zone_id'),{})
    icon=zone.get('zoneIconId');floor=next((i for i in range(1,7)if icon==f'zone_{i}'),None)
    return zone.get('name')or'区域未确认',floor

def node_style(node):
    """A single guessed candidate never becomes a revealed game icon."""
    observed=node.get('observed_type');remembered=node.get('remembered_type')
    if observed=='林间空地':return observed,('原为'+remembered if remembered else'已读空地'),'history'if remembered else'observed'
    if observed and not observed.startswith(('未知','类型未确认')):return observed,'已读','observed'
    if remembered:return remembered,'本局记录','history'
    if node.get('template_type'):return node['template_type'],'模板固定','template'
    if observed in ICONS:return observed,'尚未揭示','unknown'
    return None,'类型未确认','unknown'

def dossier_graph(graph):
    """Constrain reference candidates by fixed template facts without asserting a read."""
    query=deepcopy(graph)
    for node in query['nodes']:
        observed=node.get('observed_type')
        if node.get('template_type') and (not observed or observed.startswith(('未知','类型未确认'))):
            node['prediction']={**(node.get('prediction')or{}),'candidates':[node['template_type']]}
    return query

@lru_cache(maxsize=1)
def art_manifest():return json.loads((ART/'sources.json').read_text('utf8'))

class PreviewMapView(MapView):
    nodeHovered=Signal(str,QPoint)
    def __init__(self):
        super().__init__();self.atlas=QImage(str(ART/'nodes.png'));self.background=QImage();self.icons={};self.filter_kind=None;self.overlay={};self.hover_id=None;self.frequencies=None;self.setMinimumSize(480,300)
    def sprite_for(self,kind):
        key=ICONS.get(kind);sprite=art_manifest()['sprites'].get(key)
        if not sprite:return QImage()
        if key not in self.icons:
            import numpy as np
            icon=self.atlas.copy(sprite['x'],sprite['y'],sprite['width'],sprite['height']).convertToFormat(QImage.Format.Format_RGBA8888)
            alpha=np.frombuffer(icon.bits(),np.uint8).reshape(icon.height(),icon.width(),4)[:,:,3];ys,xs=np.where(alpha>16)
            self.icons[key]=icon.copy(int(xs.min()),int(ys.min()),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1))if len(xs)else icon
        return self.icons[key]
    def set_type_filter(self,kind):
        from .player_map_reference import overlay_rows
        self.filter_kind=kind;self.overlay=overlay_rows(self.graph,kind,self.frequencies)if kind else{};self.update()
    def set_map(self,graph,image=None,*,historical=False):
        _,floor=zone_info(graph)
        # Decoration only. Exact zone/topology remains in the graph, not inferred from artwork.
        name=f'area-{floor+1}.png'if floor and floor<6 else'area-1.png'if floor==6 else'blindness.png'
        self.background=QImage(str(ART/name));super().set_map(graph,None,historical=historical);self.set_type_filter(self.filter_kind)
    def _positions(self):
        canvas=QRectF(self.contentsRect()).adjusted(38,36,-38,-72);points={}
        if self.graph:
            rows=self.graph['grid']['rows'];cols=self.graph['grid']['cols']
            step=min(canvas.width()/max(1,cols-1),canvas.height()/max(1,rows-1),125)
            left=canvas.center().x()-(cols-1)*step/2;top=canvas.center().y()-(rows-1)*step/2
            points={n['id']:QPointF(left+n['col']*step,top+n['row']*step)for n in self.graph['nodes']}
        return QRectF(self.contentsRect()),points
    def icon_size(self):
        _,points=self._positions();xs=sorted({round(p.x(),2)for p in points.values()})
        return min(60,max(28,min((b-a for a,b in zip(xs,xs[1:])),default=85)*.66))
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.fillRect(self.rect(),QColor('#0e1717'))
        if not self.background.isNull():p.drawImage(QRectF(self.rect()),self.background);p.fillRect(self.rect(),QColor(0,0,0,85))
        if not self.graph:
            p.setPen(QColor('#eff4f4'));p.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'尚无本局地图记录\n后台读到地图后会自动显示');return
        _,points=self._positions();size=self.icon_size()
        for a,b in self.graph.get('edges',[]):
            if a not in points or b not in points:continue
            path=QPainterPath(points[a]);mid=(points[a]+points[b])/2
            path.cubicTo(QPointF(mid.x(),points[a].y()),QPointF(mid.x(),points[b].y()),points[b])
            p.setPen(QPen(QColor(135,143,136,90),7,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap));p.drawPath(path)
            p.setPen(QPen(QColor(183,189,179,135),1.5));p.drawPath(path)
        font=self.font();font.setPointSize(9);p.setFont(font)
        for node in self.graph['nodes']:
            point=points[node['id']];kind,note,evidence=node_style(node);overlay=self.overlay.get(node['id'],{});match=overlay.get('match')
            image_kind=self.filter_kind if match=='candidate'else kind;icon=self.sprite_for(image_kind)
            p.setOpacity(.22 if match=='excluded'else .7 if match=='candidate'else .64 if evidence=='template'else 1)
            if not icon.isNull():
                rect=QRectF(point.x()-size/2,point.y()-size/2,size,size)
                factor=min(rect.width()/icon.width(),rect.height()/icon.height());w,h=icon.width()*factor,icon.height()*factor
                p.drawImage(QRectF(point.x()-w/2,point.y()-h/2,w,h),icon)
            else:
                p.setPen(QPen(QColor('#acb9b3'),1.7));p.setBrush(QColor('#0c1415'));p.drawEllipse(point,6,6)
                if kind!='林间空地':p.setPen(QColor('#ffffff'));p.drawText(QRectF(point.x()-14,point.y()-12,28,24),Qt.AlignmentFlag.AlignCenter,'?')
            p.setOpacity(1)
            if match in('observed','template','candidate','history'):
                p.setPen(QPen(QColor('#ffd087')if match=='history'else QColor('#8cebd2'),1.7,Qt.PenStyle.DashLine if match=='candidate'else Qt.PenStyle.SolidLine));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(point,size/2+7,size/2+7)
            if node['id']==self.selected:
                p.setPen(QPen(QColor('#ffffff'),2));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(point,size/2+4,size/2+4)
            current=self.graph.get('current_node')
            last=self.graph.get('last_confirmed_current_node')or current
            if node['id']==current and not self.historical or node['id']==last and(self.historical or not current):
                p.setPen(QPen(QColor('#ffcf79')if self.historical or not current else QColor('#a1ffd2'),2,Qt.PenStyle.DashLine if self.historical or not current else Qt.PenStyle.SolidLine))
                p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(point,size/2+9,size/2+9)
                p.drawText(QRectF(point.x()-55,point.y()-size/2-30,110,20),Qt.AlignmentFlag.AlignCenter,'最近位置'if self.historical or not current else'当前位置')
            width=max(46,min(112,self._badge_width(points)));label=kind or'类型未确认'
            if kind=='林间空地'and node.get('remembered_type'):label='原·'+node['remembered_type']
            if evidence=='template':label+='·模板'
            elif evidence=='history'and kind!='林间空地':label+='·记录'
            if match=='candidate':label='候选·'+self.filter_kind
            badge=QRectF(point.x()-width/2,point.y()+size/2+2,width,20)
            p.fillRect(badge,QColor(0,0,0,145));p.setPen(QColor('#ffdb9f')if evidence=='history'else QColor('#f4f5f0'))
            p.drawText(badge,Qt.AlignmentFlag.AlignCenter,p.fontMetrics().elidedText(label,Qt.TextElideMode.ElideRight,int(width)-4))
            if match=='candidate':
                row=overlay.get('frequency');label=f"历史 {row['frequency']:.1%}"if row else'历史比例未知'
                badge.translate(0,20);p.fillRect(badge,QColor(13,42,35,220));p.setPen(QColor('#bef6e3'));p.drawText(badge,Qt.AlignmentFlag.AlignCenter,label)
    def _hit(self,point):
        _,points=self._positions();size=self.icon_size()
        hits=[((p-point).manhattanLength(),key)for key,p in points.items()if QRectF(p.x()-size/2-5,p.y()-size/2-7,size+10,size+35).contains(point)]
        return min(hits)[1]if hits else None
    def mouseMoveEvent(self,event):
        node_id=self._hit(event.position());self.setCursor(Qt.CursorShape.PointingHandCursor if node_id else Qt.CursorShape.ArrowCursor)
        if node_id!=self.hover_id:self.hover_id=node_id;self.nodeHovered.emit(node_id or'',event.globalPosition().toPoint())
    def leaveEvent(self,event):
        self.hover_id=None;self.nodeHovered.emit('',QPoint());super().leaveEvent(event)

class MapPanel(QWidget):
    def __init__(self,owner,*,statistics_source=None):
        super().__init__();self.owner=owner;self.statistics_source=statistics_source;self.epoch=None;self.graphs={};self.readings={};self.entry_readings={};self.selected_zone=None;self.rows={};self.selected_reference=None;self.reading_key=None;self.reference_popup=None;self.reference_binding=None
        body=QVBoxLayout(self);body.setContentsMargins(5,0,5,5)
        head=QHBoxLayout();self.floors=QTabBar();self.floors.setExpanding(False);self.floors.setAccessibleName('本局已记录楼层');head.addWidget(self.floors,1)
        self.zoom=QComboBox();self.zoom.addItems(['适应窗口','放大125%','放大150%','放大200%']);head.addWidget(self.zoom)
        self.details_toggle=QPushButton('节点资料');self.details_toggle.setCheckable(True);head.addWidget(self.details_toggle);body.addLayout(head)
        self.finder_toggle=QPushButton('查找节点');self.finder_toggle.setCheckable(True);head.addWidget(self.finder_toggle)
        self.finder=QWidget();finder=QVBoxLayout(self.finder);finder.setContentsMargins(0,0,0,0);body.addWidget(self.finder);self.finder.hide();self.finder_toggle.toggled.connect(self.finder.setVisible)
        self.latest_position=QPushButton('回到最近已读位置');self.latest_position.clicked.connect(self.focus_latest_position)
        find=QHBoxLayout();self.node_query=QLineEdit();self.node_query.setMaxLength(100);self.node_query.setPlaceholderText('查找本局已记录楼层中的类型、位置或已读名称');self.node_query.setStyleSheet('QLineEdit{color:#28332e;background:white;border:1px solid #d2d9d5;border-radius:7px;padding:5px;}');find.addWidget(self.node_query,1);self.node_results=QComboBox();self.node_results.setMinimumWidth(200);find.addWidget(self.node_results,2);self.find_node=QPushButton('定位节点');find.addWidget(self.find_node);find.addWidget(self.latest_position);finder.addLayout(find);self.node_query.textChanged.connect(self.update_node_finder);self.find_node.clicked.connect(self.locate_found_node)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        read_row=QHBoxLayout();self.read_scope=QComboBox()
        for label,key in(('查找全部记录',None),('只查已读或历史类型','read'),('只查模板固定类型','fixed'),('只查尚待确认类型','unknown')):self.read_scope.addItem(label,key)
        read_row.addWidget(self.read_scope);self.coverage_notice=QLabel();self.coverage_notice.setWordWrap(True);read_row.addWidget(self.coverage_notice,1);finder.addLayout(read_row);self.read_scope.currentIndexChanged.connect(self.update_node_finder)
        from .player_resource_strip import ResourceStrip
        self.resources=ResourceStrip(owner.run.state);body.addWidget(self.resources)
        self.floor_resources=QLabel();self.floor_resources.setWordWrap(True);body.addWidget(self.floor_resources)
        row=QHBoxLayout();self.filter_notice=QLabel();self.filter_notice.setWordWrap(True);row.addWidget(self.filter_notice,1);self.clear_filter=QPushButton('显示所有类型');self.clear_filter.clicked.connect(lambda:self.set_type_filter(None));row.addWidget(self.clear_filter);body.addLayout(row);self.clear_filter.hide()
        self.split=QSplitter();self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.view=PreviewMapView();self.scroll.setWidget(self.view);self.split.addWidget(self.scroll)
        self.palette=QWidget();self.palette.setObjectName('mapNodePalette');self.palette.setFixedWidth(58);self.palette.setStyleSheet('#mapNodePalette{background:#253b39;border:1px solid #82958c;border-radius:23px;} QToolButton{border:0;background:transparent;border-radius:18px;} QToolButton:checked{background:#658979;}')
        palette_layout=QVBoxLayout(self.palette);palette_layout.setContentsMargins(6,12,6,12);self.type_buttons={}
        for kind in ('秘境行商','诡意行商','误入奇境','狭路相逢','不期而遇'):
            button=QToolButton();button.setFixedSize(44,44);button.setIcon(QIcon(QPixmap.fromImage(self.view.sprite_for(kind))))
            button.setIconSize(QSize(36,36));button.setCheckable(True);button.setToolTip(kind+'：在助手地图查看对应位置和历史节点比例');button.setAccessibleName('地图类型筛选：'+kind);button.clicked.connect(lambda checked=False,k=kind:self.set_type_filter(k if checked else None));palette_layout.addWidget(button);self.type_buttons[kind]=button
        palette_layout.addStretch();stage=QWidget();stage_layout=QHBoxLayout(stage);stage_layout.setContentsMargins(0,0,0,0);stage_layout.addWidget(self.palette);stage_layout.addWidget(self.scroll,1);self.split.insertWidget(0,stage)
        self.drawer=QWidget();right=QVBoxLayout(self.drawer);right.setContentsMargins(6,0,0,0);self.title=QLabel('请选择地图节点');self.title.setWordWrap(True);right.addWidget(self.title)
        self.entry_search=QLineEdit();self.entry_search.setMaxLength(100);self.entry_search.setPlaceholderText('筛选所选节点的事件或作战名称');self.entry_search.setStyleSheet('QLineEdit{color:#28332e;background:white;border:1px solid #d2d9d5;border-radius:7px;padding:5px;}');right.addWidget(self.entry_search)
        self.entry_count=QLabel();self.entry_count.setWordWrap(True);right.addWidget(self.entry_count)
        self.entries=QTreeWidget();self.entries.setHeaderHidden(True);right.addWidget(self.entries,2)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);right.addWidget(self.detail,2)
        self.open_button=QPushButton('打开完整资料');self.open_button.setEnabled(False);right.addWidget(self.open_button)
        self.split.addWidget(self.drawer);self.split.setSizes([700,300]);self.drawer.hide();body.addWidget(self.split,1)
        legend=QLabel('实色：已读　半透明：模板固定　金字：本局记录　?：未确认　历史比例不是本局概率；连线不代表现在可通行');legend.setWordWrap(True);body.addWidget(legend)
        self.floors.currentChanged.connect(self.show_floor);self.zoom.currentIndexChanged.connect(self.change_zoom);self.view.nodeSelected.connect(self.select_interactive)
        self.details_toggle.toggled.connect(self.drawer.setVisible);self.entries.currentItemChanged.connect(self.read_entry);self.open_button.clicked.connect(self.open_entry);self.refresh()
        self.entry_search.textChanged.connect(lambda _text:self.selected(self.view.selected))
        from .player_map_hover import NodeHoverCard
        self.hover_card=NodeHoverCard(self);self.hover_card.entryRequested.connect(self.open_hover_entry);self.hover_pending=None
        self.hover_timer=QTimer(self);self.hover_timer.setSingleShot(True);self.hover_timer.setInterval(180);self.hover_timer.timeout.connect(self.show_hover)
        self.leave_timer=QTimer(self);self.leave_timer.setSingleShot(True);self.leave_timer.setInterval(220);self.leave_timer.timeout.connect(self.leave_hover)
        self.view.nodeHovered.connect(self.queue_hover);self.hover_card.entered.connect(self.leave_timer.stop);self.hover_card.left.connect(self.leave_timer.start)
        if self.statistics_source is not None:self.statistics_source.changed.connect(self.refresh_statistics)
    def refresh_statistics(self):
        if self.isVisible():self.refresh()
    def set_type_filter(self,kind):
        for name,button in self.type_buttons.items():button.setChecked(name==kind)
        self.view.set_type_filter(kind)
        self.filter_notice.setText(('正在查看：'+kind+'。实线为已读或模板，虚线为候选；不保证可达或掉落。')if kind else'')
        self.clear_filter.setVisible(bool(kind))
        companion=getattr(self.owner,'compact_window',None)
        if companion is not None and hasattr(companion,'game_overlay'):companion.game_overlay.set_kind(kind)
    def queue_hover(self,node_id,point):
        self.hover_timer.stop();self.leave_timer.stop()
        if not node_id:self.hover_pending=None;self.leave_timer.start();return
        self.hover_pending=(node_id,point);self.hover_timer.start()
    def leave_hover(self):
        if not self.hover_card.pinned and not self.hover_card.underMouse():self.hover_card.hide()
    def show_hover(self):
        if not self.hover_pending or not self.view.graph:return
        node_id,point=self.hover_pending;graph=self.view.graph;binding=(self.epoch,graph.get('zone_id'),graph.get('template_id'),node_id)
        if not self.hover_card.install(binding,graph,node_id,self.owner.run.state.get('config',{}),self.view):return
        self.hover_card.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,bool(self.window().windowFlags()&Qt.WindowType.WindowStaysOnTopHint));self.hover_card.show()
        area=self.screen().availableGeometry();self.hover_card.move(max(area.left(),min(point.x()+22,area.right()-self.hover_card.width())),max(area.top(),min(point.y()+12,area.bottom()-self.hover_card.height())))
    def open_hover_entry(self,node_id,kind,identity):
        from .player_map_reference import node_dossier
        try:dossier=node_dossier(self.view.graph,node_id,self.owner.run.state.get('config',{}))or{}
        except(ValueError,KeyError,TypeError):return False
        names=('rows','history_observed_event_rows')if kind=='event'else('battle_rows','history_observed_battle_rows')if kind=='battle'else()
        if not any(row.get('id')==identity for name in names for row in dossier.get(name,[])):return False
        self.hover_card.dismiss();self.view.select_node(node_id)
        self.entry_search.clear()
        for i in range(self.entries.topLevelItemCount()):
            group=self.entries.topLevelItem(i)
            for j in range(group.childCount()):
                item=group.child(j);key=item.data(0,Qt.ItemDataRole.UserRole)
                if key and key[1:]==(kind,identity):group.setExpanded(True);self.entries.setCurrentItem(item);return True
        return False
    def hideEvent(self,event):
        if hasattr(self,'hover_card'):self.hover_timer.stop();self.hover_card.dismiss()
        self.close_reference()
        super().hideEvent(event)
    def refresh(self):
        epoch=self.owner.run.state['id'];old_key=self.selected_zone
        if self.statistics_source is not None:self.view.frequencies=self.statistics_source.index
        if epoch!=self.epoch:
            self.close_reference()
            self.readings.clear();self.entry_readings.clear();self.reading_key=None;blocked=self.entry_search.blockSignals(True);self.entry_search.clear();self.entry_search.blockSignals(blocked);old_key=None;self.epoch=epoch;self.selected_zone=None;self.view.set_map(None)
        self.graphs=deepcopy(self.owner.run.state.get('maps',{}));original=self.owner.map_view
        self.resources.refresh(self.owner.run.state)
        if original.graph and original.graph.get('template_id')==(self.graphs.get(original.graph.get('zone_id'))or{}).get('template_id'):self.graphs[original.graph['zone_id']]=deepcopy(original.graph)
        self.latest_position.setEnabled(self.latest_position_key()is not None)
        self.update_node_finder();self.floors.blockSignals(True)
        while self.floors.count():self.floors.removeTab(0)
        for key,graph in sorted(self.graphs.items(),key=lambda pair:(zone_info(pair[1])[1]or 99,pair[0])):
            name,floor=zone_info(graph);i=self.floors.addTab(('第'+str(floor)+'层 · 'if floor else'')+name);self.floors.setTabData(i,key)
        keys=[self.floors.tabData(i)for i in range(self.floors.count())];wanted=old_key if old_key in keys else(original.graph or{}).get('zone_id')
        self.floors.setCurrentIndex(keys.index(wanted)if wanted in keys else 0 if keys else-1);self.floors.blockSignals(False);self.show_floor()
    def update_node_finder(self,*_):
        from .player_map_find import rows
        previous=self.node_results.currentData();self.node_results.blockSignals(True);self.node_results.clear()
        from .player_map_find import coverage
        c=coverage(self.graphs);self.coverage_notice.setText(f"本局已保存{len(self.graphs)}个区域：已读或历史类型{c['read']}处，模板固定{c['fixed']}处，尚待确认{c['unknown']}处。只筛查找列表，不改变地图候选。")
        for row in rows(self.graphs,self.node_query.text(),self.read_scope.currentData()):self.node_results.addItem(row['label'],row['key'])
        i=self.node_results.findData(previous)
        if i>=0:self.node_results.setCurrentIndex(i)
        self.node_results.blockSignals(False);self.find_node.setEnabled(self.node_results.count()>0)
        self.node_results.setToolTip('只查找本局保存的地图位置；已读名称须直接关联到该节点。搜索不到不表示未生成。')
    def locate_found_node(self):
        key=self.node_results.currentData()
        if not key:return False
        zone,template,node=key;g=self.graphs.get(zone)
        if not g or g.get('template_id')!=template or not any(n['id']==node for n in g['nodes']):return False
        index=next((i for i in range(self.floors.count())if self.floors.tabData(i)==zone),None)
        if index is None:return False
        self.floors.setCurrentIndex(index);self.view.select_node(node);self.select_interactive(node);return True
    def latest_position_key(self):
        original=self.owner.map_view;g=original.graph
        if not g:return None
        saved=self.graphs.get(g.get('zone_id'));node=g.get('current_node')or g.get('last_confirmed_current_node')
        if not saved or saved.get('template_id')!=g.get('template_id')or not any(n['id']==node for n in saved.get('nodes',[])):return None
        return (g['zone_id'],g['template_id'],node)
    def focus_latest_position(self):
        self.refresh();key=self.latest_position_key()
        if not key:return False
        index=next((i for i in range(self.floors.count())if self.floors.tabData(i)==key[0]),None)
        if index is None:return False
        self.floors.setCurrentIndex(index);self.view.select_node(key[2]);self.select_interactive(key[2]);return True
    def show_floor(self,*_):
        if self.view.graph:
            old=(self.view.graph.get('zone_id'),self.view.graph.get('template_id'));self.readings[old]=(self.view.selected,self.selected_reference,self.detail.verticalScrollBar().value())
        index=self.floors.currentIndex();key=self.floors.tabData(index)if index>=0 else None
        graph=self.graphs.get(key);original=self.owner.map_view;self.selected_zone=key
        from .player_floor_resources import snapshots,snapshot_text
        row=next((r for r in reversed(snapshots(self.owner.run.state))if r['zone_id']==key),None);self.floor_resources.setText(snapshot_text(row))
        if hasattr(self,'hover_card')and ((self.view.graph or{}).get('zone_id'),(self.view.graph or{}).get('template_id'))!=(key,(graph or{}).get('template_id')):
            self.hover_timer.stop();self.leave_timer.stop();self.hover_pending=None;self.hover_card.dismiss()
        historical=not(graph and original.graph and key==original.graph.get('zone_id')and graph.get('template_id')==original.graph.get('template_id')and not original.historical)
        saved=self.readings.get((key,(graph or{}).get('template_id')),(None,None,0))
        self.view.blockSignals(True);self.view.set_map(graph,historical=historical)
        if graph and saved[0]in {n['id']for n in graph['nodes']}:self.view.select_node(saved[0])
        self.view.blockSignals(False);self.selected(self.view.selected)
        for i in range(self.entries.topLevelItemCount()):
            parent=self.entries.topLevelItem(i)
            for j in range(parent.childCount()):
                item=parent.child(j)
                if item.data(0,Qt.ItemDataRole.UserRole)==saved[1]:self.entries.setCurrentItem(item)
        self.detail.verticalScrollBar().setValue(saved[2])
        self.restore_entry_expansion()
        name,_=zone_info(graph);self.status.setText(name+(' · 本局历史记录'if historical else' · 最近确认的地图')+'；未揭示内容仍是候选。'if graph else'尚无本局地图记录；读到地图后自动显示，不填入示例。')
        from .run_config import difficulty_value
        config=self.owner.run.state.get('config',{});grade=difficulty_value(config.get('difficulty'))
        squad=config.get('squad',{}).get('name');squad=squad if isinstance(squad,str) and squad else'未读'
        self.status.setText(self.status.text()+f'　保密等级 {grade if grade is not None else "未读"} · 分队 {squad}')
        self.change_zoom()
        if hasattr(self,'hover_card')and self.hover_card.isVisible():
            binding=self.hover_card.binding
            if not graph or not binding or binding[:3]!=(self.epoch,graph.get('zone_id'),graph.get('template_id')):self.hover_card.dismiss()
            else:self.hover_card.install(binding,graph,binding[-1],self.owner.run.state.get('config',{}),self.view,force=True)
        self.check_reference()
    def change_zoom(self,*_):
        scale=(1,1.25,1.5,2)[self.zoom.currentIndex()];self.scroll.setWidgetResizable(scale==1)
        if scale!=1:self.view.resize(max(600,int(self.scroll.viewport().width()*scale)),max(330,int(self.scroll.viewport().height()*scale)))
    def select_interactive(self,node_id):
        self.selected(node_id)
        if node_id:self.details_toggle.setChecked(True)
    def selected(self,node_id):
        from . import player_map_reference as model
        from .map_reporting import format_node,location
        self.remember_entry_reading();graph=self.view.graph
        if self.reference_popup is not None and self.reference_binding[:4]!=(self.epoch,(graph or{}).get('zone_id'),(graph or{}).get('template_id'),node_id):self.close_reference()
        self.reading_key=((graph or{}).get('zone_id'),(graph or{}).get('template_id'),node_id)
        reading=self.entry_readings.get(self.reading_key,{})
        blocked=self.entry_search.blockSignals(True);self.entry_search.setText(reading.get('query',''));self.entry_search.blockSignals(blocked)
        keep=reading.get('selected');query=self.entry_search.text().strip().casefold()
        self.entries.blockSignals(True);self.entries.clear();self.rows={};self.selected_reference=None;self.open_button.setEnabled(False)
        self.entry_count.setText('所选节点的资料尚未读取；未用全目录填充。')
        if not graph or not node_id:
            self.title.setText('请选择地图节点');self.detail.setPlainText('点击图标查看事件、奖励与作战；可切换已记录楼层。');self.entries.blockSignals(False);return
        node=next(n for n in graph['nodes']if n['id']==node_id);kind,note,basis=node_style(node)
        self.title.setText(location(node,graph['grid']['rows'])+' · '+(kind or'类型未确认')+(' · '+note if basis=='history'else''))
        try:dossier=model.node_dossier(graph,node_id,self.owner.run.state.get('config',{}))
        except(ValueError,KeyError,TypeError)as error:
            self.detail.setPlainText('节点资料尚不能读取：'+str(error));self.entries.blockSignals(False);return
        if dossier is None:
            self.detail.setPlainText(format_node(graph,node_id,historical=self.view.historical)+'\n\n类型尚未确认，暂不把全目录当作本节点候选。');self.entries.blockSignals(False);return
        groups=[('事件候选','event',dossier['rows']),('作战预览','battle',dossier['battle_rows']),('功能说明','function',dossier['function_rows']),('已读历史事件','event',dossier['history_observed_event_rows']),('已读历史作战','battle',dossier['history_observed_battle_rows']),('已列条件排除的事件（不是候选）','event',dossier.get('excluded_event_candidates',[]))]
        chosen=None
        total=sum(len(rows)for _,_,rows in groups);shown=0
        for label,kind,rows in groups:
            full_count=len(rows);rows=[row for row in rows if not query or query in(row.get('title')or row.get('node_type')or'').casefold()]
            if not rows:continue
            shown+=len(rows);root=QTreeWidgetItem([label+(f'（{len(rows)}/{full_count}）'if query else f'（{len(rows)}）')]);root.setData(0,257,label);self.entries.addTopLevelItem(root)
            for row in rows:
                key=(label,kind,row.get('id')or row.get('node_type'));item=QTreeWidgetItem([row.get('title')or row.get('node_type')or'功能节点']);item.setToolTip(0,item.text(0));item.setData(0,Qt.ItemDataRole.UserRole,key);root.addChild(item);self.rows[key]=row
                if key==keep:chosen=item
            root.setExpanded(not label.startswith('已列条件排除'))
        self.entries.blockSignals(False);self.detail.setPlainText(format_node(graph,node_id,historical=self.view.historical))
        if chosen:self.entries.setCurrentItem(chosen)
        self.restore_entry_expansion()
        self.detail.verticalScrollBar().setValue(reading.get('scroll',0)if chosen else 0)
        self.entry_count.setText(f'显示{shown}/{total}项所选节点资料，含单列的排除说明。名称筛选只改变查阅列表，不改变候选与历史比例；无匹配不表示没有其它内容。')
        # Only synchronize the owning current map; historical-floor reading never rebinds it.
        if self.owner.map_view.graph and graph.get('zone_id')==self.owner.map_view.graph.get('zone_id')and graph.get('template_id')==self.owner.map_view.graph.get('template_id'):self.owner.map_view.select_node(node_id)

    def remember_entry_reading(self):
        if not self.reading_key or not all(isinstance(value,str)and value for value in self.reading_key):return
        expanded={}
        for i in range(self.entries.topLevelItemCount()):
            root=self.entries.topLevelItem(i);label=root.data(0,257)
            if isinstance(label,str):expanded[label]=root.isExpanded()
        previous=self.entry_readings.get(self.reading_key,{})
        self.entry_readings[self.reading_key]={'query':self.entry_search.text(),'selected':self.selected_reference,
            'expanded':{**previous.get('expanded',{}),**expanded},'scroll':self.detail.verticalScrollBar().value()}

    def restore_entry_expansion(self):
        expanded=self.entry_readings.get(self.reading_key,{}).get('expanded',{})
        for i in range(self.entries.topLevelItemCount()):
            root=self.entries.topLevelItem(i);label=root.data(0,257);root.setExpanded(expanded.get(label,not str(label).startswith('已列条件排除')))
    def read_entry(self,*_):
        item=self.entries.currentItem();key=item.data(0,Qt.ItemDataRole.UserRole)if item else None;row=self.rows.get(key)
        self.selected_reference=key if row else None;self.open_button.setEnabled(bool(row and key[1]in('event','battle')))
        if self.reference_popup is not None and self.reference_binding!=self.reader_binding():self.close_reference()
        if not row:return
        from .player_node_information import node_information_text
        from .node_catalog_view import map_conditions
        graph=self.view.graph or {};context=map_conditions(graph,self.owner.run.state.get('config',{}))
        entry={'kind':key[1],'record':row,'history_context_reference':self.view.historical or key[0].startswith('已读历史')}
        context['entry_mode']='content'if entry['history_context_reference']else'natural'
        node=next((n for n in graph.get('nodes',[])if n['id']==self.view.selected),{})
        observed=node.get('observed_type');context['node_type']=observed if observed and not observed.startswith('未知')else node.get('template_type')
        text=node_information_text(entry,context=context)
        if key[0].startswith('已列条件排除'):text='【不属于本节点当前资料候选】\n排除依据：'+str(row.get('reason')or'请查看已列条件')+'\n这是固定目录的条件对照，不能替代当前服务器规则或证明其它层必定出现。\n\n'+text
        self.detail.setPlainText(text)
    def open_entry(self):
        binding=self.reader_binding();key=self.selected_reference
        self.refresh()
        if binding!=self.reader_binding():return False
        row=self.rows.get(key)
        if not row:return False
        self.close_reference()
        from .player_map_reader import make_reader
        popup=make_reader(key[1],row,self,historical=self.view.historical or key[0].startswith('已读历史'))
        if popup is not None:
            self.reference_popup=popup;self.reference_binding=binding
            popup.setWindowFlag(Qt.WindowType.Tool,True);popup.show()
            area=self.screen().availableGeometry();popup.move(max(area.left(),min(self.mapToGlobal(QPoint(20,20)).x(),area.right()-popup.width()+1)),max(area.top(),min(self.mapToGlobal(QPoint(20,20)).y(),area.bottom()-popup.height()+1)))
            return True
        # Retain the existing full-directory route when no exact floating
        # reader is available; never substitute another same-name instance.
        self.detail.appendPlainText('\n这份资料暂时没有可核对的完整浮窗入口，将在助手原目录继续查阅。')
        if key[1]=='battle':self.owner.show_catalog_battle(row['id'])
        elif key[1]=='event':self.owner.show_source_catalog_event(row['id'])
        else:return False
        self.owner.show();self.owner.raise_();self.owner.activateWindow()
        return True

    def reader_binding(self):
        graph=self.view.graph or{}
        return (self.epoch,graph.get('zone_id'),graph.get('template_id'),self.view.selected,self.selected_reference)

    def close_reference(self):
        if self.reference_popup is not None:self.reference_popup.close();self.reference_popup=None
        self.reference_binding=None

    def check_reference(self):
        if self.reference_popup is None:return
        if not self.reference_popup.isVisible():self.close_reference();return
        if self.reference_binding!=self.reader_binding():self.close_reference();return
        panel=getattr(self.reference_popup,'panel',None)
        if panel is not None and hasattr(panel,'refresh_reference')and panel.refresh_reference()is False:self.close_reference()

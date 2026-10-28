"""Whole-floor player map: game artwork, recorded floors and local node dossiers."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import json
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QColor,QPainter,QPen,QImage,QPainterPath
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QTabBar,
    QPushButton,QScrollArea,QSplitter,QTreeWidget,QTreeWidgetItem,QPlainTextEdit,QComboBox)
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
    def __init__(self):
        super().__init__();self.atlas=QImage(str(ART/'nodes.png'));self.background=QImage();self.icons={};self.setMinimumSize(480,300)
    def set_map(self,graph,image=None,*,historical=False):
        _,floor=zone_info(graph)
        # Decoration only. Exact zone/topology remains in the graph, not inferred from artwork.
        name=f'area-{floor+1}.png'if floor and floor<6 else'area-1.png'if floor==6 else'blindness.png'
        self.background=QImage(str(ART/name));super().set_map(graph,None,historical=historical)
    def _positions(self):
        canvas=QRectF(self.contentsRect()).adjusted(38,36,-38,-45);points={}
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
            point=points[node['id']];kind,note,evidence=node_style(node);key=ICONS.get(kind);sprite=art_manifest()['sprites'].get(key)
            p.setOpacity(.64 if evidence=='template' else 1)
            if sprite:
                if key not in self.icons:
                    import numpy as np
                    icon=self.atlas.copy(sprite['x'],sprite['y'],sprite['width'],sprite['height']).convertToFormat(QImage.Format.Format_RGBA8888)
                    alpha=np.frombuffer(icon.bits(),np.uint8).reshape(icon.height(),icon.width(),4)[:,:,3];ys,xs=np.where(alpha>16)
                    self.icons[key]=icon.copy(int(xs.min()),int(ys.min()),int(xs.max()-xs.min()+1),int(ys.max()-ys.min()+1))if len(xs)else icon
                rect=QRectF(point.x()-size/2,point.y()-size/2,size,size)
                icon=self.icons[key];factor=min(rect.width()/icon.width(),rect.height()/icon.height());w,h=icon.width()*factor,icon.height()*factor
                p.drawImage(QRectF(point.x()-w/2,point.y()-h/2,w,h),icon)
            else:
                p.setPen(QPen(QColor('#acb9b3'),1.7));p.setBrush(QColor('#0c1415'));p.drawEllipse(point,6,6)
                if kind!='林间空地':p.setPen(QColor('#ffffff'));p.drawText(QRectF(point.x()-14,point.y()-12,28,24),Qt.AlignmentFlag.AlignCenter,'?')
            p.setOpacity(1)
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
            badge=QRectF(point.x()-width/2,point.y()+size/2+2,width,20)
            p.fillRect(badge,QColor(0,0,0,145));p.setPen(QColor('#ffdb9f')if evidence=='history'else QColor('#f4f5f0'))
            p.drawText(badge,Qt.AlignmentFlag.AlignCenter,p.fontMetrics().elidedText(label,Qt.TextElideMode.ElideRight,int(width)-4))
    def _hit(self,point):
        _,points=self._positions();size=self.icon_size()
        hits=[((p-point).manhattanLength(),key)for key,p in points.items()if QRectF(p.x()-size/2-5,p.y()-size/2-7,size+10,size+35).contains(point)]
        return min(hits)[1]if hits else None

class MapPanel(QWidget):
    def __init__(self,owner):
        super().__init__();self.owner=owner;self.epoch=None;self.graphs={};self.readings={};self.selected_zone=None;self.rows={};self.selected_reference=None;self.reading_key=None
        body=QVBoxLayout(self);body.setContentsMargins(5,0,5,5)
        head=QHBoxLayout();self.floors=QTabBar();self.floors.setExpanding(False);self.floors.setAccessibleName('本局已记录楼层');head.addWidget(self.floors,1)
        self.zoom=QComboBox();self.zoom.addItems(['适应窗口','放大125%','放大150%','放大200%']);head.addWidget(self.zoom)
        self.details_toggle=QPushButton('节点资料');self.details_toggle.setCheckable(True);head.addWidget(self.details_toggle);body.addLayout(head)
        self.status=QLabel();self.status.setWordWrap(True);body.addWidget(self.status)
        self.split=QSplitter();self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.view=PreviewMapView();self.scroll.setWidget(self.view);self.split.addWidget(self.scroll)
        self.drawer=QWidget();right=QVBoxLayout(self.drawer);right.setContentsMargins(6,0,0,0);self.title=QLabel('请选择地图节点');self.title.setWordWrap(True);right.addWidget(self.title)
        self.entries=QTreeWidget();self.entries.setHeaderHidden(True);right.addWidget(self.entries,2)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);right.addWidget(self.detail,2)
        self.open_button=QPushButton('打开完整资料');self.open_button.setEnabled(False);right.addWidget(self.open_button)
        self.split.addWidget(self.drawer);self.split.setSizes([700,300]);self.drawer.hide();body.addWidget(self.split,1)
        legend=QLabel('实色：已读　半透明：模板固定　金字：本局记录　?：未确认　连线不代表现在可通行');legend.setWordWrap(True);body.addWidget(legend)
        self.floors.currentChanged.connect(self.show_floor);self.zoom.currentIndexChanged.connect(self.change_zoom);self.view.nodeSelected.connect(self.select_interactive)
        self.details_toggle.toggled.connect(self.drawer.setVisible);self.entries.currentItemChanged.connect(self.read_entry);self.open_button.clicked.connect(self.open_entry);self.refresh()
    def refresh(self):
        epoch=self.owner.run.state['id'];old_key=self.selected_zone
        if epoch!=self.epoch:
            self.readings.clear();old_key=None;self.epoch=epoch;self.selected_zone=None;self.view.set_map(None)
        self.graphs=deepcopy(self.owner.run.state.get('maps',{}));original=self.owner.map_view
        if original.graph and original.graph.get('template_id')==(self.graphs.get(original.graph.get('zone_id'))or{}).get('template_id'):self.graphs[original.graph['zone_id']]=deepcopy(original.graph)
        self.floors.blockSignals(True)
        while self.floors.count():self.floors.removeTab(0)
        for key,graph in sorted(self.graphs.items(),key=lambda pair:(zone_info(pair[1])[1]or 99,pair[0])):
            name,floor=zone_info(graph);i=self.floors.addTab(('第'+str(floor)+'层 · 'if floor else'')+name);self.floors.setTabData(i,key)
        keys=[self.floors.tabData(i)for i in range(self.floors.count())];wanted=old_key if old_key in keys else(original.graph or{}).get('zone_id')
        self.floors.setCurrentIndex(keys.index(wanted)if wanted in keys else 0 if keys else-1);self.floors.blockSignals(False);self.show_floor()
    def show_floor(self,*_):
        if self.view.graph:
            old=(self.view.graph.get('zone_id'),self.view.graph.get('template_id'));self.readings[old]=(self.view.selected,self.selected_reference,self.detail.verticalScrollBar().value())
        index=self.floors.currentIndex();key=self.floors.tabData(index)if index>=0 else None
        graph=self.graphs.get(key);original=self.owner.map_view;self.selected_zone=key
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
        name,_=zone_info(graph);self.status.setText(name+(' · 本局历史记录'if historical else' · 最近确认的地图')+'；未揭示内容仍是候选。'if graph else'尚无本局地图记录；读到地图后自动显示，不填入示例。')
        self.change_zoom()
    def change_zoom(self,*_):
        scale=(1,1.25,1.5,2)[self.zoom.currentIndex()];self.scroll.setWidgetResizable(scale==1)
        if scale!=1:self.view.resize(max(600,int(self.scroll.viewport().width()*scale)),max(330,int(self.scroll.viewport().height()*scale)))
    def select_interactive(self,node_id):
        self.selected(node_id)
        if node_id:self.details_toggle.setChecked(True)
    def selected(self,node_id):
        from . import node_catalog as model
        from .node_catalog_view import map_conditions
        from .map_reporting import format_node,location
        graph=self.view.graph;old=self.entries.currentItem();keep=old.data(0,Qt.ItemDataRole.UserRole)if old and self.reading_key==((graph or{}).get('zone_id'),(graph or{}).get('template_id'),node_id)else None
        self.reading_key=((graph or{}).get('zone_id'),(graph or{}).get('template_id'),node_id)
        self.entries.blockSignals(True);self.entries.clear();self.rows={};self.selected_reference=None;self.open_button.setEnabled(False)
        if not graph or not node_id:
            self.title.setText('请选择地图节点');self.detail.setPlainText('点击图标查看事件、奖励与作战；可切换已记录楼层。');self.entries.blockSignals(False);return
        node=next(n for n in graph['nodes']if n['id']==node_id);self.title.setText(location(node,graph['grid']['rows'])+' · '+(node_style(node)[0]or'类型未确认'))
        if node_style(node)[0]is None and not(node.get('prediction')or{}).get('candidates'):
            self.detail.setPlainText(format_node(graph,node_id,historical=self.view.historical)+'\n\n类型尚未确认，暂不把全目录当作本节点候选。');self.entries.blockSignals(False);return
        try:dossier=model.node_dossier(dossier_graph(graph),node_id,**map_conditions(graph,self.owner.run.state.get('config',{})))
        except(ValueError,KeyError,TypeError)as error:
            self.detail.setPlainText('节点资料尚不能读取：'+str(error));self.entries.blockSignals(False);return
        groups=[('事件候选','event',dossier['rows']),('作战预览','battle',dossier['battle_rows']),('功能说明','function',dossier['function_rows']),('已读历史事件','event',dossier['history_observed_event_rows']),('已读历史作战','battle',dossier['history_observed_battle_rows'])]
        chosen=None
        for label,kind,rows in groups:
            if not rows:continue
            root=QTreeWidgetItem([label+f'（{len(rows)}）']);self.entries.addTopLevelItem(root)
            for row in rows:
                key=(label,kind,row.get('id')or row.get('node_type'));item=QTreeWidgetItem([row.get('title')or row.get('node_type')or'功能节点']);item.setData(0,Qt.ItemDataRole.UserRole,key);root.addChild(item);self.rows[key]=row
                if key==keep:chosen=item
            root.setExpanded(True)
        self.entries.blockSignals(False);self.detail.setPlainText(format_node(graph,node_id,historical=self.view.historical))
        if chosen:self.entries.setCurrentItem(chosen)
        # Only synchronize the owning current map; historical-floor reading never rebinds it.
        if self.owner.map_view.graph and graph.get('zone_id')==self.owner.map_view.graph.get('zone_id')and graph.get('template_id')==self.owner.map_view.graph.get('template_id'):self.owner.map_view.select_node(node_id)
    def read_entry(self,*_):
        item=self.entries.currentItem();key=item.data(0,Qt.ItemDataRole.UserRole)if item else None;row=self.rows.get(key)
        self.selected_reference=key if row else None;self.open_button.setEnabled(bool(row and key[1]in('event','battle')))
        if not row:return
        from .node_catalog_view import event_text
        if key[1]=='event':text=event_text(row['id'])
        elif key[1]=='battle':text=row.get('title','')+'\n普通/紧急、敌人和地图请打开作战预览。\n这是资料候选，不表示本节点一定出现。'
        else:text='\n'.join(str(v)for k,v in row.items()if k in('node_type','description','description_text','notes'))or'功能条件详见节点完整资料。'
        self.detail.setPlainText(text)
    def open_entry(self):
        key=self.selected_reference;row=self.rows.get(key)
        if not row:return
        if key[1]=='battle':self.owner.show_catalog_battle(row['id'])
        elif key[1]=='event':self.owner.show_source_catalog_event(row['id'])
        else:return
        self.owner.show();self.owner.raise_();self.owner.activateWindow()

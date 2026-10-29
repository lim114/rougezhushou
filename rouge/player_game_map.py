"""Transparent, input-free annotations on a freshly corroborated game map."""
import time,math
import numpy as np
from PySide6.QtCore import QObject,QTimer,Qt,QPointF
from PySide6.QtGui import QPainter,QColor,QPen
from PySide6.QtWidgets import QWidget

def payload(reference,current,snapshot,run_id,now=None):
    now=time.time()if now is None else now
    if not reference or not current or not snapshot or not snapshot.get('active')or not snapshot.get('foreground_on_game'):return None
    if reference.get('run_id')!=run_id:return None
    observation=reference['observation'];graph=observation.get('map')or{}
    if graph.get('status')!='matched'or observation.get('page')not in('exploration','node_detail'):return None
    for frame,limit in ((reference,30),(current,2)):
        if type(frame.get('captured_at'))not in(int,float)or not 0<=now-frame['captured_at']<=limit:return None
        if tuple(frame.get('target',{}).get(k)for k in('hwnd','pid'))!=tuple(snapshot['key']):return None
    source=reference['image'];image=current['image'];rect=reference.get('client_rect')
    if rect is None or rect!=current.get('client_rect')or source.shape!=image.shape:return None
    x0,y0,x1,y1=rect;h,w=source.shape[:2]
    if not 0<=x0<x1<=w or not 0<=y0<y1<=h or(x1-x0,y1-y0)!=tuple(snapshot['physical_client'][2:]):return None
    from .run_config import config_data
    title=config_data()['zones'].get(graph.get('zone_id'),{}).get('name')
    header=next((t for t in observation.get('texts',[])if t.get('text')==title and t.get('confidence',0)>=.85),None)
    if not header:return None
    anchors=[];box=header['box'];anchors.append((int(min(p[0]for p in box)*w),int(min(p[1]for p in box)*h),int(max(p[0]for p in box)*w)+1,int(max(p[1]for p in box)*h)+1))
    points=[]
    area=snapshot['logical_client']
    for node in graph.get('nodes',[]):
        center=node.get('center')
        if not isinstance(center,(list,tuple))or len(center)!=2 or any(type(v)not in(int,float)or not math.isfinite(v)for v in center):continue
        x,y=center[0]*w,center[1]*h
        if not x0<=x<x1 or not y0<=y<y1:continue
        points.append((node['id'],(x-x0)*area.width()/(x1-x0),(y-y0)*area.height()/(y1-y0)))
        if node.get('visible')is True:anchors.append((round(x)-12,round(y)-12,round(x)+13,round(y)+13))
    if len(anchors)<4:return None
    for x,y,u,v in anchors:
        if not 0<=x<u<=w or not 0<=y<v<=h or not np.array_equal(source[y:v,x:u],image[y:v,x:u]):return None
    return {'graph':graph,'points':points,'rect':area,'scope':'fresh_pixels_registered_map'}

class OverlaySurface(QWidget):
    def __init__(self,parent):
        flags=Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.WindowTransparentForInput|Qt.WindowType.WindowDoesNotAcceptFocus
        super().__init__(parent,flags);self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground);self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.data=None;self.kind=None;self.setWindowTitle('地图只读标注')
    def paintEvent(self,event):
        if not self.data:return
        from .player_map_reference import overlay_rows
        rows=overlay_rows(self.data['graph'],self.kind);p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for identity,x,y in self.data['points']:
            row=rows[identity]
            if row['match']not in('observed','template','candidate','history'):continue
            text=('候选·'if row['match']=='candidate'else'原·'if row['match']=='history'else'')+self.kind
            if row['frequency']:text+=f" 历史{row['frequency']['frequency']:.1%}"
            p.setPen(QPen(QColor('#ffd38b')if row['match']=='history'else QColor('#92edd1'),2,Qt.PenStyle.DashLine if row['match']=='candidate'else Qt.PenStyle.SolidLine));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(QPointF(x,y),30,30)
            size=p.fontMetrics().horizontalAdvance(text)+12;p.fillRect(round(x-size/2),round(y+34),size,24,QColor(15,32,29,225));p.setPen(QColor('#eefcf4'));p.drawText(round(x-size/2+6),round(y+51),text)
        p.setPen(QColor('#d8f4e6'));p.drawText(14,24,'资料标注 · 候选不代表实际生成；历史比例不是本局概率')

class GameMapOverlay(QObject):
    def __init__(self,companion,owner):
        super().__init__(companion);self.companion=companion;self.owner=owner;self.enabled=False;self.kind=None;self.surface=OverlaySurface(companion);self.current=None
        self.timer=QTimer(self);self.timer.setInterval(500);self.timer.timeout.connect(self.tick);self.timer.start()
    def set_enabled(self,value):self.enabled=bool(value);self.tick()
    def set_kind(self,value):self.kind=value;self.tick()
    def tick(self):
        self.current=None;c=self.companion;reference=getattr(self.owner,'map_overlay_reference',None)
        if self.enabled and self.kind and reference and not self.owner.closing and c.hidden_windows is None:
            snapshot=c.game_binding.api.read(c.game_binding.target())
            self.current=payload(reference,self.owner.capture.buffer.latest(),snapshot,self.owner.run.state['id'])
        if not self.current:self.surface.hide();self.surface.data=None;return
        self.surface.data=self.current;self.surface.kind=self.kind;self.surface.setGeometry(self.current['rect']);self.surface.show();self.surface.update()
    def close(self):self.timer.stop();self.surface.close();self.current=None

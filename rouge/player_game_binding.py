"""Read-only native window identity/geometry and non-activating companion following."""
import time
from PySide6.QtCore import QObject,QTimer,QPoint,QRect,Qt,QEvent
from PySide6.QtWidgets import QApplication,QDialog
from shiboken6 import isValid
from .windows_dpi import physical_pixels


def logical_rect(client,monitor,logical_origin,scale):
    if not isinstance(scale,(int,float)) or not .5<=scale<=8:raise ValueError('无法核对屏幕缩放。')
    x,y,w,h=client
    if w<=0 or h<=0:raise ValueError('客户端范围无效。')
    return QRect(round(logical_origin[0]+(x-monitor[0])/scale),round(logical_origin[1]+(y-monitor[1])/scale),max(1,round(w/scale)),max(1,round(h/scale)))

class BindingApi:
    def read(self,target):
        import win32gui,win32process,win32api
        if not target:return None
        try:
            hwnd,pid=target['hwnd'],target['pid']
            with physical_pixels():
                if not win32gui.IsWindow(hwnd)or win32process.GetWindowThreadProcessId(hwnd)[1]!=pid:return None
                cursor=win32gui.GetCursorPos();active=win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)
                _,_,w,h=win32gui.GetClientRect(hwnd);x,y=win32gui.ClientToScreen(hwnd,(0,0));monitor=win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd))
                hit=win32gui.WindowFromPoint(cursor);hit=win32gui.GetAncestor(hit,2)if hit else None
            screens=[s for s in QApplication.screens()if s.name()==monitor['Device']]
            if len(screens)!=1:return None
            screen=screens[0];origin=screen.geometry().topLeft();rect=logical_rect((x,y,w,h),monitor['Monitor'],(origin.x(),origin.y()),screen.devicePixelRatio())
            foreground=win32gui.GetForegroundWindow()
            return {'target':dict(target),'key':(hwnd,pid),'physical_client':(x,y,w,h),'logical_client':rect,'cursor':cursor,'cursor_on_game':bool(active and hit==hwnd and x<=cursor[0]<x+w and y<=cursor[1]<y+h),'foreground_hwnd':foreground,'foreground_on_game':foreground==hwnd,'active':bool(active),'screen':screen}
        except (OSError,RuntimeError,ValueError,KeyError,TypeError,win32gui.error):return None

def clamp_window(widget,area):
    widget.move(max(area.left(),min(widget.x(),area.right()-widget.width()+1)),max(area.top(),min(widget.y(),area.bottom()-widget.height()+1)))

def outside_position(client,area,size,preferred=None):
    """Choose a screen-visible position entirely outside the game client."""
    gap=8;w,h=size.width(),size.height()
    bands=[QRect(area.left(),max(area.top(),client.bottom()+gap+1),area.width(),max(0,area.bottom()-client.bottom()-gap)),
           QRect(max(area.left(),client.right()+gap+1),area.top(),max(0,area.right()-client.right()-gap),area.height()),
           QRect(area.left(),area.top(),area.width(),max(0,min(area.bottom()+1,client.top()-gap)-area.top())),
           QRect(area.left(),area.top(),max(0,min(area.right()+1,client.left()-gap)-area.left()),area.height())]
    origin=preferred if preferred is not None else QPoint(client.right()-w+1,client.bottom()+gap+1)
    bands=[b.intersected(area)for b in bands]
    positions=[QPoint(max(b.left(),min(origin.x(),b.right()-w+1)),max(b.top(),min(origin.y(),b.bottom()-h+1)))
               for b in bands if b.width()>=w and b.height()>=h]
    if not positions:return None
    return min(positions,key=lambda p:(p-origin).manhattanLength())if preferred is not None else positions[0]

def retained_window(widget):
    role=widget.property('playerVisibility')
    return not widget.property('outsideSpaceHidden')and role!='ephemeral'and(role!='hover'or widget.pinned)

def parent_chain(widget):
    chain=[]
    while widget is not None:chain.append(widget);widget=widget.parentWidget()
    return chain

class GameWindowBinding(QObject):
    def __init__(self,companion,owner,api=None):
        super().__init__(companion);self.companion=companion;self.owner=owner;self.api=api or BindingApi()
        self.enabled=True;self.snapshot=None;self.previous=None;self.suspended=[];self.ever_bound=False
        self._targets=[];self._next_discovery=0.;self.status='尚未找到游戏；可先独立查阅。'
        self.timer=QTimer(self);self.timer.setInterval(250);self.timer.timeout.connect(self.tick);self.timer.start()
        QApplication.instance().installEventFilter(self)
    def target(self):
        selected=getattr(self.owner.capture,'target',None)
        if selected is not None:return selected
        if time.monotonic()>=self._next_discovery:
            from .app import list_game_windows
            self._targets=list_game_windows();self._next_discovery=time.monotonic()+2
        return self._targets[0]if len(self._targets)==1 else None
    def surfaces(self):
        c=self.companion
        roots=[c,c.active_popup,self.owner.player_notes,self.owner.public_archive,self.owner.public_statistics];found=[]
        for widget in QApplication.topLevelWidgets():
            if not isinstance(widget,QDialog):continue
            if widget.property('independentMapWeb'):continue
            chain=parent_chain(widget)
            if any(root in chain for root in roots):found.append((len(chain),widget))
        return [widget for _,widget in sorted(found,key=lambda row:row[0])]
    def eventFilter(self,widget,event):
        if event.type()==QEvent.Type.Close and(widget in self.suspended or widget in(self.companion.hidden_windows or[])):
            # Dispatch the original virtual close handler once, including an
            # ignored close from an editor with unsaved changes.
            widget.closeEvent(event)
            if event.isAccepted():
                closed={w for w in set(self.suspended).union(self.companion.hidden_windows or[])if not isValid(w)or widget in parent_chain(w)}
                for w in closed:
                    if isValid(w):w.setProperty('playerSuspended',False)
                self.suspended=[w for w in self.suspended if w not in closed]
                if self.companion.hidden_windows is not None:self.companion.hidden_windows=[w for w in self.companion.hidden_windows if w not in closed]
            return True
        return False
    def set_enabled(self,value):
        self.enabled=bool(value);self.previous=None
        if not self.enabled and self.companion.property('outsideSpaceHidden'):
            self.companion.setProperty('outsideSpaceHidden',False)
            if self.companion.hidden_windows is None:self.companion.show()
        self.tick()
    def restore(self):
        while self.suspended:
            w=self.suspended.pop(0)
            if isValid(w):
                if retained_window(w):w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);w.show()
                w.setProperty('playerSuspended',False)
    def apply(self,snapshot):
        self.snapshot=snapshot
        if self.enabled and snapshot is not None and snapshot['active']:self.ever_bound=True
        if QApplication.activeModalWidget()is not None:
            self.status='当前对话框操作结束后继续更新窗口跟随。';return
        unavailable=self.enabled and self.ever_bound and(snapshot is None or not snapshot['active'])
        if self.companion.hidden_windows is not None or unavailable:
            live=[w for w in self.surfaces()if w.isVisible()]
            self.suspended.extend(w for w in live if retained_window(w)and w not in self.suspended)
            for w in live:w.setProperty('playerSuspended',True)
            for w in live:
                w.hide()
                if not retained_window(w):w.setProperty('playerSuspended',False)
            if unavailable:self.status='游戏不可见或绑定失效；玩家小窗已隐藏，记录保留。'
            return
        if not self.enabled:
            self.restore();self.status='已暂停跟随游戏，窗口可自由移动。';return
        if snapshot is None or not snapshot['active']:self.restore();return
        current=snapshot['logical_client'];area=snapshot['screen'].availableGeometry();c=self.companion
        same=self.previous is not None and self.previous['key']==snapshot['key']
        visible=[w for w in self.surfaces()if retained_window(w)and(w.isVisible()or w in self.suspended)]
        if not same:
            c._dock_positioned=True
        elif current!=self.previous['logical_client']:
            old=self.previous['logical_client'];delta=current.topLeft()-old.topLeft()
            for w in visible:
                if w is c:continue
                else:w.move(w.pos()+delta)
        for w in visible:clamp_window(w,area)
        preferred=(c.pos()+current.bottomRight()-self.previous['logical_client'].bottomRight())if same and current!=self.previous['logical_client']else c.pos()if same else None
        position=outside_position(current,area,c.size(),preferred)
        was_hidden=bool(c.property('outsideSpaceHidden'));c.setProperty('outsideSpaceHidden',position is None)
        self.restore()
        if position is None:
            c.hide();self.status='游戏外侧没有空间，可从系统托盘打开助手。'
        else:
            c.move(position)
            if was_hidden:c.show()
            self.status='工具条位于游戏窗口外，随客户端移动。'
        self.previous=snapshot
    def tick(self):
        if self.owner.closing:return
        self.apply(self.api.read(self.target()))
        label=getattr(self.companion,'binding_status',None)
        if label is not None:label.setText(self.status)
    def close(self):self.timer.stop();QApplication.instance().removeEventFilter(self);self.suspended=[];self.snapshot=None

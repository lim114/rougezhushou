"""Read-only native window identity/geometry and non-activating companion following."""
import ctypes,time
from contextlib import contextmanager
from PySide6.QtCore import QObject,QTimer,QPoint,QRect,Qt,QEvent
from PySide6.QtWidgets import QApplication,QDialog
from shiboken6 import isValid

@contextmanager
def physical_pixels():
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.SetThreadDpiAwarenessContext.argtypes=[ctypes.c_void_p];user.SetThreadDpiAwarenessContext.restype=ctypes.c_void_p
    prior=user.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
    try:yield
    finally:
        if prior:user.SetThreadDpiAwarenessContext(prior)

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
            return {'target':dict(target),'key':(hwnd,pid),'physical_client':(x,y,w,h),'logical_client':rect,'cursor':cursor,'cursor_on_game':bool(active and hit==hwnd and x<=cursor[0]<x+w and y<=cursor[1]<y+h),'foreground_on_game':win32gui.GetForegroundWindow()==hwnd,'active':bool(active),'screen':screen}
        except (OSError,RuntimeError,ValueError,KeyError,TypeError,win32gui.error):return None

def clamp_window(widget,area):
    widget.move(max(area.left(),min(widget.x(),area.right()-widget.width()+1)),max(area.top(),min(widget.y(),area.bottom()-widget.height()+1)))

def retained_window(widget):
    role=widget.property('playerVisibility')
    return role!='ephemeral'and(role!='hover'or widget.pinned)

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
            c._dock_positioned=True;c._move_dock(QPoint(current.right()-c.width()-12,current.bottom()-c.height()-10))
        elif current!=self.previous['logical_client']:
            old=self.previous['logical_client'];delta=current.topLeft()-old.topLeft()
            for w in visible:
                if w is c:w.move(w.pos()+QPoint(current.right()-old.right(),current.bottom()-old.bottom()))
                else:w.move(w.pos()+delta)
        for w in visible:clamp_window(w,area)
        self.restore();self.previous=snapshot
        self.status='已绑定游戏窗口；玩家小窗随客户端移动。'
    def tick(self):
        if self.owner.closing:return
        self.apply(self.api.read(self.target()))
        label=getattr(self.companion,'binding_status',None)
        if label is not None:label.setText(self.status)
    def close(self):self.timer.stop();QApplication.instance().removeEventFilter(self);self.suspended=[];self.snapshot=None

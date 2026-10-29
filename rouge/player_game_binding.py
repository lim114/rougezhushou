"""Read-only native window identity/geometry and non-activating companion following."""
import ctypes,time
from contextlib import contextmanager
from PySide6.QtCore import QObject,QTimer,QPoint,QRect,Qt
from PySide6.QtWidgets import QApplication

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
            return {'target':dict(target),'key':(hwnd,pid),'physical_client':(x,y,w,h),'logical_client':rect,'cursor':cursor,'cursor_on_game':bool(active and hit==hwnd and x<=cursor[0]<x+w and y<=cursor[1]<y+h),'active':bool(active),'screen':screen}
        except (OSError,RuntimeError,ValueError,KeyError,TypeError,win32gui.error):return None

def clamp_window(widget,area):
    widget.move(max(area.left(),min(widget.x(),area.right()-widget.width()+1)),max(area.top(),min(widget.y(),area.bottom()-widget.height()+1)))

class GameWindowBinding(QObject):
    def __init__(self,companion,owner,api=None):
        super().__init__(companion);self.companion=companion;self.owner=owner;self.api=api or BindingApi()
        self.enabled=True;self.snapshot=None;self.previous=None;self.suspended=[];self.ever_bound=False
        self._targets=[];self._next_discovery=0.;self.status='尚未找到游戏；可先独立查阅。'
        self.timer=QTimer(self);self.timer.setInterval(250);self.timer.timeout.connect(self.tick);self.timer.start()
    def target(self):
        selected=getattr(self.owner.capture,'target',None)
        if selected is not None:return selected
        if time.monotonic()>=self._next_discovery:
            from .app import list_game_windows
            self._targets=list_game_windows();self._next_discovery=time.monotonic()+2
        return self._targets[0]if len(self._targets)==1 else None
    def surfaces(self):
        c=self.companion
        values=[c]+[getattr(c,name,None)for name in ('active_popup','inventory_popup','map_popup','overview_popup','settings_popup','recent_notes_popup','scene_popup','team_popup','exchange_popup','replay_popup','note_library')]
        values+=[getattr(self.owner,name,None)for name in ('player_notes','public_archive','public_statistics')]
        return list(dict.fromkeys(w for w in values if w is not None))
    def set_enabled(self,value):
        self.enabled=bool(value);self.previous=None
        if not value:self.restore();self.status='已暂停跟随游戏，窗口可自由移动。'
        else:self.tick()
    def restore(self):
        for w in self.suspended:
            try:w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);w.show()
            except RuntimeError:pass
        self.suspended=[]
    def apply(self,snapshot):
        self.snapshot=snapshot
        if not self.enabled:return
        if getattr(self.companion,'hidden_windows',None)is not None:return
        if snapshot is None or not snapshot['active']:
            if self.ever_bound:
                for w in self.surfaces():
                    if w.isVisible():
                        if w not in self.suspended:self.suspended.append(w)
                        w.hide()
                self.status='游戏不可见或绑定失效；玩家小窗已隐藏，记录保留。'
            self.previous=None;return
        self.ever_bound=True;current=snapshot['logical_client'];area=snapshot['screen'].availableGeometry();c=self.companion
        same=self.previous is not None and self.previous['key']==snapshot['key']
        visible=[w for w in self.surfaces()if w.isVisible()or w in self.suspended]
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
    def close(self):self.timer.stop();self.suspended=[];self.snapshot=None

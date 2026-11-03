"""Window-scoped Windows Graphics Capture. Never captures the whole desktop."""
import threading
import time
import win32gui
import win32process
import win32api
import win32con
import ctypes
from ctypes import wintypes
from .frame_buffer import FrameBuffer

def process_names():
    class Entry(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
                    ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', wintypes.LONG), ('dwFlags', wintypes.DWORD),
                    ('szExeFile', wintypes.WCHAR * 260)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise RuntimeError('无法读取进程列表。')
    names = {}
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(Entry)
        available = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while available:
            names[entry.th32ProcessID] = entry.szExeFile
            available = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return names

def list_game_windows():
    windows = []
    names = process_names()
    def visit(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if '明日方舟' not in title and 'Arknights' not in title:
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            executable = names.get(pid, '')
            if executable.lower() != 'arknights.exe':
                return
            windows.append({'hwnd': hwnd, 'pid': pid, 'title': title, 'executable': executable,
                            'minimized': bool(win32gui.IsIconic(hwnd))})
        except Exception:
            return
    win32gui.EnumWindows(visit, None)
    return windows

def frame_client_rect(hwnd,image):
    """Physical client bounds for this frame, with thread-local DPI awareness."""
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.SetThreadDpiAwarenessContext.argtypes=[ctypes.c_void_p]
    user.SetThreadDpiAwarenessContext.restype=ctypes.c_void_p
    previous=user.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))
    try:
        rect=wintypes.RECT()
        dwm=ctypes.WinDLL('dwmapi')
        dwm.DwmGetWindowAttribute.argtypes=[wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
        if dwm.DwmGetWindowAttribute(hwnd,9,ctypes.byref(rect),ctypes.sizeof(rect))!=0:return None
        h,w=image.shape[:2]
        if (rect.right-rect.left,rect.bottom-rect.top)!=(w,h):return None
        x,y=win32gui.ClientToScreen(hwnd,(0,0));_,_,cw,ch=win32gui.GetClientRect(hwnd)
        bounds=[x-rect.left,y-rect.top,x-rect.left+cw,y-rect.top+ch]
        if 0<=bounds[0]<bounds[2]<=w and 0<=bounds[1]<bounds[3]<=h:return bounds
    except (OSError,win32gui.error):return None
    finally:
        if previous:user.SetThreadDpiAwarenessContext(previous)

class GameCapture:
    def __init__(self):
        self._lock = threading.Lock()
        self.buffer = FrameBuffer()
        self._session = 0
        self._collecting = True
        self._control = None
        self._capture = None
        self.target = None
        self.closed = False

    def connect(self, target):
        self.close()
        known = {w['hwnd']: w for w in list_game_windows()}
        if target['hwnd'] not in known or known[target['hwnd']]['pid'] != target['pid']:
            raise RuntimeError('游戏窗口已关闭或变化，请刷新窗口列表。')
        from windows_capture import WindowsCapture
        self.target = known[target['hwnd']]
        self.closed = False
        session = self._session
        target = dict(self.target)
        self._capture = WindowsCapture(window_hwnd=self.target['hwnd'], cursor_capture=False,
                                       draw_border=True, minimum_update_interval=100)
        @self._capture.event
        def on_frame_arrived(frame, capture_control):
            with self._lock:
                if session != self._session or not self._collecting:return
                # Native mapped pixels expire after this callback. The buffer owns
                # retained candidates; expensive recognition runs on another worker.
                image=frame.frame_buffer[:,:,:3]
                client_rect=frame_client_rect(target['hwnd'],image)
                self.buffer.offer(image,time.time(),client_rect,target)
        @self._capture.event
        def on_closed():
            with self._lock:
                if session == self._session:self.closed = True
        self._control = self._capture.start_free_threaded()

    def set_collecting(self, enabled):
        with self._lock:
            if self._collecting != bool(enabled):
                self._collecting = bool(enabled)
                self.buffer.clear()

    def discard_pending(self):
        with self._lock:self.buffer.clear()

    def stats(self):
        return {**self.buffer.stats(),'capture_interval_ms':100,'collecting':self._collecting}

    def check_health(self):
        if self.target is None:
            raise RuntimeError('请先连接游戏窗口。')
        hwnd = self.target['hwnd']
        if self.closed or not win32gui.IsWindow(hwnd):
            raise RuntimeError('游戏窗口已关闭，请重新连接。')
        if win32gui.IsIconic(hwnd):
            raise RuntimeError('游戏窗口已最小化，已捕获页面仍可处理；还原后继续取新画面。')

    def next_frame(self, force=False):
        if force and not self.buffer.stats()['pending']:
            self.check_health()
            stats=self.buffer.stats()
            if not stats.get('latest_at') or time.time()-stats['latest_at']>=5:return None
        frame=self.buffer.take(force=force)
        if frame is not None:return frame
        self.check_health()
        return None

    def capture(self, timeout=4):
        """Compatibility one-shot: get a recent frame, without consuming the FIFO."""
        self.check_health()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.check_health()
            frame=self.buffer.latest()
            if frame is not None and time.time()-frame['captured_at']<5:return frame
            time.sleep(.05)
        raise TimeoutError('未收到新的窗口画面，请检查游戏是否正常显示。')

    def close(self):
        # Invalidate callbacks before stopping their native capture thread.
        with self._lock:
            self._session += 1
            self.buffer.clear()
        if self._control is not None:
            self._control.stop()
            self._control = None
        self._capture = None
        self.target = None

"""Owned hidden-window Windows hotkey; never hooks or sends input to the game."""
import ctypes
from ctypes import wintypes
import json
import re
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QSaveFile, QIODevice, Qt
from PySide6.QtWidgets import QApplication, QWidget

DEFAULT = 'Ctrl+Alt+Space'
WM_HOTKEY = 0x0312
MOD_NOREPEAT = 0x4000

def parse_shortcut(text, allow_single=False):
    parts = [p.strip() for p in text.split('+')]
    if not parts or any(not p for p in parts):
        raise ValueError('请填写一个按键组合，例如 Ctrl+Alt+Space。')
    names = {'ctrl': ('Ctrl', 2), 'alt': ('Alt', 1), 'shift': ('Shift', 4)}
    modifiers = 0
    for part in parts[:-1]:
        entry = names.get(part.lower())
        if entry is None or modifiers & entry[1]:
            raise ValueError('组合键只支持 Ctrl、Alt、Shift，且不能重复。')
        modifiers |= entry[1]
    key = parts[-1].upper()
    special = {'SPACE': ('Space', 0x20), 'TAB': ('Tab', 9)}
    if key in special:
        label, vk = special[key]
    elif re.fullmatch('[A-Z0-9]', key):
        label, vk = key, ord(key)
    elif re.fullmatch(r'F(?:[1-9]|10|11)', key):
        label, vk = key, 0x70 + int(key[1:]) - 1
    else:
        raise ValueError('支持字母、数字、Space、Tab、F1～F11；F12 和 Windows 组合键保留给系统。')
    if not modifiers and not allow_single:
        raise ValueError('单独按键会占用其他程序的这个键；确认下方说明后才能启用。')
    canonical = '+'.join([name for name, bit in [('Ctrl', 2), ('Alt', 1), ('Shift', 4)] if modifiers & bit] + [label])
    return canonical, modifiers, vk

def load_preferences(path):
    default = {'enabled': True, 'shortcut': DEFAULT, 'allow_single': False}
    try:
        data = json.loads(Path(path).read_text('utf8'))
        if not isinstance(data, dict) or type(data.get('enabled')) is not bool or type(data.get('allow_single')) is not bool:
            return default, '快捷键设置格式不正确，暂用默认值；原文件未改动。'
        canonical, _, _ = parse_shortcut(data['shortcut'], data['allow_single'])
        return {**default, **{k: data[k] for k in default}, 'shortcut': canonical}, ''
    except FileNotFoundError:
        return default, ''
    except (ValueError, TypeError, KeyError, OSError):
        return default, '快捷键设置无法读取，暂用默认值；原文件未改动。'

def save_preferences(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file = QSaveFile(str(path))
    if not file.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError('无法保存快捷键设置。')
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    if file.write(payload) != len(payload) or not file.commit():
        file.cancelWriting()
        raise OSError('快捷键设置未保存；请检查磁盘权限或空间。')

class WindowsApi:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.dll = ctypes.WinDLL('user32', use_last_error=True)
        self.dll.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
        self.dll.RegisterHotKey.restype = wintypes.BOOL
        self.dll.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        self.dll.UnregisterHotKey.restype = wintypes.BOOL
    def register(self, identity, modifiers, vk):
        return bool(self.dll.RegisterHotKey(self.hwnd, identity, modifiers | MOD_NOREPEAT, vk))
    def unregister(self, identity):
        return bool(self.dll.UnregisterHotKey(self.hwnd, identity))

class NativeReceiver(QWidget):
    def __init__(self, hotkey):
        super().__init__(None, Qt.WindowType.Tool)
        self.hotkey = hotkey
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        self.setWindowTitle('助手快捷键接收器（隐藏）')
    def nativeEvent(self, event_type, message):
        if bytes(event_type) == b'windows_generic_MSG':
            msg = wintypes.MSG.from_address(int(message))
            if self.hotkey.dispatch(msg.message, int(msg.wParam), int(msg.lParam)):
                return True, 0
        return super().nativeEvent(event_type, message)

class GlobalHotkey(QObject):
    triggered = Signal()
    _next_id = 0x5300
    def __init__(self, parent=None, api=None):
        super().__init__(parent)
        self.binding = None
        self.receiver = NativeReceiver(self)
        self.api = api if api is not None else WindowsApi(int(self.receiver.winId())) if sys.platform == 'win32' else None
        self.app = QApplication.instance()
        self.app.aboutToQuit.connect(self.close)

    def configure(self, enabled, shortcut, allow_single=False):
        canonical, modifiers, vk = parse_shortcut(shortcut, allow_single)
        if not enabled:
            if not self.release():
                return False, '旧快捷键未能释放，仍保持原设置。'
            return True, '快捷键已关闭，可继续点击工具条。'
        if self.binding and self.binding[1:] == (modifiers, vk):
            return True, '当前快捷键：' + canonical + '，按一次收起，再按一次恢复。'
        if self.api is None:
            return False, '当前系统不支持全局快捷键，请点击工具条。'
        identity = GlobalHotkey._next_id
        GlobalHotkey._next_id += 1
        if identity > 0xBFFF:
            return False, '本次程序快捷键变更次数已达上限，请重新打开助手。'
        if not self.api.register(identity, modifiers, vk):
            return False, '无法启用 ' + canonical + '：可能已被其他程序占用。请换一个组合；原快捷键保持。'
        if not self.release():
            self.api.unregister(identity)
            return False, '旧快捷键未能释放，仍保持原设置。'
        self.binding = (identity, modifiers, vk)
        return True, '当前快捷键：' + canonical + '，按一次收起，再按一次恢复。'

    def dispatch(self, message, identity, packed_keys):
        if not self.binding or message != WM_HOTKEY or identity != self.binding[0]:
            return False
        if packed_keys & 0xFFFF != self.binding[1] or (packed_keys >> 16) & 0xFFFF != self.binding[2]:
            return False
        self.triggered.emit()
        return True

    def release(self):
        if self.binding is not None:
            if not self.api.unregister(self.binding[0]):
                return False
            self.binding = None
        return True

    def close(self):
        self.release()
        self.receiver.close()

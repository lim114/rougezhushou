"""One local overlay preference, separate from chat and shortcut credentials."""
import json
from pathlib import Path
from PySide6.QtCore import QSaveFile,QIODevice


class OverlayPreferences:
    def __init__(self,path):
        self.path=Path(path)if path is not None else None
        self.data={};self.enabled=True;self.warning='';self.readable=True
        if self.path is None:return
        try:
            data=json.loads(self.path.read_text('utf8'))
            if not isinstance(data,dict)or type(data.get('enabled',True))is not bool:
                raise ValueError('Invalid overlay preference')
            self.data=data;self.enabled=data.get('enabled',True)
        except FileNotFoundError:pass
        except(OSError,ValueError):
            self.enabled=False;self.readable=False
            self.warning='地图叠加设置无法读取，原文件保留；本次选择不会覆盖它。'

    def save(self,value):
        self.enabled=value
        if self.path is None:return ''
        if not self.readable:return self.warning
        data={**self.data,'enabled':value}
        file=QSaveFile(str(self.path));raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8')
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            if not file.open(QIODevice.OpenModeFlag.WriteOnly):raise OSError(file.errorString())
        except OSError:return '地图叠加设置未保存，请检查文件或文件夹权限。'
        if file.write(raw)!=len(raw)or not file.commit():
            file.cancelWriting();return '地图叠加设置未保存，原设置保留。'
        self.data=data
        return ''

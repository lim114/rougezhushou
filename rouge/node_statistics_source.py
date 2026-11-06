"""One read-only public source shared by statistics, map highlights and cards."""
from pathlib import Path
from copy import deepcopy
import json,os
from PySide6.QtCore import QObject,Signal
from . import public_node_statistics as model


class NodeStatisticsSource(QObject):
    changed=Signal()

    def __init__(self,cache,parent=None):
        super().__init__(parent);self.cache=Path(cache);self.data=None;self.index=model.FrequencyIndex()
        try:
            data=model.load(self.cache if self.cache.is_file()else model.DEFAULT)
        except(OSError,ValueError,KeyError,TypeError):return
        self.index=model.FrequencyIndex.from_validated(data);self.data=data

    def accept(self,data):
        model.validate(data)
        index=model.FrequencyIndex.from_validated(data)
        self.cache.parent.mkdir(parents=True,exist_ok=True)
        temp=self.cache.with_suffix('.tmp')
        temp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8');os.replace(temp,self.cache)
        changed=index.identity!=self.index.identity
        self.data=deepcopy(data);self.index=index
        if changed:self.changed.emit()
        return changed

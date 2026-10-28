"""Known tactical-tool possession and fixed effects; no use/activation action."""
from pathlib import Path
from . import expansion_reference
from .record_flags import active_record

def tool_rows(state,query='',held_only=True):
    packet=expansion_reference.packet()
    if packet is None:return None
    result=[];query=query.strip().casefold()
    held={key for key,row in state.get('tactical_tools',{}).items()if active_record(row,'held')}
    for identity,item in packet['current']['details']['items'].items():
        if item.get('type')!='ACTIVE_TOOL':continue
        usage=expansion_reference._plain(item.get('usage'))
        if held_only and identity not in held:continue
        if query not in(item['name']+' '+usage).casefold():continue
        result.append({'id':identity,'name':item['name'],'icon':item.get('iconId'),
                       'usage':usage,'held':identity in held})
    return result

from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QCheckBox,QListWidget,QListWidgetItem,QPlainTextEdit

class ToolsPanel(QWidget):
    def __init__(self,run,parent=None):
        super().__init__(parent);self.run=run;self.rows={};self.key=None;body=QVBoxLayout(self)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('查找战术道具或效果');bar.addWidget(self.search)
        self.held=QCheckBox('只看本局已确认持有');self.held.setChecked(True);bar.addWidget(self.held);body.addLayout(bar)
        self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.entries=QListWidget();self.entries.setIconSize(QSize(42,42));body.addWidget(self.entries,1)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1)
        self.search.textChanged.connect(self.refresh);self.held.toggled.connect(self.refresh);self.entries.currentItemChanged.connect(self.selected);self.refresh()
    def refresh(self,*_):
        rows=tool_rows(self.run.state,self.search.text(),self.held.isChecked());key=repr(rows)
        self.notice.setText('道具资料暂时不可用，旧列表已清除；本局持有记录没有被重置。'if rows is None else f'显示{len(rows)}件战术道具。未列出不表示没有；资料不证明当前可用或本次已经生效。国服10月16日固定基准，当前完整覆盖仍待核验。')
        if key==self.key:return
        self.key=key;current=self.entries.currentItem();old=current.data(Qt.ItemDataRole.UserRole)if current else None;offset=self.entries.verticalScrollBar().value();self.rows={r['id']:r for r in rows or[]}
        self.entries.blockSignals(True);self.entries.clear()
        for row in rows or[]:
            path=Path(__file__).with_name('data')/'relic-icons'/((row['icon']or'')+'.png')
            item=QListWidgetItem(QIcon(str(path))if path.is_file()else QIcon(),row['name']+(' · 本局已确认'if row['held']else' · 资料')+(''if path.is_file()else' · 图片待补'))
            item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==old:self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.selected()
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        text=(row['name']+'\n\n资料效果\n'+row['usage']+'\n\n仅提供持有记录与资料查阅，不自动使用、不计算实际战斗触发，也不改变本局。')if row else'选择一件战术道具阅读固定说明。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)

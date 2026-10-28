"""Fixed part catalogue and an independently observed box count; never fake members."""
from pathlib import Path
from . import expansion_reference as source

def part_rows(query='',kind=None):
    packet=source.packet()
    if packet is None:return None
    scrap=packet['current']['modules']['scrap'];result=[];q=query.strip().casefold()
    for row in source.rows('scrap',changes_only=False,reference=packet):
        identity=row['id'];item=row['value']['item']or{};group=scrap['scrapItemToType'].get(identity);named=scrap['scrapTypeData'].get(group,{})
        usage=source._plain(item.get('usage'))
        if kind is not None and group!=kind:continue
        if q and q not in(row['name']+' '+usage).casefold():continue
        result.append({'id':identity,'name':row['name'],'kind':group,'kind_name':named.get('typeName')or'类别未确认','kind_description':source._plain(named.get('typeDesc')),'usage':usage,'icon':item.get('iconId'),'rarity':item.get('rarity'),'can_sacrifice':item.get('canSacrifice')})
    return result

def box_status(state):
    record=state.get('resources',{}).get('parts_count');value=record.get('value')if isinstance(record,dict)else None
    if type(value)is not int or value<0:return '本局零件数量尚未读到；具体成员也未完整读取。以下为固定资料目录，不是库存。'
    return f'最近读到本局零件{value}件；具体成员与剩余使用次数未完整读取。以下为资料目录，不把数量当作成员名单。'

from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton
class PartsPanel(QWidget):
    def __init__(self,run,parent=None):
        super().__init__(parent);self.run=run;self.rows={};self.key=None;body=QVBoxLayout(self);self.notice=QLabel();self.notice.setWordWrap(True);body.addWidget(self.notice)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('搜索零件名称或效果');bar.addWidget(self.search,1);self.kind=QComboBox();self.kind.addItem('全部零件类别',None)
        for key,label in [('MOVE','加工品'),('GOODS','自然物'),('PASSIVE','概念体')]:self.kind.addItem(label,key)
        bar.addWidget(self.kind);body.addLayout(bar);self.entries=QListWidget();self.entries.setIconSize(QSize(45,45));body.addWidget(self.entries,1)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1);self.refresh_button=QPushButton('重新核对本机零件资料');body.addWidget(self.refresh_button)
        self.search.textChanged.connect(self.refresh);self.kind.currentIndexChanged.connect(self.refresh);self.entries.currentItemChanged.connect(self.selected);self.refresh_button.clicked.connect(self.refresh);self.refresh()
    def refresh(self,*_):
        self.notice.setText(box_status(self.run.state)+'资料基准：国服2026年10月16日；当前DLC完整覆盖未核验。')
        rows=part_rows(self.search.text(),self.kind.currentData());key=repr(rows)
        if key==self.key:return
        self.key=key;old=self.entries.currentItem();identity=old.data(Qt.ItemDataRole.UserRole)if old else None;offset=self.entries.verticalScrollBar().value();self.rows={r['id']:r for r in rows or[]};self.entries.blockSignals(True);self.entries.clear()
        for row in rows or[]:
            path=Path(__file__).with_name('data')/'part-icons'/((row['icon']or'')+'.png');item=QListWidgetItem(QIcon(str(path))if path.is_file()else QIcon(),row['name']+' · '+row['kind_name']+(''if path.is_file()else' · 暂无图片'));item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==identity:self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset);self.entries.blockSignals(False);self.selected()
        if rows is None:self.notice.setText('零件资料暂不可用，旧目录与效果已清除；本局记录没有被重置。')
    def selected(self,*_):
        item=self.entries.currentItem();row=self.rows.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        text=row['name']+' · '+row['kind_name']+'\n'+row['kind_description']+'\n\n效果资料\n'+row['usage']+'\n\n本局是否持有、装载、已经触发或剩余次数未确认；资料效果不是已生效证明。'if row else'选择一件零件阅读效果；未读具体成员时不展示假定库存。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)

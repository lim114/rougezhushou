"""Player-facing current offer catalogue and separate documented quantities."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,QTabWidget,QPushButton,QSizePolicy
from . import current_exchange_reference as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
from .reference_copy import mechanism_copy
from .flow_layout import FlowLayout


class CurrentExchangePanel(QWidget):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.result=None;self.item_id=None;self.group_id=None
        layout=QVBoxLayout(self);notice=QLabel('回滚文明 · 查看可交出的藏品、交换奖励与消耗。');notice.setWordWrap(True);layout.addWidget(notice)
        self.refresh_button=QPushButton('刷新资料');self.refresh_button.setAutoDefault(False);layout.addWidget(self.refresh_button);self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        item_page=QWidget();body=QVBoxLayout(item_page);bar=FlowLayout();self.offer=QComboBox();self.rarity=QComboBox();self.change=QComboBox();self.search=QLineEdit();self.search.setPlaceholderText('按收藏品中文名查找')
        for text,value in(('全部提供物',None),('可交出',True),('不可交出',False)):self.offer.addItem(text,value)
        self.rarity.addItem('全部稀有度',None)
        for value,text in model.RARITIES.items():self.rarity.addItem(text,value)
        for text,value in(('本版本全部',None),('本次新增','added'),('已有改动','changed'),('未改动','unchanged')):self.change.addItem(text,value)
        for widget,name in((self.offer,'收藏品交出分类'),(self.rarity,'交换收藏品稀有度'),(self.change,'交换资料的更新范围'),(self.search,'交换收藏品中文检索')):widget.setAccessibleName(name);bar.addWidget(widget)
        body.addLayout(bar);self.count=QLabel();body.addWidget(self.count);self.items=QListWidget();self.items.setMaximumHeight(155);self.items.setAccessibleName('当前交换提供物');body.addWidget(self.items)
        self.item_tabs=QTabWidget();self.item_player=QPlainTextEdit();self.item_technical=QPlainTextEdit();self.item_tabs.addTab(self.item_player,'能否交出与作用');self.item_tabs.addTab(self.item_technical,'原始物品与来源');body.addWidget(self.item_tabs,1);self.tabs.addTab(item_page,'收藏品能否交出')
        doc_page=QWidget();body=QVBoxLayout(doc_page);self.groups=QListWidget();self.groups.setMaximumHeight(155);self.groups.setAccessibleName('交换条文与明确数量');body.addWidget(self.groups);self.doc_tabs=QTabWidget();self.doc_player=QPlainTextEdit();self.doc_technical=QPlainTextEdit();self.doc_tabs.addTab(self.doc_player,'选项与奖励');self.doc_tabs.addTab(self.doc_technical,'原文与资料说明');body.addWidget(self.doc_tabs,1);self.tabs.addTab(doc_page,'交换条文与奖励')
        for tabs in(self.tabs,self.item_tabs,self.doc_tabs):tabs.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored)
        for reader in(self.item_player,self.item_technical,self.doc_player,self.doc_technical):reader.setReadOnly(True)
        for widget in(self.offer,self.rarity,self.change):widget.currentIndexChanged.connect(self._filter_changed)
        self.search.textChanged.connect(self._filter_changed);self.items.currentItemChanged.connect(self._item_changed);self.groups.currentItemChanged.connect(self._group_changed);self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()
        if target and self.result:
            if target['tab']=='document':self.tabs.setCurrentIndex(1)
            self._select(self.items,target.get('item_id'));self._select(self.groups,target.get('group_id'))

    @staticmethod
    def _select(widget,key):
        if key is None:return
        for i in range(widget.count()):
            if widget.item(i).data(Qt.ItemDataRole.UserRole)==key:widget.setCurrentRow(i);return

    def clear_reference(self):
        self.result=None;self.item_id=None;self.group_id=None
        for widget in(self.items,self.groups):
            block=widget.blockSignals(True);widget.clear();widget.blockSignals(block)
        self.count.setText(model.UNAVAILABLE)
        for widget in(self.item_player,self.doc_player):replace_text(widget,model.UNAVAILABLE,preserve=False)
        for widget in(self.item_technical,self.doc_technical):replace_text(widget,'',preserve=False)
        for tabs in(self.tabs,self.item_tabs,self.doc_tabs):tabs.setCurrentIndex(0)

    def refresh_reference(self,*_):
        fresh=model.packet()
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity'];selected=self.group_id if keep else None;self.result=fresh
        block=self.groups.blockSignals(True);self.groups.clear()
        for row in fresh['data']['document_groups']:
            item=QListWidgetItem(row['title']+' · '+model.version._plain(row['description']));item.setData(Qt.ItemDataRole.UserRole,row['id']);self.groups.addItem(item)
        self._select(self.groups,selected);self.groups.blockSignals(block);self._group_changed(self.groups.currentItem(),preserve=keep);self._populate(preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        return True

    def _filter_changed(self,*_):self._populate(preserve=True)

    def _populate(self,*,preserve):
        if self.result is None:return
        selected=self.item_id if preserve else None;rows=model.catalogue_rows(self.result,can_offer=self.offer.currentData(),rarity=self.rarity.currentData(),change=self.change.currentData(),query=self.search.text())
        block=self.items.blockSignals(True);self.items.clear()
        for row in rows:
            item=QListWidgetItem(row['name']+' · '+('可交出'if row['can_offer']else'不可交出')+' · '+model.RARITIES[row['rarity']]);item.setData(Qt.ItemDataRole.UserRole,row['id']);self.items.addItem(item)
        self._select(self.items,selected);self.items.blockSignals(block);self.count.setText('当前筛选'+str(len(rows))+'件 · 目录共'+str(len(self.result['data']['catalogue']))+'件');self._item_changed(self.items.currentItem(),preserve=preserve)

    def _item_changed(self,item,*_,preserve=False):
        key=item.data(Qt.ItemDataRole.UserRole)if item else None;keep=preserve and key==self.item_id;self.item_id=key
        if self.result is None:return
        row=next((r for r in self.result['data']['catalogue']if r['id']==key),None)
        text,notes=mechanism_copy(model.item_text(self.result,key,prepared_row=row),'',extra_detail_headings=('【范围与未知】',))
        replace_text(self.item_player,text,preserve=keep);replace_text(self.item_technical,_technical_json({'资料说明':notes,'selected_item':row,'scope':self.result['data']['scope'],'source_identity':self.result['source_identity'],'source':self.result['data']['source']})if row else'',preserve=keep)
        if not keep:self.item_tabs.setCurrentIndex(0)

    def _group_changed(self,item,*_,preserve=False):
        key=item.data(Qt.ItemDataRole.UserRole)if item else None;keep=preserve and key==self.group_id;self.group_id=key
        if self.result is None:return
        row=next((r for r in self.result['data']['document_groups']if r['id']==key),None)
        originals={k:self.result['data']['original_choices'][k]for k in row['primary_candidate_ids']}if row else{}
        text,notes=mechanism_copy(model.document_text(self.result,key,prepared_row=row),'',extra_detail_headings=('【相同文案仍需分清】','【本局与奖励仍未知】'))
        replace_text(self.doc_player,text,preserve=keep);replace_text(self.doc_technical,_technical_json({'资料说明':notes,'document_group':row,'complete_candidates':originals,'source_identity':self.result['source_identity'],'source':self.result['data']['source']})if row else'',preserve=keep)
        if not keep:self.doc_tabs.setCurrentIndex(0)


class CurrentExchangeDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('当前回滚文明 · 提供物与奖励条文');self.resize(1050,810);layout=QVBoxLayout(self);self.panel=CurrentExchangePanel(target,self);layout.addWidget(self.panel)

"""Read-only named source directory with independently owned original readers."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
                              QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,
                              QTabWidget,QPushButton,QSplitter)
from . import current_non_event_origins as model
from .ui_state import replace_text


class CurrentNonEventOriginsPanel(QWidget):
    def __init__(self,target=None,parent=None):
        super().__init__(parent)
        self.result=self.source_identity=self.identity=self.source_request=self.original_dialog=None
        layout=QVBoxLayout(self); notice=QLabel(model.NOTICE);notice.setWordWrap(True);layout.addWidget(notice)
        filters=QHBoxLayout();self.kind=QComboBox();self.kind.addItem('总览：全部来源',None)
        for key,label in model.KINDS:self.kind.addItem(label,key)
        self.timing=QComboBox();self.timing.addItem('总览：全部时点依据',None)
        for key,label in model.TIMES:self.timing.addItem(label,key)
        self.kind.setAccessibleName('具名物品非事件取得来源种类')
        self.timing.setAccessibleName('有证据的取得时点，不从变量名称猜时刻')
        self.search=QLineEdit();self.search.setPlaceholderText('按物品或准确来源的中文名称查询')
        self.refresh_button=QPushButton('重新核对资料')
        for control in(self.kind,self.timing,self.search,self.refresh_button):filters.addWidget(control)
        layout.addLayout(filters);self.count=QLabel();self.count.setWordWrap(True);layout.addWidget(self.count)
        splitter=QSplitter();self.entries=QListWidget();self.entries.setAccessibleName('非事件取得资料：每个准确来源单独列出')
        splitter.addWidget(self.entries);self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for reader in(self.player,self.technical):reader.setReadOnly(True)
        self.tabs.addTab(self.player,'能获得什么、来源与时点');self.tabs.addTab(self.technical,'完整原值与来源')
        splitter.addWidget(self.tabs);splitter.setSizes([340,790]);layout.addWidget(splitter,1)
        actions=QHBoxLayout();self.source_button=QPushButton('查看准确来源原文');self.item_button=QPushButton('查看对应物品原文')
        for button in(self.source_button,self.item_button):button.hide();actions.addWidget(button)
        layout.addLayout(actions)
        self.kind.currentIndexChanged.connect(self._filter_changed);self.timing.currentIndexChanged.connect(self._filter_changed)
        self.search.textChanged.connect(self._filter_changed);self.refresh_button.clicked.connect(self.refresh_reference)
        self.entries.currentItemChanged.connect(self._selected)
        self.source_button.clicked.connect(lambda:self.open_original('source'));self.item_button.clicked.connect(lambda:self.open_original('item'))
        self.refresh_reference()
        if target is not None:self.open_target(target)

    def _filters(self):return {'kind':self.kind.currentData(),'timing':self.timing.currentData(),'query':self.search.text()}

    def _fresh(self,identity=None):
        fresh=model.reference(identity,**self._filters())
        return {**fresh,'source_request':deepcopy(self.source_request)} if fresh else None

    def close_children(self):
        if self.original_dialog is not None:
            panel=getattr(self.original_dialog,'panel',None)
            if panel is not None and hasattr(panel,'close_children'):panel.close_children()
            self.original_dialog.close()
        self.original_dialog=None

    def _unavailable(self):
        self.close_children();self.result=self.source_identity=self.identity=self.source_request=None
        blocked=self.entries.blockSignals(True)
        try:self.entries.clear()
        finally:self.entries.blockSignals(blocked)
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False)
        for button in(self.source_button,self.item_button):button.hide();button.setEnabled(False)
        self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self,*_):
        self.source_request=None;self._populate(preserve=False)

    def _populate(self,*,preserve):
        fresh=self._fresh()
        if fresh is None:self._unavailable();return False
        same=self.source_identity==fresh['source_identity'];identity=self.identity if same and preserve else None
        if not same:self.close_children();self.source_request=None;fresh=self._fresh()
        self.source_identity=fresh['source_identity'];blocked=self.entries.blockSignals(True)
        try:
            self.entries.clear()
            for row in fresh['rows']:
                item=QListWidgetItem(row['item_name']+' ← '+row['source_name']);item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
                if row['id']==identity:self.entries.setCurrentItem(item)
        finally:self.entries.blockSignals(blocked)
        self.count.setText('当前筛选列出'+str(len(fresh['rows']))+'条准确来源；不同来源不相加，不是本局物品数量。')
        current=self.entries.currentItem()
        if current is None:
            keep=same and preserve and self.identity is None;self.identity=None
            if not keep:self.close_children();self.source_request=None;fresh=self._fresh()
            self._show(fresh,preserve=keep)
            if keep:self._refresh_child()
        else:self._selected(current,preserve=same and preserve)
        return True

    def refresh_reference(self):return self._populate(preserve=True)

    def _show(self,fresh,*,preserve):
        self.result=deepcopy(fresh);replace_text(self.player,model.player_text(fresh),preserve=preserve)
        replace_text(self.technical,json.dumps(fresh,ensure_ascii=False,indent=2),preserve=preserve)
        selected=fresh['selected']
        for button in(self.source_button,self.item_button):button.setVisible(selected is not None);button.setEnabled(selected is not None)
        if selected:
            self.source_button.setText('查看'+selected['source_name']+'的准确原文')
            self.item_button.setText('查看'+selected['item_name']+('说明与留存规则' if selected['item_category']=='recruit_tickets' else '完整用途'))
        if not preserve:self.tabs.setCurrentIndex(0)

    def _selected(self,item,*_,preserve=False):
        identity=item.data(Qt.ItemDataRole.UserRole) if item else None
        fresh=self._fresh(identity)
        if fresh is None or fresh['source_identity']!=self.source_identity:self._unavailable();return
        keep=preserve and identity==self.identity
        if not keep:self.close_children()
        if not keep and self.identity is not None:self.source_request=None;fresh=self._fresh(identity)
        self.identity=identity;self._show(fresh,preserve=keep)
        if keep:self._refresh_child()

    def _refresh_child(self):
        if self.original_dialog is not None and self.original_dialog.isVisible():self.original_dialog.panel.refresh_reference()

    def open_target(self,target):
        if type(target)is not dict or set(target)!={'identity','source_request'}:return False
        request=target['source_request']
        if type(request)is not dict or set(request)!={'category','key'}:return False
        fresh=model.locate(request['category'],request['key'])
        if fresh!=target:return False
        for index in range(self.entries.count()):
            item=self.entries.item(index)
            if item.data(Qt.ItemDataRole.UserRole)==target['identity']:
                self.source_request=deepcopy(request);self.identity=None
                blocked=self.entries.blockSignals(True)
                try:self.entries.setCurrentItem(item)
                finally:self.entries.blockSignals(blocked)
                self._selected(item);return True
        return False

    def open_original(self,side):
        if self.result is None or self.identity is None:return False
        fresh=self._fresh(self.identity)
        if fresh is None or fresh!=self.result:self._unavailable();return False
        link=model.destination(self.identity,side)
        if link is None:return False
        self.close_children()
        if link['category']=='recruit_tickets':
            from .current_recruit_tickets_view import CurrentRecruitTicketsDialog
            child=CurrentRecruitTicketsDialog(self)
        else:
            from .expansion_view import ExpansionUpdatePanel
            child=QDialog(self);child.setWindowTitle(link['name']+' · 准确原始资料');child.resize(1080,800)
            child.panel=ExpansionUpdatePanel(child,categories=(link['category'],),full_catalog=True)
            QVBoxLayout(child).addWidget(child.panel)
            child.finished.connect(lambda *_:child.panel.close_children())
        for index in range(child.panel.entries.count()):
            item=child.panel.entries.item(index)
            if item.data(Qt.ItemDataRole.UserRole)==link['key']:
                child.panel.entries.setCurrentItem(item);break
        else:child.close();return False
        self.original_dialog=child
        if child.panel.result is None:self.close_children();return False
        child.show();return True

    def closeEvent(self,event):self.close_children();super().closeEvent(event)


class CurrentNonEventOriginsDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('具名物品 · 分队与收藏品的取得来源');self.resize(1150,830)
        self.panel=CurrentNonEventOriginsPanel(target,self);QVBoxLayout(self).addWidget(self.panel)

    def closeEvent(self,event):self.panel.close_children();super().closeEvent(event)

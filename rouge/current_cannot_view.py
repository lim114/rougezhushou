"""Manual documentary reading, exact current preview links, no game actions."""
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QPlainTextEdit, QPushButton,
                               QTabWidget, QVBoxLayout, QWidget)
from . import current_cannot_reference as model
from .ui_state import replace_text


class CurrentCannotPanel(QWidget):
    def __init__(self, target=None, parent=None):
        super().__init__(parent)
        self.target = target if target is not None else {'kind':'shop','stage_id':None,'key':None}
        self.result = None
        self.battle_dialog = None
        layout = QVBoxLayout(self)
        notice = QLabel(model.NOTICE); notice.setWordWrap(True); layout.addWidget(notice)
        controls = QHBoxLayout()
        self.topic = QComboBox(); self.topic.setAccessibleName('坎诺特机制阅读分支')
        self.topic.addItem('总览（全部条件与差异）', None)
        for key, title in model.TOPICS:self.topic.addItem(title, key)
        controls.addWidget(self.topic, 1)
        self.refresh_button = QPushButton('重新核对资料'); controls.addWidget(self.refresh_button)
        layout.addLayout(controls)
        self.floor_row = QWidget(); floor_layout = QHBoxLayout(self.floor_row); floor_layout.setContentsMargins(0,0,0,0)
        floor_layout.addWidget(QLabel('可选，仅本页：按文献中的主层条件查找作战'))
        self.floor = QComboBox(); self.floor.addItem('层数未知，保留两份条件候选', None)
        for n in range(1,7):self.floor.addItem('第'+str(n)+'层', n)
        floor_layout.addWidget(self.floor,1); layout.addWidget(self.floor_row)
        self.entries_row = QWidget(); entry_layout = QHBoxLayout(self.entries_row); entry_layout.setContentsMargins(0,0,0,0)
        entry_layout.addWidget(QLabel('本关精确资料'))
        self.entries = QComboBox(); self.entries.setAccessibleName('当前关卡的坎诺特或保险柜引用')
        entry_layout.addWidget(self.entries,1); layout.addWidget(self.entries_row)
        self.tabs = QTabWidget(); self.player = QPlainTextEdit(); self.technical = QPlainTextEdit()
        for reader,title in ((self.player,'机制、领取条件与限制'),(self.technical,'完整来源与原值')):
            reader.setReadOnly(True); self.tabs.addTab(reader,title)
        layout.addWidget(self.tabs,1)
        layout.addWidget(QLabel('关联资料（打开前会再次核对对应关系）'))
        self.related = QListWidget(); self.related.setAccessibleName('坎诺特与保险柜的准确关联入口'); self.related.setMaximumHeight(160); layout.addWidget(self.related)
        self.open_button = QPushButton('打开选中的关联资料'); self.open_button.setEnabled(False); layout.addWidget(self.open_button)
        self.topic.currentIndexChanged.connect(self._topic_changed)
        self.floor.currentIndexChanged.connect(self._floor_changed)
        self.entries.currentIndexChanged.connect(self._entry_changed)
        self.related.currentItemChanged.connect(self._link_changed)
        self.open_button.clicked.connect(lambda:self.open_link())
        self.refresh_button.clicked.connect(self.refresh_reference)
        self.refresh_reference()

    def _close_battle(self):
        if self.battle_dialog is not None:
            self.battle_dialog.close(); self.battle_dialog = None

    def clear_reference(self):
        self._close_battle(); self.result = None
        self.target = {'kind':'shop','stage_id':None,'key':None}
        for widget in (self.floor,self.topic):
            blocked=widget.blockSignals(True)
            try:widget.setCurrentIndex(0)
            finally:widget.blockSignals(blocked)
        previous = self.entries.blockSignals(True)
        try:self.entries.clear()
        finally:self.entries.blockSignals(previous)
        self.related.clear(); self.open_button.setEnabled(False)
        self.entries_row.hide(); self.floor_row.hide()
        replace_text(self.player,model.UNAVAILABLE,preserve=False); replace_text(self.technical,'',preserve=False)
        self.tabs.setCurrentIndex(0)

    def refresh_reference(self,*_):
        floor = self.floor.currentData() if type(self.target) is dict and self.target.get('kind') == 'shop' else None
        fresh = model.reference(self.target,floor=floor)
        if fresh is None:self.clear_reference();return False
        same = self.result is not None and model.same(self.result['source_identity'],fresh['source_identity']) and self.result['target'] == fresh['target']
        if not same:self._close_battle();self.tabs.setCurrentIndex(0)
        self.result = fresh
        self.floor_row.setVisible(fresh['target']['kind'] == 'shop')
        self.entries_row.setVisible(fresh['stage_id'] is not None)
        previous = self.entries.blockSignals(True)
        try:
            self.entries.clear()
            if fresh['stage_id'] is not None:
                stage = fresh['stages'][0];sid = stage['id']
                choices = [('本关总览',{'kind':'stage','stage_id':sid,'key':None}),
                           ('坎诺特 · 精确敌人引用',{'kind':'enemy','stage_id':sid,'key':stage['boss']['key']})]
                choices += [(v['label'],{'kind':'vault','stage_id':sid,'key':v['key']}) for v in stage['vaults']]
                for label,target in choices:self.entries.addItem(label,target)
                for index in range(self.entries.count()):
                    if self.entries.itemData(index) == fresh['target']:self.entries.setCurrentIndex(index);break
        finally:self.entries.blockSignals(previous)
        self._render(preserve=same)
        if same and self.battle_dialog is not None and self.battle_dialog.isVisible():
            self.battle_dialog.panel.refresh_reference()
        return True

    def _render(self,*,preserve):
        if self.result is None:return
        selected = self.related.currentItem().data(Qt.ItemDataRole.UserRole) if preserve and self.related.currentItem() else None
        scroll = self.related.verticalScrollBar().value() if preserve else 0
        replace_text(self.player,model.player_text(self.result,self.topic.currentData()),preserve=preserve)
        # Full DOM is preserved for audit, including hidden tooltips; default player text avoids raw keys and white values.
        technical = {'target':self.result['target'],'source_identity':self.result['source_identity'],
                     'selected':self.result['selected'],'stages':self.result['stages'],
                     'originals':self.result['data']['originals'],'documents':self.result['documents'],
                     'actual_free_slots':None,'actual_goods':None,'actual_gold_lost':None}
        replace_text(self.technical,json.dumps(technical,ensure_ascii=False,indent=2),preserve=preserve)
        self.related.clear()
        for link in model.links(self.result):
            item=QListWidgetItem(link['label']);item.setData(Qt.ItemDataRole.UserRole,link['target']);self.related.addItem(item)
            if link['target'] == selected:self.related.setCurrentItem(item)
        self.related.verticalScrollBar().setValue(scroll);self._link_changed()

    def _topic_changed(self,*_):
        if self.result is None:return
        fresh = model.reference(self.target,floor=self.result['floor_declared'])
        if fresh is None or not model.same(fresh['source_identity'],self.result['source_identity']):self.clear_reference();return
        self.result=fresh;self._render(preserve=False)

    def _floor_changed(self,*_):
        if type(self.target) is dict and self.target.get('kind')=='shop':
            self._close_battle();self.result=None;self.refresh_reference()

    def _entry_changed(self,*_):
        target=self.entries.currentData()
        if target is None or target == self.target:return
        self.navigate(target)

    def navigate(self,target):
        fresh=model.reference(target)
        if fresh is None:return False
        self._close_battle();self.target=target;self.result=None
        if target['kind']=='shop':
            previous=self.floor.blockSignals(True)
            try:self.floor.setCurrentIndex(0)
            finally:self.floor.blockSignals(previous)
        return self.refresh_reference()

    def _link_changed(self,*_):
        item=self.related.currentItem()
        self.open_button.setEnabled(self.result is not None and item is not None and any(model.same(item.data(Qt.ItemDataRole.UserRole),r['target'])for r in model.links(self.result)))

    def open_link(self,target=None):
        if self.result is None:return False
        if target is None:
            item=self.related.currentItem();target=item.data(Qt.ItemDataRole.UserRole)if item else None
        qualified=model.qualify_link(self.result,target)
        if qualified is None:
            if model.reference(self.target,floor=self.result['floor_declared']) is None:self.clear_reference()
            return False
        if qualified['kind']!='battle':return self.navigate(qualified)
        from .current_battle_view import CurrentBattleDialog
        self._close_battle();dialog=CurrentBattleDialog(qualified['stage_id'],self)
        if dialog.panel.result is None:dialog.close();return False
        if qualified['enemy_key'] is not None:
            if not dialog.panel.enemy_choices.select_value(qualified['enemy_key'],emit=True):dialog.close();return False
            dialog.panel.tabs.setCurrentIndex(1)
        elif qualified['reward_id'] is not None:
            if not dialog.panel.rewards.choices.select_value(qualified['reward_id'],emit=True):dialog.close();return False
            dialog.panel.tabs.setCurrentIndex(dialog.panel.tabs.indexOf(dialog.panel.rewards))
        if model.qualify_link(self.result,qualified) is None:dialog.close();self.clear_reference();return False
        self.battle_dialog=dialog;dialog.show();return True

    def closeEvent(self,event):
        self.clear_reference();super().closeEvent(event)


class CurrentCannotDialog(QDialog):
    def __init__(self,target=None,parent=None):
        super().__init__(parent);self.setWindowTitle('坎诺特与保险柜 · 商店挑战的条件与后果');self.resize(1080,870)
        layout=QVBoxLayout(self);self.panel=CurrentCannotPanel(target,self);layout.addWidget(self.panel)

    def closeEvent(self,event):
        self.panel.clear_reference();super().closeEvent(event)

"""Named event-to-battle references and reverse lookup with owned dialogs."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QHBoxLayout,QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QTabWidget,QLabel
from . import current_event_battles as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text

class CurrentEventBattlesPanel(QWidget):
    def __init__(self,event_id=None,choice_id=None,stage_id=None,parent=None):
        super().__init__(parent);self.event_id=event_id;self.stage_id=stage_id;self.result=None;self.choice_id=None;self.battle_dialog=None
        layout=QVBoxLayout(self);notice=QLabel('具名作战选项与固定地图资料。情景入口仅打开同名事件总览，文献对应不等于本局可选或已经进入。');notice.setWordWrap(True);layout.addWidget(notice)
        self.refresh_button=QPushButton('重新核对事件与作战');layout.addWidget(self.refresh_button);self.choices=QListWidget();self.choices.setMaximumHeight(180);self.choices.setAccessibleName('文献中的作战选项');layout.addWidget(self.choices)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for v in(self.player,self.technical):v.setReadOnly(True)
        self.tabs.addTab(self.player,'选项与作战');self.tabs.addTab(self.technical,'原文与依据');layout.addWidget(self.tabs,1)
        row=QHBoxLayout();self.stages=QComboBox();self.stages.setAccessibleName('查阅的具体作战配置');self.open_button=QPushButton('打开这份固定作战预览');row.addWidget(self.stages,1);row.addWidget(self.open_button);layout.addLayout(row)
        self.choices.currentItemChanged.connect(self._selected);self.stages.currentIndexChanged.connect(self._stage_changed);self.open_button.clicked.connect(self.open_battle);self.refresh_button.clicked.connect(self.refresh_reference);self.refresh_reference(initial_choice=choice_id)

    def _close_battle(self):
        if self.battle_dialog is not None:self.battle_dialog.close()

    def clear_reference(self):
        self._close_battle();self.result=None;self.choice_id=None
        for v in(self.choices,self.stages):b=v.blockSignals(True);v.clear();v.blockSignals(b)
        self.open_button.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def refresh_reference(self,*_,initial_choice=None):
        fresh=model.reference(self.event_id,self.stage_id)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity'];selected=self.choice_id if keep else initial_choice
        if not keep:self._close_battle()
        self.result=fresh;b=self.choices.blockSignals(True);self.choices.clear()
        for c in fresh['rows']:
            item=QListWidgetItem(c['event_id']+' · '+c['title']);item.setData(Qt.ItemDataRole.UserRole,c['id']);self.choices.addItem(item)
            if c['id']==selected:self.choices.setCurrentItem(item)
        if selected is None:self.choices.setCurrentRow(-1)
        self.choices.blockSignals(b);self._selected(self.choices.currentItem(),preserve=keep)
        if keep and self.battle_dialog is not None and self.battle_dialog.isVisible():self.battle_dialog.panel.refresh_reference()
        return True

    def _selected(self,item,*_,preserve=False):
        cid=item.data(Qt.ItemDataRole.UserRole)if item else None;keep=preserve and cid==self.choice_id;sid=self.stages.currentData()if keep else None
        if not keep:self._close_battle()
        self.choice_id=cid;c=model.choice(self.result,cid)if self.result else None
        if self.result is None:return
        replace_text(self.player,model.player_text(self.result,cid),preserve=keep);replace_text(self.technical,_technical_json({'choice':c,'source':self.result['data']['source'],'identity':self.result['source_identity']})if c else'',preserve=keep)
        b=self.stages.blockSignals(True);self.stages.clear();self.stages.addItem('请选择要查阅的配置；不默认本局版本',None)
        for row in model.stage_rows(self.result,cid):self.stages.addItem(model.stage_label(self.result,cid,row['id']),row['id'])
        self.stages.setCurrentIndex(max(0,self.stages.findData(sid)));self.stages.blockSignals(b);self.open_button.setEnabled(self.stages.currentData()is not None)
        if not keep:self.tabs.setCurrentIndex(0)

    def _stage_changed(self,*_):self._close_battle();self.open_button.setEnabled(self.stages.currentData()is not None)

    def open_battle(self):
        if self.result is None:return False
        if model.reference(self.event_id,self.stage_id)!=self.result:self.clear_reference();return False
        sid=self.stages.currentData()
        if sid not in{v['id']for v in model.stage_rows(self.result,self.choice_id)}:return False
        from .current_battle_view import CurrentBattleDialog
        self._close_battle();self.battle_dialog=CurrentBattleDialog(sid,self);self.battle_dialog.show();return True

    def closeEvent(self,event):self._close_battle();super().closeEvent(event)

class CurrentEventBattlesDialog(QDialog):
    def __init__(self,event_id=None,choice_id=None,stage_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('事件与固定作战 · 选项和版本核对');self.resize(1100,820);layout=QVBoxLayout(self);self.panel=CurrentEventBattlesPanel(event_id,choice_id,stage_id,self);layout.addWidget(self.panel)
    def closeEvent(self,event):self.panel._close_battle();super().closeEvent(event)

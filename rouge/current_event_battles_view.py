"""Named event-to-battle references and reverse lookup with owned dialogs."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QTabWidget,QLabel
from . import current_event_battles as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
from .collapsible_section import QCollapsible
from .reference_copy import mechanism_copy

class CurrentEventBattlesPanel(QWidget):
    def __init__(self,event_id=None,choice_id=None,stage_id=None,parent=None):
        super().__init__(parent);self.event_id=event_id;self.stage_id=stage_id;self.result=None;self.choice_id=None;self.battle_dialog=None;self.flow_dialog=None
        layout=QVBoxLayout(self);notice=QLabel('选择事件选项，查看关联作战。');notice.setWordWrap(True)
        header=QHBoxLayout();header.addWidget(notice,1);self.refresh_button=QPushButton('刷新资料');header.addWidget(self.refresh_button);layout.addLayout(header)
        self.choices=QListWidget();self.choices.setMaximumHeight(180);self.choices.setAccessibleName('文献中的作战选项');layout.addWidget(self.choices)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.technical=QPlainTextEdit()
        for v in(self.player,self.technical):v.setReadOnly(True)
        self.tabs.addTab(self.player,'选项与作战');self.tabs.addTab(self.technical,'原文与依据');layout.addWidget(self.tabs,1)
        self.scope=QCollapsible('资料说明',expandedIcon='−',collapsedIcon='+');self.scope.setDuration(0)
        self.reference_notes=QPlainTextEdit();self.reference_notes.setReadOnly(True);self.reference_notes.setMaximumHeight(150);self.scope.addWidget(self.reference_notes)
        self.scope.content().hide();self.scope.toggled.connect(self.scope.content().setVisible);layout.addWidget(self.scope)
        self.flow_button=QPushButton('查看这一选项的完整对话与代价');self.flow_button.hide();layout.addWidget(self.flow_button);self.flow_button.clicked.connect(self.open_full_flow)
        row=QHBoxLayout();self.stages=QComboBox();self.stages.setAccessibleName('查阅的具体作战配置');self.open_button=QPushButton('打开这份固定作战预览');row.addWidget(self.stages,1);row.addWidget(self.open_button);layout.addLayout(row)
        self.choices.currentItemChanged.connect(self._selected);self.stages.currentIndexChanged.connect(self._stage_changed);self.open_button.clicked.connect(self.open_battle);self.refresh_button.clicked.connect(self.refresh_reference);self.refresh_reference(initial_choice=choice_id)

    def _close_battle(self):
        child=self.battle_dialog;self.battle_dialog=None
        if child is not None:child.close();child.deleteLater()

    def clear_reference(self):
        self._close_battle();self._close_flow();self.flow_button.hide();self.result=None;self.choice_id=None
        for v in(self.choices,self.stages):b=v.blockSignals(True);v.clear();v.blockSignals(b)
        self.open_button.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);replace_text(self.reference_notes,'',preserve=False);self.scope.collapse(animate=False);self.tabs.setCurrentIndex(0)

    def refresh_reference(self,*_,initial_choice=None):
        fresh=model.reference(self.event_id,self.stage_id)
        if fresh is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity'];selected=self.choice_id if keep else initial_choice
        if not keep:self._close_battle();self._close_flow()
        self.result=fresh;b=self.choices.blockSignals(True);self.choices.clear()
        for c in fresh['rows']:
            item=QListWidgetItem(c['event_id']+' · '+c['title']);item.setData(Qt.ItemDataRole.UserRole,c['id']);self.choices.addItem(item)
            if c['id']==selected:self.choices.setCurrentItem(item)
        if selected is None:self.choices.setCurrentRow(-1)
        self.choices.setMaximumHeight(min(180,sum(self.choices.sizeHintForRow(i)for i in range(self.choices.count()))+2*self.choices.frameWidth()))
        self.choices.blockSignals(b);self._selected(self.choices.currentItem(),preserve=keep)
        if keep and self.battle_dialog is not None and self.battle_dialog.isVisible():self.battle_dialog.panel.refresh_reference()
        if keep and self.flow_dialog is not None and self.flow_dialog.isVisible():self.flow_dialog.panel.refresh_reference()
        return True

    def _selected(self,item,*_,preserve=False):
        cid=item.data(Qt.ItemDataRole.UserRole)if item else None;keep=preserve and cid==self.choice_id;sid=self.stages.currentData()if keep else None
        if not keep:self._close_battle();self._close_flow()
        self.choice_id=cid;c=model.choice(self.result,cid)if self.result else None
        if self.result is None:return
        _,target=self._flow_target(cid)
        self.flow_button.setVisible(target is not None);self.flow_button.setEnabled(target is not None)
        if target is None:self._close_flow()
        full_text=model.player_text(self.result,cid,prepared_choice=c)
        replace_text(self.player,mechanism_copy(full_text,'',extra_detail_headings=('【从固定关卡反查】','【重复记载】','【仍需区分】'))[0],preserve=keep);replace_text(self.reference_notes,full_text,preserve=keep)
        replace_text(self.technical,_technical_json({'choice':c,'source':self.result['data']['source'],'identity':self.result['source_identity']})if c else'',preserve=keep)
        b=self.stages.blockSignals(True);self.stages.clear();self.stages.addItem('选择作战配置',None)
        rows=model.stage_rows(self.result,cid,prepared_choice=c)
        for row in rows:self.stages.addItem(model.stage_label(self.result,cid,row['id'],prepared_rows=rows),row['id'])
        self.stages.setCurrentIndex(max(0,self.stages.findData(sid)));self.stages.blockSignals(b);self.open_button.setEnabled(self.stages.currentData()is not None)
        if not keep:self.tabs.setCurrentIndex(0);self.scope.collapse(animate=False)

    def _stage_changed(self,*_):self._close_battle();self.open_button.setEnabled(self.stages.currentData()is not None)

    def open_battle(self):
        if self.result is None:return False
        if model.reference(self.event_id,self.stage_id)!=self.result:self.clear_reference();return False
        sid=self.stages.currentData()
        rows=model.stage_rows(self.result,self.choice_id)
        if sid not in{v['id']for v in rows}:return False
        from .player_reference_links import open_stage
        opened=open_stage(self,sid,context=lambda:None if self.result is None else(self.result['source_identity'],self.choice_id,self.stages.currentData()))
        if opened is not None:return opened
        from .player_map_reader import make_reader
        if self.battle_dialog is not None and self.battle_dialog.panel.stage_id!=sid:self._close_battle()
        if self.battle_dialog is None:
            self.battle_dialog=make_reader('battle',{'id':sid,'title':model.stage_label(self.result,self.choice_id,sid,prepared_rows=rows)},self)
        elif self.battle_dialog.panel.refresh_reference()is False:self._close_battle()
        if self.battle_dialog is None:return False
        self.battle_dialog.show();self.battle_dialog.raise_();return True

    def _close_flow(self):
        if self.flow_dialog is not None:self.flow_dialog.close()

    @staticmethod
    def _flow_target(cid):
        if cid is None:return None,None
        from .current_encounters import locate
        target=locate('choices',cid)
        if target is not None:return 'encounter',target
        from .current_lake import locate as lake_locate
        return 'lake',lake_locate('choices',cid)

    def open_full_flow(self):
        if self.result is None:return False
        if model.reference(self.event_id,self.stage_id)!=self.result:self.clear_reference();return False
        kind,target=self._flow_target(self.choice_id)
        if target is None:self._close_flow();self.flow_button.hide();return False
        from .player_reference_links import open_full_event
        opened=open_full_event(self,kind,target)
        if opened is not None:return opened
        self._close_flow()
        if kind=='lake':
            from .current_lake_view import CurrentLakeDialog
            self.flow_dialog=CurrentLakeDialog(target,self)
        else:
            from .current_encounters_view import CurrentEncountersDialog
            self.flow_dialog=CurrentEncountersDialog(target['event_id'],target['scene_id'],target['choice_id'],self)
        self.flow_dialog.show();return True

    def closeEvent(self,event):self._close_battle();self._close_flow();super().closeEvent(event)

from .player_window_frame import PlayerDialog


class CurrentEventBattlesDialog(PlayerDialog):
    def __init__(self,event_id=None,choice_id=None,stage_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('事件与固定作战 · 选项和版本核对');layout=QVBoxLayout(self);self.panel=CurrentEventBattlesPanel(event_id,choice_id,stage_id,self);layout.addWidget(self.panel)
        from .player_map_reader import prepare_reference_window
        prepare_reference_window(self,760,600)
    def closeEvent(self,event):self.panel._close_battle();self.panel._close_flow();super().closeEvent(event)

    def reject(self):self.panel._close_battle();self.panel._close_flow();super().reject()

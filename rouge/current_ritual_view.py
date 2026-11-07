"""Owned ritual, source-event and static-battle readers."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout,QPushButton
from .documented_event_flow_view import DocumentedEventFlowPanel
from . import current_ritual_reference as model
from .flow_layout import FlowLayout

class CurrentRitualPanel(DocumentedEventFlowPanel):
    def __init__(self,event_id='ritual',scene_id=None,choice_id=None,parent=None):
        self.material_dialog=None
        super().__init__(event_id,scene_id,parent,reference_model=model, defer_initial_refresh=True)
        row=FlowLayout();self.material_button=QPushButton('查看这件材料的来源');self.related_button=QPushButton('查看相关首领：畸症（未套用削弱）')
        row.addWidget(self.material_button);row.addWidget(self.related_button);self.layout().insertLayout(3,row)
        self.material_button.clicked.connect(self.open_material);self.related_button.clicked.connect(self.open_related)
        self.refresh_reference(initial_scene=scene_id, initial=True)
        if choice_id:
            for i in range(self.choices.count()):
                if self.choices.item(i).data(Qt.ItemDataRole.UserRole)==choice_id:self.choices.setCurrentRow(i);break

    def _close_material(self):
        if self.material_dialog is not None:self.material_dialog.close()

    def _sync_extra(self,choice=...):
        source=model.acquisition_reference(self.result,self.scene_id,self.choice_id,choice=choice)if self.result else None
        if source and source['kind']=='exchange':
            from .current_exchange_reference import target_entry
            if target_entry('choices',source['source_choice_id'])is None:source=None
        self.material_button.setVisible(source is not None);self.material_button.setEnabled(source is not None)
        related=self.result is not None and self.event_id=='ritual';self.related_button.setVisible(related);self.related_button.setEnabled(related)
        if source is None:self._close_material()

    def clear_reference(self):
        super().clear_reference();self._sync_extra(None)

    def _choice_changed(self,item,*args,preserve=False):
        cid=item.data(Qt.ItemDataRole.UserRole)if item else None
        if not(preserve and cid==self.choice_id):self._close_material()
        choice=super()._choice_changed(item,*args,preserve=preserve);self._sync_extra(choice)

    def refresh_reference(self,*args,**kwargs):
        ok=super().refresh_reference(*args,**kwargs)
        if ok and self.material_dialog is not None and self.material_dialog.isVisible():self.material_dialog.panel.refresh_reference()
        return ok

    def open_material(self):
        if not self._recheck():return False
        source=model.acquisition_reference(self.result,self.scene_id,self.choice_id)
        if source is None:self._close_material();return False
        from .player_reference_links import open_material_source
        opened=open_material_source(self,source)
        if opened is not None:return opened
        if source['kind']=='event':
            target=model.locate('choices',source['source_choice_id'])
            if target is None:self.clear_reference();return False
            new=CurrentRitualDialog(target['event_id'],target['scene_id'],target['choice_id'],self)
        elif source['kind']=='exchange':
            from .current_exchange_reference import target_entry
            from .current_exchange_view import CurrentExchangeDialog
            target=target_entry('choices',source['source_choice_id'])
            if target is None:
                self._close_material();self.material_button.hide();self.material_button.setEnabled(False);return False
            new=CurrentExchangeDialog(target,self)
        elif source['kind']=='battle':
            from .current_battle_view import CurrentBattleDialog
            new=CurrentBattleDialog(source['stage_id'],self)
        else:raise ValueError('未支持的材料来源类型：'+str(source['kind']))
        self._close_material();self.material_dialog=new;new.show();return True

    def open_related(self):
        if not self._recheck()or self.event_id!='ritual':return False
        from .player_reference_links import open_stage
        opened=open_stage(self,self.result['data']['related_boss_stage_id'])
        if opened is not None:return opened
        from .current_battle_view import CurrentBattleDialog
        self._close_battle();self.battle_dialog=CurrentBattleDialog(self.result['data']['related_boss_stage_id'],self);self.battle_dialog.show();return True

    def closeEvent(self,event):
        self._close_material();super().closeEvent(event)

from .player_window_frame import PlayerDialog


class CurrentRitualDialog(PlayerDialog):
    def __init__(self,event_id='ritual',scene_id=None,choice_id=None,parent=None):
        super().__init__(parent);self.setWindowTitle('调谐仪式 · 选项、削弱与材料来源'if event_id=='ritual'else'泪之聚落 · 选项与获得')
        layout=QVBoxLayout(self);self.panel=CurrentRitualPanel(event_id,scene_id,choice_id,self);layout.addWidget(self.panel)
        from .documented_event_flow_view import prepare_event_dialog
        prepare_event_dialog(self)
    def closeEvent(self,event):
        self.panel._close_material();self.panel._close_battle();super().closeEvent(event)

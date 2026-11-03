"""Manual source-bound ending reference; never updates actual run memory."""
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QGridLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QPushButton,QTabWidget,QPlainTextEdit
from . import ending_event_reference as model
from .branch_choice import BranchChoice
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class EndingEventPanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.result=None;self.identity=None;self.source_identity=None
        layout=QVBoxLayout(self)
        notice=QLabel('旧日重燃：查看已查证的事件、选项和相关作战。下方条件仅供对照，不代表本局已读取，也不会改写本局记忆。');notice.setWordWrap(True);layout.addWidget(notice)
        self.combo=QComboBox();self.choices=BranchChoice(self.combo,[],overview_label='总览（结局相关信息）',placeholder='请选择事件或区域');layout.addWidget(self.choices)
        self.controls={};grid=QGridLayout();layout.addLayout(grid)
        specifications=[('scope','查看范围',[('当前节点','current'),('下一层生成条件','future'),('以前经过的节点','history')]),('floor','主层',[('未知',None)]+[(str(n),n)for n in range(1,7)]),('region','区域',[('未知','unknown'),('主要区域','main'),('熄日余径','熄日余径'),('盲目者所见','盲目者所见')]),('node_type','节点',[('未知','unknown')]+[(n,n)for n in ('险路尽头','命运所指','不期而遇','普通作战','紧急作战','险路恶敌')])]
        labels={'post_update_clear':'更新后已通关一次','has_prayer':'持有谒日之祈','has_covenant':'持有祭日之契','adventurer_alive':'探险家仍存活','next_unmarked_after_first_down':'首次倒下后的下个无标记不期而遇','rescue_used':'本局救援机会已使用'}
        specifications +=[(k,labels[k],[('未知',None),('是',True),('否',False)])for k in model.BOOL_FIELDS]
        for i,(key,label,options)in enumerate(specifications):
            control=QComboBox();control.setAccessibleName(label)
            for text,value in options:control.addItem(text,value)
            self.controls[key]=control;row,col=divmod(i,2);grid.addWidget(QLabel(label),row,col*2);grid.addWidget(control,row,col*2+1);control.currentIndexChanged.connect(self._context_changed)
        bar=QHBoxLayout();self.gold=QLineEdit();self.gold.setPlaceholderText('源石锭：留空表示未知');self.gold.setAccessibleName('用于对照的源石锭');bar.addWidget(self.gold);self.refresh_button=QPushButton('重新核对资料');bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.player,'条件与后续');self.tabs.addTab(self.technical,'完整来源');layout.addWidget(self.tabs,1)
        self.flow_button=QPushButton('逐步查看本事件的选项、奖励和后续');self.flow_button.hide();layout.addWidget(self.flow_button);self.flow_button.clicked.connect(self.open_documented_flow)
        bar=QHBoxLayout();self.battle_combo=QComboBox();self.battle_combo.setAccessibleName('相关作战的精确配置');self.battle_button=QPushButton('查看这场作战');bar.addWidget(self.battle_combo,1);bar.addWidget(self.battle_button);layout.addLayout(bar)
        self.combo.currentIndexChanged.connect(self._selected);self.gold.textChanged.connect(self._context_changed);self.refresh_button.clicked.connect(self.refresh_reference);self.battle_combo.currentIndexChanged.connect(self._battle_changed);self.battle_button.clicked.connect(self.open_battle);self.refresh_reference()

    def _close_battle(self):
        dialog=getattr(self,'battle_dialog',None)
        if dialog is not None:dialog.close()

    def _close_flow(self):
        dialog=getattr(self,'flow_dialog',None)
        if dialog is not None:dialog.close()

    def clear_reference(self):
        self._close_battle();self._close_flow();self.flow_button.hide();self.result=None;self.identity=None;self.source_identity=None;self.choices.set_groups([],emit=False)
        blocked=self.battle_combo.blockSignals(True);self.battle_combo.clear();self.battle_combo.blockSignals(blocked);self.battle_button.setEnabled(False)
        replace_text(self.player,'来源暂时无法核对，旧条件和作战入口已清除。恢复后请手动重新选择。',preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def refresh_reference(self):
        ref=model.packet()
        if ref is None:self.clear_reference();return False
        keep=self.source_identity==ref['identity'];selected=self.combo.currentData()if keep else None;self.source_identity=ref['identity']
        groups=[(name,[(r['title'],r['id'],QIcon())for r in ref['data']['records']if r['group']==name])for name in dict.fromkeys(r['group']for r in ref['data']['records'])]
        blocked=self.combo.blockSignals(True);self.choices.set_groups(groups,emit=False)
        self.choices.select_value(selected,emit=False)if selected is not None else self.combo.setCurrentIndex(0)
        self.combo.blockSignals(blocked);self._selected(preserve=keep);return True

    def declared_context(self):
        values={k:c.currentData()for k,c in self.controls.items()};raw=self.gold.text().strip()
        if raw and(not raw.isascii()or not raw.isdecimal()):raise ValueError('源石锭请输入非负整数，或留空表示未知。')
        values['gold']=int(raw)if raw else None;return model.context(values)

    def _context_changed(self,*_):self._selected(preserve=True)

    def _selected(self,*_,preserve=False):
        identity=self.combo.currentData();keep=preserve and identity==self.identity;old_battle=self.battle_combo.currentData()if keep else None
        if not keep:self._close_battle();self._close_flow()
        try:values=self.declared_context()
        except ValueError as exc:
            self._close_battle();self._close_flow();self.flow_button.hide();self.result=None;self.battle_combo.clear();self.battle_button.setEnabled(False);replace_text(self.player,str(exc),preserve=False);replace_text(self.technical,'',preserve=False);return
        result=model.evaluate(identity,values)if identity is not None else None
        if identity is not None and result is None:self.clear_reference();return
        self.identity=identity;self.result=result
        self.flow_button.setVisible(result is not None and identity in ('button','blueprint','revive'))
        self.flow_button.setEnabled(result is not None and identity in ('button','blueprint','revive'))
        child=getattr(self,'flow_dialog',None)
        if keep and child is not None and child.isVisible():child.panel.refresh_reference()
        replace_text(self.player,model.player_text(result)if result else'请选择一项。条件不全时会保留未知，不据此排除所有事件。',preserve=keep)
        replace_text(self.technical,_technical_json(result)if result else'',preserve=keep)
        blocked=self.battle_combo.blockSignals(True);self.battle_combo.clear();self.battle_combo.addItem('手动选择相关作战；同名配置分别保留',None)
        ids=result['record']['stage_ids']if result else[]
        for index,sid in enumerate(ids):
            row=result['originals']['stages'][sid];kind='紧急作战'if sid.startswith('ro6_e_')else'险路恶敌'if sid.startswith('ro6_b_')else'普通作战'if sid.startswith('ro6_n_')else'特殊作战'
            self.battle_combo.addItem(kind+' · '+row['name']+' · 资料'+str(index+1),sid)
        if old_battle is not None:self.battle_combo.setCurrentIndex(max(0,self.battle_combo.findData(old_battle)))
        self.battle_combo.blockSignals(blocked);self._battle_changed()
        if not keep:self.tabs.setCurrentIndex(0)

    def _battle_changed(self,*_):self.battle_button.setEnabled(self.result is not None and self.battle_combo.currentData()is not None)

    def open_battle(self):
        sid=self.battle_combo.currentData()
        if self.result is None or sid is None:return False
        fresh=model.evaluate(self.identity,self.declared_context())
        if fresh!=self.result:self.clear_reference();return False
        if sid not in fresh['record']['stage_ids']:return False
        from .current_battle_view import CurrentBattleDialog
        self._close_battle();self.battle_dialog=CurrentBattleDialog(sid,self);self.battle_dialog.show();return True

    def open_documented_flow(self):
        if self.result is None or self.identity not in ('button','blueprint','revive'):return False
        if model.evaluate(self.identity,self.declared_context())!=self.result:self.clear_reference();return False
        from .documented_event_flow_view import DocumentedEventFlowDialog
        from .documented_event_flows import reference
        if reference(self.identity)is None:
            self._close_flow();self.flow_button.setEnabled(False);return False
        self.flow_button.setEnabled(True);self._close_flow();self.flow_dialog=DocumentedEventFlowDialog(self.identity,parent=self);self.flow_dialog.show();return True

    def closeEvent(self,event):self._close_battle();self._close_flow();super().closeEvent(event)


class EndingEventDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('旧日重燃 · 事件条件与相关作战');self.resize(1060,820);layout=QVBoxLayout(self);self.panel=EndingEventPanel(self);layout.addWidget(self.panel)

    def closeEvent(self,event):self.panel._close_battle();self.panel._close_flow();super().closeEvent(event)

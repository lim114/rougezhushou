"""Terrain-to-stage lookup with an exact cell jump and guarded owned map."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QTabWidget,QPushButton,QSplitter)
from . import current_terrain_directory as model
from . import current_stage_directory as directory
from .boss_hunt_view import _technical_json
from .ui_state import replace_text

class CurrentTerrainDirectoryPanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.reference=None;self.result=None;self.selected_key=None;self.map_dialog=None
        layout=QVBoxLayout(self);notice=QLabel(model.NOTICE);notice.setWordWrap(True);layout.addWidget(notice)
        bar=QHBoxLayout();self.search=QLineEdit();self.search.setPlaceholderText('搜索地形、效果或关卡名，例如：草丛、推、灵魂归宿')
        self.kind=QComboBox();self.kind.setAccessibleName('地形用途分支')
        for value,name in model.KINDS:self.kind.addItem(name,value)
        self.floor=QComboBox();self.floor.setAccessibleName('地形关卡层数')
        for value,name in directory.FLOORS:self.floor.addItem(name,value)
        self.play_kind=QComboBox();self.play_kind.setAccessibleName('地形关卡来源')
        for value,name in directory.KINDS:self.play_kind.addItem(name,value)
        self.refresh_button=QPushButton('重新核对资料')
        for widget in (self.search,self.kind,self.floor,self.play_kind,self.refresh_button):bar.addWidget(widget)
        layout.addLayout(bar);self.count=QLabel();self.count.setWordWrap(True);layout.addWidget(self.count)
        split=QSplitter();layout.addWidget(split,1);self.entries=QListWidget();self.entries.setWordWrap(True);self.entries.setAccessibleName('地形对应的独立关卡与参数记录');split.addWidget(self.entries)
        right=QWidget();body=QVBoxLayout(right);split.addWidget(right);split.setSizes([430,700])
        cells=QHBoxLayout();self.cells=QComboBox();self.cells.setAccessibleName('这份地形的准确地图格');self.open_button=QPushButton('在对应地图上查看这个格子')
        cells.addWidget(self.cells,1);cells.addWidget(self.open_button);body.addLayout(cells)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'地形、效果与限制');self.tabs.addTab(self.technical,'完整原值与来源');body.addWidget(self.tabs,1)
        self.search.textChanged.connect(self._filter_changed)
        for widget in (self.kind,self.floor,self.play_kind):widget.currentIndexChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected);self.cells.currentIndexChanged.connect(self._cell_changed)
        self.refresh_button.clicked.connect(self.refresh_reference);self.open_button.clicked.connect(self.open_map);self.refresh_reference()

    def close_owned(self):
        if self.map_dialog is not None:
            child=self.map_dialog;self.map_dialog=None;child.panel.clear_reference();child.close()

    def _finished(self,child):
        child.panel.clear_reference()
        if self.map_dialog is child:self.map_dialog=None

    def _clear_detail(self,text=None):
        self.close_owned();self.result=None;self.selected_key=None
        blocked=self.entries.blockSignals(True);self.entries.setCurrentRow(-1);self.entries.blockSignals(blocked)
        blocked=self.cells.blockSignals(True);self.cells.clear();self.cells.blockSignals(blocked);self.cells.setEnabled(False);self.open_button.setEnabled(False)
        replace_text(self.player,text or model.player_text(None),preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def clear_reference(self):
        self.reference=None;blocked=self.entries.blockSignals(True);self.entries.clear();self.entries.blockSignals(blocked)
        self._clear_detail(model.UNAVAILABLE);self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self,*_):self._populate(preserve=False)

    def _populate(self,*,preserve):
        if self.reference is None:self.clear_reference();return
        key=self.selected_key if preserve else None
        visible=model.rows(self.search.text(),self.kind.currentData(),self.floor.currentData(),self.play_kind.currentData(),reference=self.reference)
        blocked=self.entries.blockSignals(True);self.entries.clear()
        for row in visible:
            item=QListWidgetItem(model.label(row));item.setData(Qt.ItemDataRole.UserRole,tuple(row['key']));self.entries.addItem(item)
            if tuple(row['key'])==key:self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        self.count.setText(f'找到{len(visible)}份地形参数记录，涉及{len({r["stage_id"] for r in visible})}份固定关卡配置；同名配置和不同参数分别保留。')
        if self.entries.currentItem() is None:self._clear_detail()
        else:self._selected(self.entries.currentItem(),preserve=preserve)

    def refresh_reference(self):
        fresh=model.packet()
        if fresh is None:self.clear_reference();return False
        keep=self.reference is not None and self.reference['source_identity']==fresh['source_identity']
        if not keep:self._clear_detail()
        self.reference=fresh;self._populate(preserve=keep)
        if keep and self.map_dialog is not None:
            child=self.map_dialog;expected=model.exact_map(self.result)
            if expected is None or not child.panel.refresh_reference() or child.panel.result!=expected:self.close_owned()
        return True

    def select_target(self,key):
        if self.reference is None:self.clear_reference();return False
        info=model.detail(key,reference=self.reference)
        if info is None:self._clear_detail('指定的地形记录不能核对，请重新选择。');return False
        for widget in (self.search,self.kind,self.floor,self.play_kind):widget.blockSignals(True)
        self.search.clear()
        for widget in (self.kind,self.floor,self.play_kind):widget.setCurrentIndex(widget.findData(None))
        for widget in (self.search,self.kind,self.floor,self.play_kind):widget.blockSignals(False)
        self._populate(preserve=False)
        for i in range(self.entries.count()):
            item=self.entries.item(i)
            if tuple(item.data(Qt.ItemDataRole.UserRole))==tuple(key):self.entries.setCurrentItem(item);return True
        self._clear_detail('指定的地形记录没有出现在列表中。');return False

    def _selected(self,item,*_,preserve=False):
        key=item.data(Qt.ItemDataRole.UserRole) if item else None;info=model.detail(key,reference=self.reference)
        if info is None:self._clear_detail();return
        keep=preserve and self.selected_key==tuple(key);cell=self.cells.currentData() if keep else None
        if not keep:self.close_owned()
        self.result=info;self.selected_key=tuple(key);blocked=self.cells.blockSignals(True);self.cells.clear()
        for row,col in info['row']['cells']:self.cells.addItem(f'第{row+1}行 · 第{col+1}列',(row,col))
        self.cells.setCurrentIndex(next((i for i in range(self.cells.count()) if tuple(self.cells.itemData(i))==tuple(cell)),-1) if cell is not None else -1);self.cells.blockSignals(blocked);self.cells.setEnabled(True)
        self.open_button.setEnabled(self.cells.currentData() is not None)
        replace_text(self.player,model.player_text(info),preserve=keep);replace_text(self.technical,_technical_json(info),preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)

    def _cell_changed(self,*_):
        self.close_owned();self.open_button.setEnabled(self.result is not None and self.cells.currentData() is not None)

    def open_map(self):
        cell=self.cells.currentData();expected=model.exact_map(self.result)
        valid=self.result is not None and self.selected_key==tuple(self.result['row']['key']) and type(cell)in(tuple,list) and list(cell)in self.result['row']['cells']
        if not valid or expected is None:self.clear_reference();return False
        self.close_owned()
        from .current_map_position_view import CurrentMapPositionDialog
        child=CurrentMapPositionDialog(self.result['row']['stage_id'],self);self.map_dialog=child
        child.finished.connect(lambda _result:self._finished(child))
        if child.panel.result!=expected or not child.panel.select_cell(*cell):self.clear_reference();return False
        child.show();return True

    def closeEvent(self,event):self.clear_reference();super().closeEvent(event)

class CurrentTerrainDirectoryDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent);self.setWindowTitle('按地形与效果查找关卡');self.resize(1200,850)
        layout=QVBoxLayout(self);self.panel=CurrentTerrainDirectoryPanel(self);layout.addWidget(self.panel)

    def done(self,result):self.panel.clear_reference();super().done(result)
    def closeEvent(self,event):self.panel.clear_reference();super().closeEvent(event)

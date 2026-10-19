"""Plain-language, version-separated update reader; no game interactions."""
from copy import deepcopy
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,QTabWidget,QPushButton,QSplitter
from . import expansion_reference as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text


class ExpansionUpdatePanel(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.source_identity=None;self.result=None;self.image_raw=None
        layout=QVBoxLayout(self);self.notice=QLabel(model.NOTICE);self.notice.setWordWrap(True);layout.addWidget(self.notice)
        bar=QHBoxLayout();self.category=QComboBox();self.category.setAccessibleName('更新资料分类')
        for key,label in model.CATEGORIES:self.category.addItem(label,key)
        self.scope=QComboBox();self.scope.addItem('只看新增与改动',True);self.scope.addItem('查看本版本全部资料',False)
        self.search=QLineEdit();self.search.setPlaceholderText('按中文名称搜索；同名资料分别保留')
        self.refresh_button=QPushButton('重新核对资料');bar.addWidget(self.category);bar.addWidget(self.scope);bar.addWidget(self.search,1);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        self.count=QLabel();layout.addWidget(self.count)
        split=QSplitter();layout.addWidget(split,1);self.entries=QListWidget();self.entries.setAccessibleName('本版本资料条目');split.addWidget(self.entries)
        right=QWidget();body=QVBoxLayout(right);self.map_image=QLabel('选择关卡可查看固定原图');self.map_image.setAlignment(Qt.AlignmentFlag.AlignCenter);self.map_image.setMinimumSize(260,150);body.addWidget(self.map_image)
        self.next_button=QPushButton('查看原资料指定的后续场景');self.next_button.hide();body.addWidget(self.next_button)
        self.battle_button=QPushButton('查看本版本关卡：原图、敌人和出怪条件');self.battle_button.hide();body.addWidget(self.battle_button)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True)
        self.tabs.addTab(self.player,'条件与用途');self.tabs.addTab(self.technical,'完整原值与来源');body.addWidget(self.tabs,1);split.addWidget(right);split.setSizes([300,750])
        self.category.currentIndexChanged.connect(self._filter_changed);self.scope.currentIndexChanged.connect(self._filter_changed);self.search.textChanged.connect(self._filter_changed)
        self.entries.currentItemChanged.connect(self._selected);self.next_button.clicked.connect(self.follow_scene);self.refresh_button.clicked.connect(self.refresh_reference)
        self.battle_button.clicked.connect(self.open_current_battle)
        self.refresh_reference()

    def _clear_detail(self,notice='请先选择一项资料。'):
        dialog=getattr(self,'current_battle_dialog',None)
        if dialog is not None:dialog.close()
        self.result=None;self.image_raw=None;self.map_image.clear();self.map_image.setText(notice);self.next_button.hide();self.next_button.setEnabled(False)
        self.battle_button.hide();self.battle_button.setEnabled(False)
        replace_text(self.player,'',preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)

    def _unavailable(self):
        self.source_identity=None
        # clear() destroys the C++ items. Suppress currentItemChanged while they
        # are being destroyed; its old-item argument must not reenter Python.
        blocked=self.entries.blockSignals(True)
        try:self.entries.clear()
        finally:self.entries.blockSignals(blocked)
        self._clear_detail(model.UNAVAILABLE);self.count.setText(model.UNAVAILABLE)

    def _filter_changed(self,*_):
        self._populate(preserve=False)

    def _populate(self,*,preserve):
        reference=model.packet()
        if reference is None:self._unavailable();return False
        same=self.source_identity==reference['source_identity']
        current=self.entries.currentItem();selected=current.data(Qt.ItemDataRole.UserRole)if preserve and same and current else None
        self.source_identity=reference['source_identity']
        items=model.rows(self.category.currentData(),changes_only=self.scope.currentData(),reference=reference)
        query=self.search.text().strip();visible=[r for r in items if not query or query in r['name']]
        blocked=self.entries.blockSignals(True);self.entries.clear()
        for row in visible:
            item=QListWidgetItem(row['label']);item.setData(Qt.ItemDataRole.UserRole,row['id']);self.entries.addItem(item)
            if row['id']==selected:self.entries.setCurrentItem(item)
        self.entries.blockSignals(blocked)
        self.count.setText('当前分类列出'+str(len(visible))+'项资料。条目包含同名变体与强化档位，不等于新增地图或新增分队的数量。')
        if selected is None or self.entries.currentItem()is None:self.entries.setCurrentRow(-1);self._clear_detail()
        else:self._selected(self.entries.currentItem(),preserve=True)
        return True

    def refresh_reference(self):
        # After source loss, no old identity survives; recovery restores a list, not a prior selection.
        return self._populate(preserve=True)

    def _selected(self,item,*_,preserve=False):
        if item is None:self._clear_detail();return
        key=item.data(Qt.ItemDataRole.UserRole);result=model.detail(self.category.currentData(),key)
        if result is None or result['source_identity']!=self.source_identity:self._unavailable();return
        keep=preserve and self.result is not None and self.result['row']['id']==key and self.result['row']['category']==result['row']['category']
        self.result=deepcopy(result)
        is_stage=result['row']['category']=='stages';self.battle_button.setVisible(is_stage);self.battle_button.setEnabled(is_stage)
        replace_text(self.player,result['player_text'],preserve=keep);replace_text(self.technical,_technical_json(result),preserve=keep)
        if not keep:self.tabs.setCurrentIndex(0)
        target=result['next_scene'];self.next_button.setVisible(target is not None);self.next_button.setEnabled(target is not None)
        if target:self.next_button.setText('查看后续场景：'+target['title'])
        self.image_raw=model.image_bytes(result['image'])
        self._draw_image()

    def _draw_image(self):
        if self.image_raw is None:
            self.map_image.clear();self.map_image.setText('本项无地图资料'if self.result and self.result['image']is None else'固定地图原图暂时无法核对。');return
        pixmap=QPixmap()
        if not pixmap.loadFromData(self.image_raw,'PNG')or pixmap.isNull():self.image_raw=None;self.map_image.clear();self.map_image.setText('原图无法读取。');return
        self.map_image.setPixmap(pixmap.scaled(max(1,self.map_image.width()-8),220,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        self.map_image.setToolTip('固定原图，可随窗口缩放查看；尚未校准位置，不显示未经核对的出怪标记。')

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'map_image'):self._draw_image()

    def follow_scene(self):
        if self.result is None or self.result['next_scene']is None:return False
        # Requery the exact choice before following its explicit nextSceneId; never infer its parent scene.
        current=model.detail(self.result['row']['category'],self.result['row']['id'])
        if current!=self.result:self._unavailable();return False
        target=current['next_scene']['id'];self.search.clear();self.scope.setCurrentIndex(self.scope.findData(False));self.category.setCurrentIndex(self.category.findData('scenes'))
        for i in range(self.entries.count()):
            if self.entries.item(i).data(Qt.ItemDataRole.UserRole)==target:self.entries.setCurrentRow(i);return True
        self._clear_detail('指定场景在本版本资料中无法核对。');return False

    def open_current_battle(self):
        if self.result is None or self.result['row']['category']!='stages':return False
        fresh=model.detail('stages',self.result['row']['id'])
        if fresh!=self.result:self._unavailable();return False
        from .current_battle_view import CurrentBattleDialog
        previous=getattr(self,'current_battle_dialog',None)
        if previous is not None:previous.close()
        self.current_battle_dialog=CurrentBattleDialog(fresh['row']['id'],self)
        self.current_battle_dialog.show()
        return True

"""Stage candidates come from recorded names or exact IDs; never live combat."""
from . import current_battle_reference as model
from . import expansion_reference
from collections import Counter

def stage_candidates(content):
    if not isinstance(content,dict)or content.get('kind')!='battle':return []
    packet=expansion_reference.packet()
    if packet is None:return []
    rows=packet['current']['details']['stages'];identity=None
    for field in('stage_id','variant_id'):
        if field in content and content[field]is not None:
            if not isinstance(content[field],str)or not content[field].strip():return []
            identity=content[field];break
    if identity is not None:
        ids=[identity]if identity in rows else[]
    else:
        title=content.get('title');ids=[k for k,v in rows.items()if v.get('name')==title]if isinstance(title,str)and title.strip()else[]
    return [{'id':k,'name':rows[k]['name'],'label':rows[k]['name']+' · '+('紧急'if rows[k]['isElite']else'领袖'if rows[k]['isBoss']else'普通')+' · 候选'+str(i+1)}for i,k in enumerate(ids)]

from PySide6.QtCore import Qt,QSize,Signal
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QListWidget,QListWidgetItem,QPlainTextEdit,QPushButton,QTabWidget

class SceneBattlePanel(QWidget):
    historical_reading=False
    noteRequested=Signal(object)
    def __init__(self,run,parent=None):
        super().__init__(parent);self.run=run;self.identity=None;self.result=None;self.enemies={};self.context_key=None;self.dialog=None
        body=QVBoxLayout(self);self.notice=QLabel('最近读取的关卡资料，不证明当前位置、实际出现或本局面板。未完整核验的数值保持未知。');self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.stages=QComboBox();self.stages.currentIndexChanged.connect(self.select_stage);body.addWidget(self.stages)
        self.tabs=QTabWidget();self.lists={}
        for tier,label in [('NORMAL','普通'),('ELITE','精英'),('BOSS','领袖'),(None,'类别未确认')]:
            widget=QListWidget();widget.setIconSize(QSize(48,48));widget.setViewMode(QListWidget.ViewMode.IconMode);widget.setResizeMode(QListWidget.ResizeMode.Adjust);widget.setGridSize(QSize(125,100));widget.setWordWrap(True);widget.currentItemChanged.connect(self.select_enemy);self.tabs.addTab(widget,label);self.lists[tier]=widget
        self.tabs.currentChanged.connect(self.select_enemy);body.addWidget(self.tabs,1)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1)
        self.open_button=QPushButton('打开所选关卡的固定地图与完整资料');self.open_button.clicked.connect(self.open_stage);body.addWidget(self.open_button)
        self.note_button=QPushButton('为这个准确关卡写笔记');body.addWidget(self.note_button);self.note_button.clicked.connect(self.write_note)
        self.refresh()
    def write_note(self):
        self.refresh()
        if self.result is None:return
        from .player_reference_notes import note_for
        content=note_for('stages',self.identity)
        if content is not None:self.noteRequested.emit(content)
    def refresh(self):
        if self.dialog is not None and self.dialog.isVisible():
            self.dialog.panel.set_context({}if self.historical_reading else self.run.state.get('config',{}))
        content=self.run.state.get('last_node_content')
        if not isinstance(content,dict):content=None
        rows=stage_candidates(content);reference=model.packet()if rows else None
        if reference is None:rows=[]
        key=(repr({k:(content or{}).get(k)for k in('kind','title','stage_id','variant_id')}),repr(rows),reference['identity']if reference else None)
        if key==self.context_key:return
        self.context_key=key;old=self.stages.currentData();self.stages.blockSignals(True);self.stages.clear();self.stages.addItem('请选择准确关卡版本',None)
        for row in rows:self.stages.addItem(row['label'],row['id'])
        index=self.stages.findData(old)if old else-1;self.stages.setCurrentIndex(max(0,index));self.stages.blockSignals(False);self.select_stage()
        if not rows:self.notice.setText('尚无可准确关联的最近关卡；旧资料已清除，可从地图节点打开固定关卡资料。')
        else:self.notice.setText('最近读取：'+str(content.get('title')or'已记录关卡')+'。请核对所选版本；候选不是本局必出，图鉴不替代完整条件和预计面板。')
    def select_stage(self,*_):
        identity=self.stages.currentData();self.identity=identity;self.result=model.stage_reference(identity)if identity else None;self.enemies={};self.detail.clear();self.open_button.setEnabled(self.result is not None)
        self.note_button.setVisible(self.result is not None)
        for widget in self.lists.values():widget.clear()
        if self.dialog is not None:self.dialog.close();self.dialog=None
        if self.result is None:
            self.detail.setPlainText('所选关卡资料无法核对，旧内容已清除。'if identity else'请选择准确关卡版本。');return
        counts=Counter(enemy['name']for enemy in self.result['enemies']);occurrences=Counter()
        for enemy in self.result['enemies']:
            self.enemies[enemy['key']]=enemy;pix=QPixmap();raw=model.picture_for_enemy(enemy)
            if raw:pix.loadFromData(raw)
            occurrences[enemy['name']]+=1
            label=enemy['name']+(f"\n同名记录{occurrences[enemy['name']]}"if counts[enemy['name']]>1 else'')
            item=QListWidgetItem(QIcon(pix),label);item.setData(Qt.ItemDataRole.UserRole,enemy['key']);item.setToolTip('关卡资料候选，不代表实际出现数量；未取得图片时不借用同名图片。');self.lists[enemy['tier']].addItem(item)
    def select_enemy(self,*_):
        widget=self.tabs.currentWidget();item=widget.currentItem();enemy=self.enemies.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        text=model.enemy_text(enemy)if enemy else'请选择敌人；同名的不同引用分别保留，不相加为实际数量。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
    def open_stage(self):
        self.refresh()
        if self.identity is None or self.result is None:return
        if self.dialog is None:
            from .player_map_reader import make_reader
            self.dialog=make_reader('battle',{'id':self.identity,'title':self.result['name']},self,historical=self.historical_reading,config=self.run.state.get('config',{}))
        elif self.dialog.panel.refresh_reference()is False:
            self.dialog.close();self.dialog=None
        if self.dialog is None:return
        self.dialog.show();self.dialog.raise_()
    def closeEvent(self,event):
        if self.dialog is not None:self.dialog.close()
        super().closeEvent(event)
    def hideEvent(self,event):
        if self.dialog is not None:self.dialog.close()
        super().hideEvent(event)

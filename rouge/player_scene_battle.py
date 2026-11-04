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
    def __init__(self,run,parent=None,*,defer_initial_refresh=False):
        super().__init__(parent);self.run=run;self.identity=None;self.result=None;self.enemies={};self.context_key=None;self.dialog=None
        body=QVBoxLayout(self);self.notice=QLabel('最近读取的关卡 · 选择对应版本查看');self.notice.setWordWrap(True);body.addWidget(self.notice)
        self.stages=QComboBox();self.stages.currentIndexChanged.connect(self.select_stage);body.addWidget(self.stages)
        self.tabs=QTabWidget();self.lists={}
        for tier,label in [('NORMAL','普通'),('ELITE','精英'),('BOSS','领袖'),(None,'类别未确认')]:
            widget=QListWidget();widget.setIconSize(QSize(48,48));widget.setViewMode(QListWidget.ViewMode.IconMode);widget.setResizeMode(QListWidget.ResizeMode.Adjust);widget.setGridSize(QSize(125,100));widget.setWordWrap(True);widget.currentItemChanged.connect(self.select_enemy);self.tabs.addTab(widget,label);self.lists[tier]=widget
        self.tabs.currentChanged.connect(self.select_enemy);body.addWidget(self.tabs,1)
        self.detail=QPlainTextEdit();self.detail.setReadOnly(True);body.addWidget(self.detail,1)
        self.open_button=QPushButton('查看地图、敌人与出怪');self.open_button.clicked.connect(self.open_stage);body.addWidget(self.open_button)
        self.note_button=QPushButton('记录关卡笔记');body.addWidget(self.note_button);self.note_button.clicked.connect(self.write_note)
        if not defer_initial_refresh:self.refresh()
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
        if not rows:self.notice.setText('暂无关卡资料，可从地图节点打开作战预览。')
        else:self.notice.setText('最近读取：'+str(content.get('title')or'已记录关卡')+' · 选择版本查看')
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
            item=QListWidgetItem(QIcon(pix),label);item.setData(Qt.ItemDataRole.UserRole,enemy['key']);item.setToolTip('关卡敌人资料；出场条件见出怪记录。');self.lists[enemy['tier']].addItem(item)
    def select_enemy(self,*_):
        widget=self.tabs.currentWidget();item=widget.currentItem();enemy=self.enemies.get(item.data(Qt.ItemDataRole.UserRole))if item else None
        text=model.enemy_text(enemy)if enemy else'选择敌人查看预计面板和机制。'
        if self.detail.toPlainText()!=text:self.detail.setPlainText(text)
    def open_stage(self):
        self.refresh()
        if self.identity is None or self.result is None:return
        from .player_reference_window import ReferenceWindow
        host=self.window()
        if isinstance(host,ReferenceWindow):
            from .player_map_reader import make_reader
            def context():
                self.refresh()
                return (self.run.state.get('id'),self.context_key,self.identity)if self.result is not None else None
            return host.open_reference(self,'recent-stage',context,
                lambda owner:make_reader('battle',{'id':self.identity,'title':self.result['name']},self,
                    historical=self.historical_reading,config=self.run.state.get('config',{}),page_owner=owner),
                verify=lambda panel:panel.set_context({}if self.historical_reading else self.run.state.get('config',{})) is not False)
        if self.dialog is None:
            from .player_map_reader import make_reader
            self.dialog=make_reader('battle',{'id':self.identity,'title':self.result['name']},self,historical=self.historical_reading,config=self.run.state.get('config',{}))
        elif self.dialog.panel.refresh_reference()is False:
            self.dialog.close();self.dialog=None
        if self.dialog is None:return
        self.dialog.show();self.dialog.raise_()
    def _close_readers(self):
        if self.dialog is not None:self.dialog.close()
    def closeEvent(self,event):
        self._close_readers()
        super().closeEvent(event)
    def hideEvent(self,event):
        if not self.window().property('playerSuspended'):self._close_readers()
        super().hideEvent(event)

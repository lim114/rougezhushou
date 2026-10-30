"""Video-style floating toolbar, with persistent read-only panels opened on demand."""
from PySide6.QtCore import Qt,QPoint
from PySide6.QtGui import QRegion
from PySide6.QtWidgets import QDialog,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QCheckBox,QToolButton,QApplication,QPlainTextEdit,QComboBox,QTabWidget,QScrollArea
from .player_overview import overview_facts
from .player_context import recent_content

class ToolPopover(QDialog):
    def __init__(self,title,content,parent,*,on_show=None):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint);self.setWindowTitle(title);self.setSizeGripEnabled(True);self.drag_origin=None
        self.on_show=on_show
        body=QVBoxLayout(self);bar=QHBoxLayout();bar.addWidget(QLabel(title),1);close=QPushButton('×');close.setObjectName('popoverCloseButton');close.setFixedWidth(30);close.clicked.connect(self.close);bar.addWidget(close);body.addLayout(bar);body.addWidget(content,1)

    def showEvent(self,event):
        super().showEvent(event)
        # Also covers hotkey/game-binding restoration, which bypasses open_*.
        if self.on_show is not None:self.on_show()

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton and event.position().y()<42:self.drag_origin=event.globalPosition().toPoint()-self.pos();event.accept()
    def mouseMoveEvent(self,event):
        if self.drag_origin is not None and event.buttons()&Qt.MouseButton.LeftButton:self.move(event.globalPosition().toPoint()-self.drag_origin);event.accept()
    def mouseReleaseEvent(self,event):self.drag_origin=None;super().mouseReleaseEvent(event)

from .player_map import MapPanel

class CompactAssistant(QDialog):
    def __init__(self,owner,hotkey_path=None):
        super().__init__(owner,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.owner=owner;self.active_popup=None;self.inventory_popup=None;self.map_popup=None;self.setWindowTitle('黑流树海助手')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True);self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating,True)
        self.buttons={};self.tool_buttons=[];self._dock_positioned=False
        overview=QWidget();layout=QVBoxLayout(overview);self.context=QLabel();self.context.setWordWrap(True);layout.addWidget(self.context);grid=QGridLayout();self.cards={}
        for i,name in enumerate(overview_facts(owner.run.state)):
            value=QLabel();value.setWordWrap(True);self.cards[name]=value;grid.addWidget(QLabel(name),i//2*2,i%2);grid.addWidget(value,i//2*2+1,i%2)
        layout.addLayout(grid);self.scene_button=QPushButton('最近节点 · 事件、关卡与敌人资料');self.scene_button.clicked.connect(self.open_scene_battle);layout.addWidget(self.scene_button);self.scene_popup=None;self.exchange_popup=None;self.replay_popup=None;self.replay_button=QPushButton('查看本局读取记录');self.replay_button.clicked.connect(self.open_replay);layout.addWidget(self.replay_button);self.team_popup=None;self.team_button=QPushButton('本局队伍 · 职业与培养');self.team_button.clicked.connect(self.open_team);layout.addWidget(self.team_button);self.overview_popup=ToolPopover('本局概况',overview,self,on_show=self.refresh);self.overview_popup.resize(460,350)
        settings=QWidget();layout=QVBoxLayout(settings);self.pin=QCheckBox('保持置顶');self.pin.setChecked(True);self.pin.toggled.connect(self.set_pinned);layout.addWidget(self.pin)
        self.expand=QPushButton('展开完整助手');self.expand.clicked.connect(self.open_full);layout.addWidget(self.expand)
        from .player_hotkey import GlobalHotkey,load_preferences,DEFAULT
        self.hotkey_path=hotkey_path;self.hidden_windows=None;self.hotkey=GlobalHotkey(self)
        self.hotkey.triggered.connect(self.toggle_visibility)
        self.hotkey_preferences,load_warning=load_preferences(hotkey_path)if hotkey_path is not None else({'enabled':False,'shortcut':DEFAULT,'allow_single':False},'')
        self.hotkey_enabled=QCheckBox('启用全局呼出 / 收起');self.hotkey_enabled.setChecked(self.hotkey_preferences['enabled']);layout.addWidget(self.hotkey_enabled)
        self.hotkey_keys=QComboBox();self.hotkey_keys.setEditable(True);self.hotkey_keys.addItems([DEFAULT,'Ctrl+Shift+F10','Alt+Space','Tab']);self.hotkey_keys.setCurrentText(self.hotkey_preferences['shortcut']);layout.addWidget(self.hotkey_keys)
        self.hotkey_single=QCheckBox('允许占用单独按键（例如 Tab）');self.hotkey_single.setChecked(self.hotkey_preferences['allow_single']);layout.addWidget(self.hotkey_single)
        warning=QLabel('单独 Tab 会影响其他程序的切换或游戏按键。\n建议使用 Ctrl+Alt+Space；收起不会关闭笔记或清空本局。');warning.setWordWrap(True);layout.addWidget(warning)
        self.hotkey_apply=QPushButton('应用快捷键');self.hotkey_apply.clicked.connect(self.apply_hotkey);layout.addWidget(self.hotkey_apply)
        self.hotkey_status=QLabel();self.hotkey_status.setWordWrap(True);layout.addWidget(self.hotkey_status)
        self.hide_button=QPushButton('收起助手（用快捷键恢复）');self.hide_button.clicked.connect(self.toggle_visibility);layout.addWidget(self.hide_button)
        ok,message=self.hotkey.configure(**self.hotkey_preferences);self.hotkey_status.setText((load_warning+'\n'if load_warning else'')+message);self.hide_button.setEnabled(ok and self.hotkey.binding is not None)
        self.binding_enabled=QCheckBox('玩家小窗跟随明日方舟窗口');self.binding_enabled.setChecked(True);layout.addWidget(self.binding_enabled)
        self.game_hover_enabled=QCheckBox('在游戏藏品上停留5秒后读取资料');self.game_hover_enabled.setChecked(True);layout.addWidget(self.game_hover_enabled)
        self.binding_status=QLabel('尚未找到游戏；可先独立查阅。');self.binding_status.setWordWrap(True);layout.addWidget(self.binding_status)
        public=QPushButton('路标资料：藏品池与节点事件');public.clicked.connect(self.open_archive);layout.addWidget(public)
        stat=QPushButton('节点历史统计');stat.clicked.connect(lambda:self.open_owner_dialog(owner.open_public_statistics,'public_statistics'));layout.addWidget(stat)
        self.note_library=None;self.note_library_button=QPushButton('查找本机场景笔记');self.note_library_button.clicked.connect(self.open_note_library);layout.addWidget(self.note_library_button)
        close=QPushButton('退出助手');close.clicked.connect(self.exit_application);layout.addWidget(close)
        self.settings_scroll=QScrollArea();self.settings_scroll.setWidgetResizable(True);self.settings_scroll.setWidget(settings);self.settings_popup=ToolPopover('工具设置',self.settings_scroll,self,on_show=self.refresh);self.settings_popup.resize(420,570)
        self.recent_notes_popup=None
        actions=[('本局概况','overview',lambda:self.present(self.overview_popup)),('地图与节点','map',self.open_map),('本局藏品','bag',self.open_inventory),('场景笔记','note',self.open_recent_notes),('干员与技能','calc',self.open_operators),('聊天分析','chat',self.open_chat),('工具设置','settings',lambda:self.present(self.settings_popup))]
        from .player_toolbar import DockButton,ORDER,NAMES
        by_name={name:(glyph,callback)for name,glyph,callback in actions}
        for name,label in zip(ORDER,NAMES):
            glyph,callback=by_name[name];button=DockButton(label,glyph,self)
            button.setAccessibleName(name);button.clicked.connect(callback)
            button.geometryChanged.connect(self._layout_dock);button.hoverChanged.connect(self._hover_tool);button.dragged.connect(self._drag_dock)
            self.buttons[name]=button;self.tool_buttons.append(button)
        # Retain programmatic shortcut compatibility; statistics lives in the settings menu.
        self.buttons['节点统计']=stat
        self._layout_dock();self.set_pinned(True);self.refresh()
        from .player_game_binding import GameWindowBinding
        self.game_binding=GameWindowBinding(self,owner);self.binding_enabled.toggled.connect(self.game_binding.set_enabled)
        from .player_game_hover import GameHover
        self.game_hover=GameHover(self,owner);self.game_hover_enabled.toggled.connect(self.game_hover.set_enabled)
        from .player_game_map import GameMapOverlay
        self.game_overlay=GameMapOverlay(self,owner);self.map_overlay_enabled=QCheckBox('游戏地图显示所选节点类型（只读）');layout.addWidget(self.map_overlay_enabled);self.map_overlay_enabled.toggled.connect(self.game_overlay.set_enabled)
    def _layout_dock(self):
        from .player_toolbar import DIAMETER,GAP
        right=self.x()+self.width();x=2;region=QRegion()
        for button in self.tool_buttons:
            button.move(x,2)
            # Leave antialiased edge pixels intact; only the spaces between tools
            # are removed from the native input region.
            region=region.united(QRegion(button.geometry()));x+=button.width()+GAP
        self.setFixedSize(x-GAP+2,DIAMETER+4);self.setMask(region)
        if self._dock_positioned:self._move_dock(QPoint(right-self.width(),self.y()))
    def _move_dock(self,position):
        screen=QApplication.screenAt(position+self.rect().center())or self.screen();area=screen.availableGeometry()
        self.move(max(area.left(),min(position.x(),area.right()-self.width()+1)),max(area.top(),min(position.y(),area.bottom()-self.height()+1)))
    def _drag_dock(self,delta):self._move_dock(self.pos()+delta)
    def _hover_tool(self,button):
        for item in self.tool_buttons:item.set_expanded(item is button)
    def showEvent(self,event):
        super().showEvent(event)
        if not self._dock_positioned:
            area=self.screen().availableGeometry();self._dock_positioned=True
            self._move_dock(QPoint(area.right()-self.width()-15,area.bottom()-self.height()-11))
    def hideEvent(self,event):
        for button in self.tool_buttons:button.set_expanded(False,animate=False)
        super().hideEvent(event)
    def apply_hotkey(self):
        from .player_hotkey import parse_shortcut,save_preferences
        try:
            canonical,_,_=parse_shortcut(self.hotkey_keys.currentText(),self.hotkey_single.isChecked())
        except ValueError as error:self.hotkey_status.setText(str(error));return
        desired={'enabled':self.hotkey_enabled.isChecked(),'shortcut':canonical,'allow_single':self.hotkey_single.isChecked()}
        ok,message=self.hotkey.configure(**desired)
        if ok:
            self.hotkey_preferences=desired;self.hotkey_keys.setCurrentText(canonical)
            try:
                if self.hotkey_path is not None:save_preferences(self.hotkey_path,desired)
            except OSError as error:message+='\n'+str(error)+' 本次仍可用，重启后不会保留。'
        self.hotkey_status.setText(message);self.hide_button.setEnabled(self.hotkey.binding is not None)
    def toggle_visibility(self):
        if self.owner.closing:return
        app=QApplication.instance()
        if app.activeModalWidget()is not None:return
        if self.hidden_windows is None:
            self.game_hover.invalidate()
            self.game_binding.suspended=[]
            if self.map_popup is not None:
                self.map_popup.panel.hover_timer.stop();self.map_popup.panel.leave_timer.stop()
            self.hidden_windows=[]
            for widget in app.topLevelWidgets():
                parent=widget
                while parent is not None and parent is not self.owner:parent=parent.parentWidget()
                if parent is self.owner and widget.isVisible():self.hidden_windows.append(widget)
            if not self.hidden_windows:self.hidden_windows=None;self.show();self.raise_();return
            for widget in self.hidden_windows:widget.hide()
        else:
            from shiboken6 import isValid
            restore=self.hidden_windows;self.hidden_windows=None
            for widget in restore:
                if isValid(widget):widget.show();widget.raise_()
            self.show();self.raise_()
    def set_pinned(self,value):
        visible=self.isVisible();self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,value)
        if visible:self.show()
    def present(self,popup):
        if self.active_popup is not None and self.active_popup is not popup and self.active_popup.isVisible():
            if not self.active_popup.close():self.active_popup.raise_();return False
        self.active_popup=popup;popup.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,self.pin.isChecked())
        if popup.isVisible():self.refresh()
        popup.show()
        screen=self.screen().availableGeometry();size=popup.size();x=max(screen.left(),min(self.x(),screen.right()-size.width()+1));y=self.y()-size.height()-8
        if y<screen.top():y=min(self.y()+self.height()+8,screen.bottom()-size.height()+1)
        popup.move(x,max(screen.top(),y));popup.raise_();return True
    def refresh(self):
        title=recent_content(self.owner.run.state);self.context.setText('最近读取：'+title if title else'本局信息 · 等待读取节点详情')
        for key,value in overview_facts(self.owner.run.state).items():self.cards[key].setText(value)
        self.buttons['场景笔记'].setEnabled(True);self.setToolTip(self.context.text())
        if self.recent_notes_popup and self.recent_notes_popup.isVisible():self.recent_notes_popup.panel.refresh()
        if self.inventory_popup and self.inventory_popup.isVisible():
            self.inventory_popup.panel.refresh();self.inventory_popup.parts.refresh();self.inventory_popup.tools.refresh();self.inventory_popup.parts.refresh_exchange();self.inventory_popup.shop.refresh()
        for popup in (self.map_popup,self.scene_popup,self.team_popup,self.replay_popup):
            if popup and popup.isVisible():popup.panel.refresh()
        if self.exchange_popup and self.exchange_popup.isVisible():
            source=self.inventory_popup.panel;source.reload_sources()
            self.exchange_popup.panel.refresh_source(source.source_index.data if source.source_index else None,source.source_signature)
    def open_exchange(self,version,identity):
        if self.inventory_popup is None:self.open_inventory()
        source=self.inventory_popup.panel;source.reload_sources()
        if self.exchange_popup is None:
            from .player_exchange_view import ExchangePanel
            panel=ExchangePanel();panel.openPool.connect(lambda version,identity:self.open_owner_dialog(lambda:self.owner.open_public_pool_reference(version,identity),'public_archive'))
            self.exchange_popup=ToolPopover('失与得 · 提供物与换入候选',panel,self,on_show=self.refresh);self.exchange_popup.panel=panel;self.exchange_popup.resize(830,670)
        self.exchange_popup.panel.bind(source.source_index.data if source.source_index else None,version,identity,source.source_signature)
        return self.present(self.exchange_popup)
    def open_replay(self):
        if self.replay_popup is None:
            from .player_replay import ReplayPanel
            panel=ReplayPanel(self.owner.run,source_panel=self.owner.inventory_panel)
            from .player_reference_notes import open_note
            panel.noteRequested.connect(lambda content:open_note(self.owner,content));self.replay_popup=ToolPopover('本局已读记录',panel,self,on_show=self.refresh);self.replay_popup.panel=panel;self.replay_popup.resize(900,720)
        return self.present(self.replay_popup)
    def open_team(self):
        if self.team_popup is None:
            from .player_team import TeamPanel
            panel=TeamPanel(self.owner.run)
            panel.openOperator.connect(lambda identity:(self.owner.select_operator(identity),self.open_operators()))
            self.team_popup=ToolPopover('本局队伍 · 已招募干员',panel,self,on_show=self.refresh);self.team_popup.panel=panel;self.team_popup.resize(830,690)
        return self.present(self.team_popup)
    def open_note_library(self):
        if self.note_library is None:
            from .player_note_library import NoteLibraryDialog
            self.note_library=NoteLibraryDialog(self.owner.player_notes.store.folder,self)
            self.note_library.openContext.connect(self.open_saved_note)
            from .player_reference_notes import open_reference
            self.note_library.openReference.connect(lambda content:open_reference(self.owner,content))
        self.note_library.refresh();return self.present(self.note_library)
    def open_saved_note(self,content):
        notes=self.owner.player_notes
        if not notes.set_context(content):notes.show();notes.raise_();return False
        return self.present(notes)
    def open_recent_notes(self):
        if self.recent_notes_popup is None:
            from .player_recent_notes import RecentNotesPanel,NOTE_STYLE
            panel=RecentNotesPanel(self.owner.run,self.owner.player_notes.store)
            panel.editRequested.connect(self.open_saved_note)
            self.recent_notes_popup=ToolPopover('备忘录',panel,self,on_show=self.refresh);self.recent_notes_popup.panel=panel
            self.recent_notes_popup.setObjectName('sceneNotesWindow');self.recent_notes_popup.setStyleSheet(NOTE_STYLE)
            self.recent_notes_popup.resize(900,480)
        self.recent_notes_popup.panel.refresh(force=True);return self.present(self.recent_notes_popup)
    def open_scene_battle(self):
        if self.scene_popup is None:
            from .player_recent_scene import RecentScenePanel
            from .player_reference_notes import open_note
            panel=RecentScenePanel(self.owner.run);panel.noteRequested.connect(lambda content:open_note(self.owner,content));self.scene_popup=ToolPopover('最近节点资料',panel,self,on_show=self.refresh);self.scene_popup.panel=panel;self.scene_popup.resize(760,600)
        return self.present(self.scene_popup)
    def open_inventory(self):
        if self.inventory_popup is None:
            from .player_inventory import InventoryPanel
            panel=InventoryPanel(self.owner.run,self.owner.inventory_panel.public_cache);panel.openReference.connect(lambda i:(self.owner.open_item_reference(i),self.open_full()))
            panel.openPoolReference.connect(lambda version,identity:self.open_owner_dialog(lambda:self.owner.open_public_pool_reference(version,identity),'public_archive'))
            from .player_parts import PartsPanel
            from .player_tools import ToolsPanel
            pages=QTabWidget();parts=PartsPanel(self.owner.run);tools=ToolsPanel(self.owner.run)
            from .player_exchange_view import related_exchanges
            panel.openExchangeReference.connect(self.open_exchange)
            parts.exchange_lookup=lambda identity:bool(panel.source_index and related_exchanges(panel.source_index.data,panel.version.currentData(),identity))
            parts.exchangeRequested.connect(lambda identity:self.open_exchange(panel.version.currentData(),identity))
            pages.addTab(panel,'收藏品');pages.addTab(tools,'战术道具');pages.addTab(parts,'零件箱资料')
            from .player_shop_memory import ShopMemoryPanel
            shop=ShopMemoryPanel(self.owner.run,panel);pages.addTab(shop,'商店记录')
            self.inventory_popup=ToolPopover('收藏品、战术道具与零件',pages,self,on_show=self.refresh)
            from .player_catalog_grid import INVENTORY_STYLE
            self.inventory_popup.setObjectName('inventoryWindow');self.inventory_popup.setStyleSheet(INVENTORY_STYLE)
            self.inventory_popup.panel=panel;self.inventory_popup.pages=pages;self.inventory_popup.parts=parts;self.inventory_popup.tools=tools;self.inventory_popup.shop=shop;self.inventory_popup.resize(840,650)
        return self.present(self.inventory_popup)
    def open_map(self):
        if self.map_popup is None:
            panel=MapPanel(self.owner);self.map_popup=ToolPopover('探索地图与节点',panel,self,on_show=self.refresh);self.map_popup.panel=panel;self.map_popup.resize(1100,650);self.map_popup.setObjectName('videoMapWindow');self.map_popup.setStyleSheet('#videoMapWindow{background:#f5f5f7;border:1px solid #bbc1c5;border-radius:12px;} #videoMapWindow QLabel{color:#25332f;} #videoMapWindow QPushButton,#videoMapWindow QComboBox{color:#263630;background:#e8ebea;border:1px solid #bbc6c1;border-radius:7px;padding:5px;} #videoMapWindow QTabBar{background:#f5f5f7;border:0;} #videoMapWindow QTabBar::tab{color:#35403c;background:#e4e7e6;border:0;border-radius:10px;padding:6px 12px;} #videoMapWindow QTabBar::tab:selected{background:#2c3533;color:white;} #videoMapWindow QPlainTextEdit,#videoMapWindow QTreeWidget{color:#28332e;background:#fff;border:1px solid #d2d9d5;}')
        return self.present(self.map_popup)
    def open_archive(self):return self.open_owner_dialog(self.owner.open_public_archive,'public_archive')
    def open_owner_dialog(self,callback,name):
        if self.active_popup is not None and self.active_popup.isVisible()and not self.active_popup.close():
            self.active_popup.raise_();return False
        callback();popup=getattr(self.owner,name,None)
        if popup is not None:return self.present(popup)
        return False
    def open_full(self,page=None):
        if page is not None and not isinstance(page,bool):self.owner.centralWidget().setCurrentWidget(page)
        self.owner.show();self.owner.raise_();self.owner.activateWindow()
    def open_operators(self):
        ws=self.owner.centralWidget();ws.show_group('干员计算');self.open_full(ws.currentWidget())
    def open_chat(self):
        ws=self.owner.centralWidget();ws.show_group('聊天');self.open_full(ws.currentWidget())
    def exit_application(self):
        self.owner.close()
        if self.owner.closing:QApplication.instance().quit()
    def closeEvent(self,event):
        if self.owner.closing:self.hotkey.close();self.game_binding.close();self.game_hover.close();self.game_overlay.close()
        if not self.owner.closing:self.open_full()
        for popup in (self.active_popup,self.inventory_popup,self.map_popup,self.overview_popup,self.settings_popup):
            if popup is not None:popup.close()
        event.accept()

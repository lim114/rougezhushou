"""Video-style floating toolbar, with persistent read-only panels opened on demand."""
from PySide6.QtCore import Qt,QPoint,Signal
from PySide6.QtGui import QRegion
from PySide6.QtWidgets import QDialog,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QCheckBox,QToolButton,QApplication,QPlainTextEdit,QComboBox,QTabWidget,QTabBar,QScrollArea
from .player_overview import overview_facts
from .player_context import recent_content

from .player_window_frame import PlayerDialog

class ToolPopover(PlayerDialog):
    def __init__(self,title,content,parent,*,on_show=None,theme='dark',extra_style='',object_name='playerPopover'):
        super().__init__(parent);self.setWindowTitle(title)
        from .player_theme import apply_theme
        self.setObjectName(object_name);apply_theme(self,theme,extra=extra_style)
        self.on_show=on_show
        body=QVBoxLayout(self);self.header_bar=self.titleBar.hBoxLayout;self.title_label=self.titleBar.titleLabel;body.addWidget(content,1)

    def showEvent(self,event):
        super().showEvent(event)
        # Also covers hotkey/game-binding restoration, which bypasses open_*.
        if self.on_show is not None:self.on_show()

from .player_map import MapPanel
from .player_reference_window import ReferenceWindow, ToolPage, NotesPage

class CompactAssistant(QDialog):
    resources_refreshed = Signal()

    def __init__(self,owner,hotkey_path=None):
        super().__init__(owner,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.owner=owner;self.active_popup=None;self.inventory_popup=None;self.map_popup=None;self.setWindowTitle('黑流树海助手')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True);self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating,True)
        self.buttons={};self.tool_buttons=[];self._dock_positioned=False;self.archive_popup=None;self.statistics_popup=None;self.workspace_popup=None
        self.reference_window=ReferenceWindow(self)
        self.overlay_web_pages={}
        overview=QWidget();layout=QVBoxLayout(overview);self.context=QLabel();self.context.setWordWrap(True);layout.addWidget(self.context);grid=QGridLayout();self.cards={}
        for i,name in enumerate(overview_facts(owner.run.state)):
            value=QLabel();value.setWordWrap(True);self.cards[name]=value;grid.addWidget(QLabel(name),i//2*2,i%2);grid.addWidget(value,i//2*2+1,i%2)
        layout.addLayout(grid);self.scene_button=QPushButton('最近节点 · 事件、关卡与敌人资料');self.scene_button.clicked.connect(self.open_scene_battle);layout.addWidget(self.scene_button);self.scene_popup=None;self.exchange_popup=None;self.replay_popup=None;self.replay_button=QPushButton('查看本局读取记录');self.replay_button.clicked.connect(self.open_replay);layout.addWidget(self.replay_button);self.team_popup=None;self.team_button=QPushButton('本局队伍 · 职业与培养');self.team_button.clicked.connect(self.open_team);layout.addWidget(self.team_button);self.overview_popup=ToolPage('本局概况',overview,self,on_show=self.refresh);self.overview_popup.resize(460,350)
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
        stat=QPushButton('节点历史统计');stat.clicked.connect(self.open_statistics);layout.addWidget(stat)
        self.note_library=None;self.note_library_page=None;self.note_library_button=QPushButton('查找本机场景笔记');self.note_library_button.clicked.connect(self.open_note_library);layout.addWidget(self.note_library_button)
        close=QPushButton('退出助手');close.clicked.connect(self.exit_application);layout.addWidget(close)
        self.settings_scroll=QScrollArea();self.settings_scroll.setWidgetResizable(True);self.settings_scroll.setWidget(settings);self.settings_popup=ToolPage('工具设置',self.settings_scroll,self,on_show=self.refresh);self.settings_popup.resize(420,570)
        self.recent_notes_popup=None
        actions=[('本局概况','overview',lambda:self.present(self.overview_popup)),('地图与节点','map',self.open_map),('本局藏品','bag',self.open_inventory),('场景笔记','note',self.open_recent_notes),('干员与技能','calc',self.open_operators),('聊天分析','chat',self.open_chat),('工具设置','settings',lambda:self.present(self.settings_popup))]
        from .player_toolbar import DockButton,ORDER,NAMES
        by_name={name:(glyph,callback)for name,glyph,callback in actions}
        for name,label in zip(ORDER,NAMES):
            glyph,callback=by_name[name];button=DockButton(label,glyph,self)
            button.setAccessibleName(name);button.clicked.connect(callback)
            button.hoverChanged.connect(self._hover_tool);button.dragged.connect(lambda delta:self._move_dock(self.pos()+delta))
            self.buttons[name]=button;self.tool_buttons.append(button)
        # Retain programmatic shortcut compatibility; statistics lives in the settings menu.
        self.buttons['节点统计']=stat
        self._layout_dock();self.set_pinned(True);self.refresh()
        from .player_game_binding import GameWindowBinding
        self.game_binding=GameWindowBinding(self,owner);self.binding_enabled.toggled.connect(self.game_binding.set_enabled)
        from .player_game_hover import GameHover
        self.game_hover=GameHover(self,owner);self.game_hover_enabled.toggled.connect(self.game_hover.set_enabled)
        from .player_game_map import GameMapOverlay
        from pathlib import Path
        from .player_overlay_settings import OverlayPreferences
        self.overlay_preferences=OverlayPreferences(Path(hotkey_path).with_name('player-map-overlay.json')if hotkey_path is not None else None)
        self.game_overlay=GameMapOverlay(self,owner,statistics_source=owner.node_statistics_source());self.map_overlay_enabled=QCheckBox('游戏地图显示所选节点类型（只读）');layout.addWidget(self.map_overlay_enabled)
        self.map_overlay_enabled.setChecked(self.overlay_preferences.enabled);self.game_overlay.set_enabled(self.overlay_preferences.enabled)
        self.map_overlay_enabled.setToolTip(self.overlay_preferences.warning or '自动保存开关；仅在已确认的当前游戏地图显示。')
        self.map_overlay_enabled.toggled.connect(self.set_map_overlay_enabled)
        from PySide6.QtWidgets import QSystemTrayIcon,QMenu
        self.tray=QSystemTrayIcon(self.tool_buttons[0].normal_icon,self);self.tray.setToolTip('黑流树海助手')
        self.tray_menu=QMenu(self)
        for label in ORDER:
            action=by_name[label][1]
            self.tray_menu.addAction(label).triggered.connect(lambda _checked=False,callback=action:self._open_from_tray(callback))
        self.tray_menu.addSeparator();self.tray_menu.addAction('退出助手').triggered.connect(self.exit_application)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(lambda reason:self._open_from_tray(by_name['本局概况'][1])if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()
    def set_map_overlay_enabled(self,value):
        self.game_overlay.set_enabled(value)
        warning=self.overlay_preferences.save(value)
        self.map_overlay_enabled.setToolTip(warning or '自动保存开关；仅在已确认的当前游戏地图显示。')

    def _open_from_tray(self,callback):
        if self.hidden_windows is not None:self.toggle_visibility()
        return callback()
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
        binding=getattr(self,'game_binding',None)
        if binding is not None and binding.enabled and binding.snapshot is not None and binding.snapshot['active']:
            from .player_game_binding import outside_position
            position=outside_position(binding.snapshot['logical_client'],area,self.size(),position)
            if position is None:return
        self.move(max(area.left(),min(position.x(),area.right()-self.width()+1)),max(area.top(),min(position.y(),area.bottom()-self.height()+1)))
    def _hover_tool(self,button):
        for item in self.tool_buttons:item.set_expanded(item is button)
        from PySide6.QtWidgets import QToolTip
        if button is None:QToolTip.hideText()
        else:QToolTip.showText(button.mapToGlobal(QPoint(0,button.height()+8)),button.label,button)
    def showEvent(self,event):
        super().showEvent(event)
        if not self._dock_positioned:
            area=self.screen().availableGeometry();self._dock_positioned=True
            self._move_dock(QPoint(area.right()-self.width()-15,area.bottom()-self.height()-11))
    def hideEvent(self,event):
        from PySide6.QtWidgets import QToolTip
        QToolTip.hideText()
        for button in self.tool_buttons:button.set_expanded(False,animate=False)
        super().hideEvent(event)
    def apply_hotkey(self):
        from .player_hotkey import save_preferences
        desired={'enabled':self.hotkey_enabled.isChecked(),'shortcut':self.hotkey_keys.currentText(),'allow_single':self.hotkey_single.isChecked()}
        try:
            ok,message=self.hotkey.configure(**desired)
        except ValueError as error:self.hotkey_status.setText(str(error));return
        if ok:
            desired['shortcut']=self.hotkey.shortcut
            self.hotkey_preferences=desired;self.hotkey_keys.setCurrentText(self.hotkey.shortcut)
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
            if self.map_popup is not None:
                self.map_popup.panel.hover_timer.stop();self.map_popup.panel.leave_timer.stop()
            from .player_game_binding import parent_chain
            found=[];managed=set(self.game_binding.surfaces())
            for widget in app.topLevelWidgets():
                chain=parent_chain(widget)
                if self.owner in chain and widget.isVisible()and widget not in managed:found.append((len(chain),widget))
            self.hidden_windows=[widget for _,widget in sorted(found,key=lambda row:row[0])]
            for widget in self.hidden_windows:widget.setProperty('playerSuspended',True)
            self.game_binding.apply(self.game_binding.snapshot)
            for widget in self.hidden_windows:widget.hide()
        else:
            from shiboken6 import isValid
            from .player_game_binding import retained_window
            while self.hidden_windows:
                widget=self.hidden_windows.pop(0)
                if isValid(widget):
                    if retained_window(widget):widget.show();widget.raise_()
                    widget.setProperty('playerSuspended',False)
            self.hidden_windows=None;self.game_binding.apply(self.game_binding.snapshot)
    def set_pinned(self,value):
        visible=self.isVisible();self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,value)
        if visible:self.show()
    def present(self,popup):
        host=self.reference_window;visible=host.isVisible();page_visible=popup.isVisible()
        if bool(host.windowFlags()&Qt.WindowType.WindowStaysOnTopHint)!=self.pin.isChecked():host.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,self.pin.isChecked())
        if not host.present(popup):return False
        self.active_popup=popup
        if page_visible and popup.on_show is not None:self.refresh()
        if not visible:
            screen=self.screen().availableGeometry();size=host.size();x=max(screen.left(),min(self.x(),screen.right()-size.width()+1));y=self.y()-size.height()-8
            if y<screen.top():y=min(self.y()+self.height()+8,screen.bottom()-size.height()+1)
            snapshot=self.game_binding.snapshot if self.game_binding.enabled else None
            if snapshot and snapshot['active']:
                from .player_game_binding import outside_position
                client=snapshot['logical_client'];position=outside_position(client,screen,size)
                if position is None:
                    x=screen.right()-size.width()+1 if screen.right()-client.right()>=client.left()-screen.left()else screen.left()
                    y=max(screen.top(),min(client.top(),screen.bottom()-size.height()+1));position=QPoint(x,y)
                host.move(position)
            else:host.move(x,max(screen.top(),y))
        return True
    def visible_current_resource_strips(self):
        strips = []
        if self.inventory_popup and self.inventory_popup.resources.isVisible():
            strips.append(self.inventory_popup.resources)
        if self.map_popup:
            panel = self.map_popup.panel
            if panel.resources.isVisible() and not (panel.view.graph and panel.view.historical):
                strips.append(panel.resources)
        return strips

    def update_current_hud(self, resources):
        from .player_resource_facts import hud_rows
        rows = {row['key']: row for row in hud_rows(resources)}
        for strip in self.visible_current_resource_strips():
            strip.set_rows([rows.get(row['key'], row) for row in strip.rows])

    def refresh(self):
        title=recent_content(self.owner.run.state);self.context.setText('最近读取：'+title if title else'本局信息 · 等待读取节点详情')
        from .player_resource_facts import inventory_summary, resource_rows
        state = self.owner.run.state
        inventory = inventory_summary(state)
        for key,value in overview_facts(state, inventory=inventory).items():self.cards[key].setText(value)
        self.buttons['场景笔记'].setEnabled(True);self.setToolTip(self.context.text())
        if self.recent_notes_popup and self.recent_notes_popup.isVisible():self.recent_notes_popup.panel.refresh()
        if self.inventory_popup and self.inventory_popup.isVisible():
            rows = resource_rows(state, inventory=inventory)
            facts = {r['key']: r for r in rows}
            popup = self.inventory_popup
            popup.resources.set_rows([r for r in rows if r['key']not in('items','parts','crew')])
            popup.navigation.setTabText(0,'收藏品 '+(''if inventory['complete']else'已读')+str(inventory['relics']))
            popup.navigation.setTabToolTip(0,facts['items']['note']);popup.navigation.setTabText(1,'道具 '+str(inventory['tools']))
            popup.navigation.setTabToolTip(1,'本局已确认持有的战术道具；不代表当前可用。')
            popup.navigation.setTabText(2,'零件箱 '+facts['parts']['value']);popup.navigation.setTabToolTip(2,facts['parts']['note']+'这是数量，不是库存成员名单。')
            popup.crew_button.setText('干员 '+facts['crew']['value']);popup.crew_button.setToolTip(facts['crew']['note'])
            self.inventory_popup.panel.refresh();self.inventory_popup.parts.refresh();self.inventory_popup.tools.refresh();self.inventory_popup.parts.refresh_exchange();self.inventory_popup.shop.refresh()
        for popup in (self.map_popup,self.scene_popup,self.team_popup,self.replay_popup):
            if popup and popup.isVisible():popup.panel.refresh()
        if self.archive_popup is not None and self.archive_popup.isVisible():self.archive_popup.panel.reload_local()
        page=self.reference_window.pages.currentWidget()
        if self.reference_window.isVisible():
            if page is not None and page.source_parent is not None:page.prepare()
            elif self.map_popup is not None and not self.map_popup.isVisible() and self.map_popup.panel.reference_popup is not None:self.map_popup.panel.refresh()
        if self.exchange_popup and self.exchange_popup.isVisible():
            source=self.inventory_popup.panel;source.reload_sources()
            self.exchange_popup.panel.refresh_source(source.source_index.data if source.source_index else None,source.source_signature)
        self.resources_refreshed.emit()

    def open_exchange(self,version,identity):
        if self.inventory_popup is None:self.open_inventory()
        source=self.inventory_popup.panel;source.reload_sources()
        if self.exchange_popup is None:
            from .player_exchange_view import ExchangePanel
            panel=ExchangePanel();panel.openPool.connect(self.open_archive_pool)
            self.exchange_popup=ToolPage('失与得 · 提供物与换入候选',panel,self,on_show=self.refresh);self.exchange_popup.panel=panel;self.exchange_popup.resize(830,670)
        self.exchange_popup.panel.bind(source.source_index.data if source.source_index else None,version,identity,source.source_signature)
        return self.present(self.exchange_popup)
    def open_replay(self):
        if self.replay_popup is None:
            from .player_replay import ReplayPanel,HISTORY_STYLE
            panel=ReplayPanel(self.owner.run,source_panel=self.owner.inventory_panel)
            from .player_reference_notes import open_note
            panel.noteRequested.connect(lambda content:open_note(self.owner,content));self.replay_popup=ToolPage('对局记录',panel,self,on_show=self.refresh,theme='light',extra_style=HISTORY_STYLE,object_name='historyWindow');self.replay_popup.panel=panel
            panel.tabs.setCurrentWidget(panel.archive_page)
            self.replay_popup.resize(640,650)
        return self.present(self.replay_popup)
    def open_team(self):
        if self.team_popup is None:
            from .player_team import TeamPanel
            panel=TeamPanel(self.owner.run)
            panel.openOperator.connect(lambda identity:(self.owner.select_operator(identity),self.open_operators()))
            self.team_popup=ToolPage('本局队伍 · 已招募干员',panel,self,on_show=self.refresh);self.team_popup.panel=panel;self.team_popup.resize(830,690)
        return self.present(self.team_popup)
    def open_note_library(self):
        if self.note_library is None:
            from .player_note_library import NoteLibraryPanel
            from .player_note_style import NOTE_STYLE
            self.note_library=NoteLibraryPanel(self.owner.player_notes.store.folder,defer_population=True)
            self.note_library_page=ToolPage('笔记目录',self.note_library,self,theme='light',extra_style=NOTE_STYLE,object_name='sceneNotesLibrary')
            self.note_library_page.panel=self.note_library;self.note_library_page.prepare=self.note_library.refresh;self.note_library_page.resize(800,430)
            refresh=QPushButton('刷新目录');refresh.setAutoDefault(False);refresh.clicked.connect(self.note_library.refresh);self.note_library_page.header_bar.addWidget(refresh)
            self.note_library.openContext.connect(lambda content:self.open_saved_note(content,allow_archived=True))
            from .player_reference_notes import open_reference
            self.note_library.openReference.connect(lambda content:open_reference(self.owner,content))
        return self.present(self.note_library_page)
    def open_saved_note(self,content,*,allow_archived=False):
        popup=self.notes_popup();ready=popup.panel.open_for_context(content,allow_archived=allow_archived)
        shown=self.present(popup)
        return ready and shown
    def notes_popup(self):
        if self.recent_notes_popup is None:
            from .player_inline_notes import InlineNotesPanel
            from .player_note_style import NOTE_STYLE
            panel=InlineNotesPanel(self.owner.run,self.owner.player_notes)
            self.recent_notes_popup=NotesPage('备忘录',panel,self,on_show=self.refresh,theme='light',extra_style=NOTE_STYLE,object_name='sceneNotesWindow');self.recent_notes_popup.panel=panel
            library=QPushButton('笔记目录');library.setAutoDefault(False);library.clicked.connect(self.open_note_library);self.recent_notes_popup.header_bar.addWidget(library)
            self.recent_notes_popup.resize(900,360)
        return self.recent_notes_popup
    def open_recent_notes(self):
        self.notes_popup()
        self.recent_notes_popup.panel.refresh(force=True);return self.present(self.recent_notes_popup)
    def open_scene_battle(self):
        if self.scene_popup is None:
            from .player_recent_scene import RecentScenePanel
            from .player_reference_notes import open_note
            panel=RecentScenePanel(self.owner.run);panel.noteRequested.connect(lambda content:open_note(self.owner,content));self.scene_popup=ToolPage('最近节点资料',panel,self,on_show=self.refresh);self.scene_popup.panel=panel;self.scene_popup.resize(760,600)
        return self.present(self.scene_popup)
    def open_inventory(self):
        if self.inventory_popup is None:
            from .player_inventory import InventoryPanel
            panel=InventoryPanel(self.owner.run,self.owner.inventory_panel.public_cache);panel.openReference.connect(self.open_inventory_reference)
            panel.openPoolReference.connect(self.open_archive_pool)
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
            navigation=QTabBar();navigation.setExpanding(False);navigation.setDrawBase(False);navigation.setUsesScrollButtons(True);navigation.setElideMode(Qt.TextElideMode.ElideNone)
            for i in range(pages.count()):navigation.addTab(pages.tabText(i))
            navigation.currentChanged.connect(pages.setCurrentIndex);pages.currentChanged.connect(navigation.setCurrentIndex);pages.tabBar().hide()
            crew_button=QPushButton('干员 未读');crew_button.clicked.connect(self.open_team)
            from .player_resource_strip import ResourceStrip
            bundle=QWidget();body=QVBoxLayout(bundle);body.setContentsMargins(0,0,0,0)
            resources=ResourceStrip(self.owner.run.state,dark=True,leading=(navigation,crew_button));resources.requested.connect(self.open_resource)
            body.addWidget(pages,1)
            from .player_catalog_grid import INVENTORY_STYLE
            self.inventory_popup=ToolPage('收藏品、战术道具与零件',bundle,self,on_show=self.refresh,theme='dark',extra_style=INVENTORY_STYLE,object_name='inventoryWindow')
            self.inventory_popup.title_label.hide();self.inventory_popup.header_bar.insertWidget(0,resources,1)
            self.inventory_popup.navigation=navigation;self.inventory_popup.crew_button=crew_button
            self.inventory_popup.finished.connect(lambda _result:panel.hover_card.dismiss())
            self.inventory_popup.resources=resources
            self.inventory_popup.panel=panel;self.inventory_popup.pages=pages;self.inventory_popup.parts=parts;self.inventory_popup.tools=tools;self.inventory_popup.shop=shop
            area=self.screen().availableGeometry();self.inventory_popup.resize(min(1200,area.width()-40),min(540,area.height()-60))
        return self.present(self.inventory_popup)
    def open_map(self):
        if self.map_popup is None:
            panel=MapPanel(self.owner,statistics_source=self.owner.node_statistics_source(),page_owner=self);self.map_popup=ToolPage('地图',panel,self,on_show=self.refresh,theme='light',object_name='videoMapWindow',extra_style='#videoMapWindow QPushButton#popoverCloseButton{color:#303139;font-size:12pt;}');self.map_popup.panel=panel;self.map_popup.resize(1200,560)
            panel.resources.requested.connect(self.open_resource)
            panel.statisticsRequested.connect(self.open_map_statistics)
        return self.present(self.map_popup)

    def open_resource(self,kind):
        if kind=='crew':return self.open_team()
        if kind in ('items','parts'):
            if self.open_inventory() is False:return False
            self.inventory_popup.pages.setCurrentWidget(self.inventory_popup.parts if kind=='parts' else self.inventory_popup.panel)
            return True
    def open_inventory_reference(self,identity):
        if not self.owner.open_item_reference(identity):return False
        self.inventory_popup.close();self.open_full();return True
    def archive_reader(self):
        if self.archive_popup is None:
            from pathlib import Path
            from .public_archive_view import ArchivePanel
            from .player_map_reader import REFERENCE_STYLE
            panel=ArchivePanel(Path(__file__).resolve().parents[1]/'.local/public-reference/archive.json')
            panel.openReference.connect(self.open_archive_event);self.owner.public_archive=panel
            self.archive_popup=ToolPage('路标资料 · 藏品池与事件',panel,self,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE);self.archive_popup.panel=panel
            self.archive_popup.prepare=panel.reload_local;self.archive_popup.resize(850,600)
        return self.archive_popup
    def open_archive(self):return self.present(self.archive_reader())
    def open_archive_pool(self,version,identity):
        page=self.archive_reader();page.panel.reload_local();selected=page.panel.select_exact_pool(version,identity)
        return self.present(page)and selected
    def open_archive_event(self,category,identity):
        from .player_reference_notes import note_for
        from .documented_readers import reader_plan,make_flow_reader
        from .player_note_reference import NoteScenePanel
        from .player_map_reader import REFERENCE_STYLE
        panel=self.archive_reader().panel;canonical=note_for(category,identity)
        if category!='scenes'or canonical is None:
            panel.status.setText('暂无对应事件原文');return False
        def context():
            current=panel.reference_context()
            return {'archive':current,'reference':canonical}if current and current['event']['id'].split(':',1)[-1]==identity and note_for(category,identity)==canonical else None
        plan=reader_plan(category,identity)
        def create(owner):
            if plan is not None:return make_flow_reader(plan,panel,page_owner=owner)
            reader=NoteScenePanel(identity)
            if reader.result is None:reader.deleteLater();return None
            page=ToolPage('事件情景 · '+canonical['title'],reader,owner,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE)
            page.panel=reader;page.resize(760,300);return page
        return self.reference_window.open_reference(panel,('archive-event',identity,plan[0]if plan else'original'),context,create)
    def statistics_reader(self):
        if self.statistics_popup is None:
            from pathlib import Path
            from .public_node_statistics_view import StatisticsPanel
            from .player_map_reader import REFERENCE_STYLE
            source=self.owner.node_statistics_source();panel=StatisticsPanel(Path(__file__).resolve().parents[1]/'.local/public-statistics/nodes.json',source=source);self.owner.public_statistics=panel
            self.statistics_popup=ToolPage('节点历史统计',panel,self,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE);self.statistics_popup.panel=panel;self.statistics_popup.prepare=panel.render;self.statistics_popup.resize(760,520)
        return self.statistics_popup
    def open_statistics(self):return self.present(self.statistics_reader())
    def open_map_statistics(self,graph,node_id):
        page=self.statistics_reader();page.panel.set_map_node(graph,node_id);return self.present(page)
    def open_full(self,page=None,*,group=None):
        workspace=self.owner.workspace
        if self.owner.diagnostic_layout:
            if page is not None and not isinstance(page,bool):workspace.setCurrentWidget(page)
            self.owner.show();self.owner.raise_();self.owner.activateWindow();return True
        if self.workspace_popup is None:
            from .player_map_reader import REFERENCE_STYLE
            self.workspace_popup=ToolPage('完整助手',self.owner.takeCentralWidget(),self,object_name='mapReferenceWindow',extra_style=REFERENCE_STYLE)
            self.workspace_popup.panel=workspace;self.workspace_popup.resize(1040,720)
            from PySide6.QtWidgets import QSizePolicy
            def fit_workspace(page):
                workspace.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Ignored if page is self.owner.chat_page else QSizePolicy.Policy.Preferred)
            workspace.activePageChanged.connect(fit_workspace);fit_workspace(workspace.currentWidget())
            back=QPushButton('上一栏目');back.setEnabled(bool(workspace._history));back.clicked.connect(workspace.go_back)
            workspace.backAvailable.connect(back.setEnabled);self.workspace_popup.header_bar.addWidget(back)
        if not self.present(self.workspace_popup):return False
        if group is not None:workspace.setCurrentWidget(workspace.groups[group])
        elif page is not None and not isinstance(page,bool):workspace.setCurrentWidget(page)
        self.owner.hide();return True
    def open_operators(self):
        return self.open_full(group='干员计算')
    def open_chat(self):
        return self.open_full(group='聊天')
    def exit_application(self):
        self.owner.close()
        if self.owner.closing:QApplication.instance().quit()
    def closeEvent(self,event):
        if self.owner.closing:self.tray.hide();self.tray_menu.close();self.hotkey.close();self.game_binding.close();self.game_hover.close();self.game_overlay.close()
        if not self.owner.closing:self.open_full()
        else:self.reference_window.close()
        event.accept()

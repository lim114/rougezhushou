"""Video-style floating toolbar, with persistent read-only panels opened on demand."""
from PySide6.QtCore import Qt,QPoint,QSize,QEvent
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtWidgets import QDialog,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QCheckBox,QToolButton,QApplication,QPlainTextEdit
from .player_overview import overview_facts
from .player_context import recent_content

PATHS={
 'overview':'<path d="M4 4h7v7H4zM15 4h5v5h-5zM4 15h5v5H4zM13 13h7v7h-7z"/>',
 'map':'<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3zM9 3v15M15 6v15"/>',
 'bag':'<path d="M5 7h14l2 13H3zM8 7V5a4 4 0 0 1 8 0v2M8 11v3M16 11v3"/>',
 'note':'<path d="M5 3h13v18H5zM8 7h7M8 11h7M8 15h4M3 7h4M3 12h4M3 17h4"/>',
 'calc':'<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h2M14 11h2M8 15h2M14 15h2M8 19h2M14 19h2"/>',
 'chat':'<path d="M3 4h18v13H9l-6 4zM7 8h10M7 12h7"/>',
 'settings':'<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="9" cy="6" r="2" fill="white"/><circle cx="15" cy="12" r="2" fill="white"/><circle cx="10" cy="18" r="2" fill="white"/>'}

def icon(name):
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" stroke="#26323b" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+PATHS[name]+'</g></svg>'
    pix=QPixmap();pix.loadFromData(svg.encode(),'SVG');return QIcon(pix)

class ToolPopover(QDialog):
    def __init__(self,title,content,parent):
        super().__init__(parent,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint);self.setWindowTitle(title);self.setSizeGripEnabled(True);self.drag_origin=None
        body=QVBoxLayout(self);bar=QHBoxLayout();bar.addWidget(QLabel(title),1);close=QPushButton('×');close.setFixedWidth(30);close.clicked.connect(self.close);bar.addWidget(close);body.addLayout(bar);body.addWidget(content,1)

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton and event.position().y()<42:self.drag_origin=event.globalPosition().toPoint()-self.pos();event.accept()
    def mouseMoveEvent(self,event):
        if self.drag_origin is not None and event.buttons()&Qt.MouseButton.LeftButton:self.move(event.globalPosition().toPoint()-self.drag_origin);event.accept()
    def mouseReleaseEvent(self,event):self.drag_origin=None;super().mouseReleaseEvent(event)

from .player_map import MapPanel

class CompactAssistant(QDialog):
    def __init__(self,owner):
        super().__init__(owner,Qt.WindowType.Tool|Qt.WindowType.FramelessWindowHint)
        self.owner=owner;self.active_popup=None;self.inventory_popup=None;self.map_popup=None;self.drag_origin=None;self.setWindowTitle('黑流树海助手')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground,True);self.setFixedSize(410,82)
        outer=QVBoxLayout(self);outer.setContentsMargins(3,3,3,3);shell=QWidget();shell.setObjectName('toolbarShell');outer.addWidget(shell)
        shell.setStyleSheet('#toolbarShell{background:#28333d;border:1px solid #68747f;border-radius:18px;} QToolButton{background:#f5f7f9;color:#26323b;border:0;border-radius:20px;} QToolButton:hover{background:#bce8ef;} QToolButton:disabled{background:#8a959c;}')
        body=QVBoxLayout(shell);body.setContentsMargins(12,7,12,5);bar=QHBoxLayout();bar.setSpacing(10);body.addLayout(bar)
        self.grip=QLabel('⠿');self.grip.setFixedWidth(12);self.grip.setToolTip('按住工具条空白处拖动');self.grip.setStyleSheet('color:#dce6ee');bar.addWidget(self.grip)
        self.buttons={};self.hover_label=QLabel('黑流树海助手 · 点图标展开');self.hover_label.setAlignment(Qt.AlignmentFlag.AlignCenter);self.hover_label.setStyleSheet('color:#e4edf3;font-size:11px;');body.addWidget(self.hover_label)
        overview=QWidget();layout=QVBoxLayout(overview);self.context=QLabel();self.context.setWordWrap(True);layout.addWidget(self.context);grid=QGridLayout();self.cards={}
        for i,name in enumerate(overview_facts(owner.run.state)):
            value=QLabel();value.setWordWrap(True);self.cards[name]=value;grid.addWidget(QLabel(name),i//2*2,i%2);grid.addWidget(value,i//2*2+1,i%2)
        layout.addLayout(grid);self.overview_popup=ToolPopover('本局概况',overview,self);self.overview_popup.resize(460,320)
        settings=QWidget();layout=QVBoxLayout(settings);self.pin=QCheckBox('保持置顶');self.pin.setChecked(True);self.pin.toggled.connect(self.set_pinned);layout.addWidget(self.pin)
        self.expand=QPushButton('展开完整助手');self.expand.clicked.connect(self.open_full);layout.addWidget(self.expand)
        public=QPushButton('路标资料：藏品池与节点事件');public.clicked.connect(self.open_archive);layout.addWidget(public)
        stat=QPushButton('节点历史统计');stat.clicked.connect(lambda:self.open_owner_dialog(owner.open_public_statistics,'public_statistics'));layout.addWidget(stat)
        close=QPushButton('退出助手');close.clicked.connect(self.exit_application);layout.addWidget(close)
        self.settings_popup=ToolPopover('工具设置',settings,self);self.settings_popup.resize(330,260)
        actions=[('本局概况','overview',lambda:self.present(self.overview_popup)),('地图与节点','map',self.open_map),('本局藏品','bag',self.open_inventory),('场景笔记','note',lambda:self.open_owner_dialog(owner.open_scene_notes,'player_notes')),('干员与技能','calc',self.open_operators),('聊天分析','chat',self.open_chat),('工具设置','settings',lambda:self.present(self.settings_popup))]
        for name,glyph,callback in actions:
            button=QToolButton();button.setIcon(icon(glyph));button.setIconSize(QSize(23,23));button.setFixedSize(40,40);button.setToolTip(name);button.setAccessibleName(name);button.clicked.connect(callback);bar.addWidget(button);self.buttons[name]=button;button.installEventFilter(self)
        # Retain programmatic shortcut compatibility; statistics lives in the settings menu.
        self.buttons['节点统计']=stat
        self.set_pinned(True);self.refresh()
    def set_pinned(self,value):
        visible=self.isVisible();self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,value)
        if visible:self.show()
    def present(self,popup):
        if self.active_popup is not None and self.active_popup is not popup and self.active_popup.isVisible():
            if not self.active_popup.close():self.active_popup.raise_();return False
        self.active_popup=popup;popup.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,self.pin.isChecked());popup.show()
        screen=self.screen().availableGeometry();size=popup.size();x=max(screen.left(),min(self.x(),screen.right()-size.width()+1));y=self.y()-size.height()-8
        if y<screen.top():y=min(self.y()+self.height()+8,screen.bottom()-size.height()+1)
        popup.move(x,max(screen.top(),y));popup.raise_();return True
    def refresh(self):
        title=recent_content(self.owner.run.state);self.context.setText('最近读取：'+title if title else'本局信息 · 等待读取节点详情')
        for key,value in overview_facts(self.owner.run.state).items():self.cards[key].setText(value)
        self.buttons['场景笔记'].setEnabled(bool(title));self.setToolTip(self.context.text())
        if self.inventory_popup:self.inventory_popup.panel.refresh()
        if self.map_popup:self.map_popup.panel.refresh()
    def open_inventory(self):
        if self.inventory_popup is None:
            from .player_inventory import InventoryPanel
            panel=InventoryPanel(self.owner.run);panel.openReference.connect(lambda i:(self.owner.open_item_reference(i),self.open_full()))
            self.inventory_popup=ToolPopover('本局藏品',panel,self);self.inventory_popup.panel=panel;self.inventory_popup.resize(680,530)
        self.inventory_popup.panel.refresh();return self.present(self.inventory_popup)
    def open_map(self):
        if self.map_popup is None:
            panel=MapPanel(self.owner);self.map_popup=ToolPopover('探索地图与节点',panel,self);self.map_popup.panel=panel;self.map_popup.resize(1100,650)
        self.map_popup.panel.refresh();return self.present(self.map_popup)
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
        ws=self.owner.centralWidget();ws.groups['干员计算'].setCurrentIndex(0);self.open_full(ws.groups['干员计算'])
    def open_chat(self):self.open_full(self.owner.centralWidget().groups['聊天'])
    def exit_application(self):
        self.owner.close()
        if self.owner.closing:QApplication.instance().quit()
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.Enter and isinstance(obj,QToolButton):self.hover_label.setText(obj.accessibleName())
        elif event.type()==QEvent.Type.Leave and isinstance(obj,QToolButton):self.hover_label.setText('黑流树海助手 · 点图标展开')
        return super().eventFilter(obj,event)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self.drag_origin=event.globalPosition().toPoint()-self.pos();event.accept()
    def mouseMoveEvent(self,event):
        if self.drag_origin is not None and event.buttons()&Qt.MouseButton.LeftButton:self.move(event.globalPosition().toPoint()-self.drag_origin);event.accept()
    def mouseReleaseEvent(self,event):self.drag_origin=None;super().mouseReleaseEvent(event)
    def closeEvent(self,event):
        if not self.owner.closing:self.open_full()
        for popup in (self.active_popup,self.inventory_popup,self.map_popup,self.overview_popup,self.settings_popup):
            if popup is not None:popup.close()
        event.accept()

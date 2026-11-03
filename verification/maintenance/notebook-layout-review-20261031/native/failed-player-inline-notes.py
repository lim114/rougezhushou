"""One notebook window, reusing the exact existing editor and local note store."""
from PySide6.QtCore import Qt,QSignalBlocker,QEvent,QTimer
from copy import deepcopy
from math import ceil
from PySide6.QtWidgets import QStackedWidget,QCheckBox,QScrollArea,QWidget,QVBoxLayout,QLabel,QPushButton,QToolButton
from .player_recent_notes import RecentNotesPanel
from .player_notes import content_key
from .player_note_preview import NotePreview
from .player_note_scopes import parents


class InlineNotesPanel(RecentNotesPanel):
    def __init__(self,run,editor,parent=None):
        self.inline_ready=False;self.note_editor=editor;self.editor_read_stamp=None;self.archived_key=None
        super().__init__(run,editor.store,parent)
        self.stack=QStackedWidget(self)
        self.layout().replaceWidget(self.preview,self.stack)
        self.stack.addWidget(self.preview)
        # One-time embedding; all entry points subsequently present this notebook.
        editor.setParent(self.stack,Qt.WindowType.Widget)
        self.stack.addWidget(editor)
        self.stack.setCurrentWidget(self.preview)
        self.parent_toggle=QCheckBox('显示上级内容');self.layout().itemAt(2).layout().insertWidget(1,self.parent_toggle)
        self.parent_area=QScrollArea();self.parent_area.setObjectName('noteAncestorScroll');self.parent_area.setWidgetResizable(True);self.parent_area.setMinimumHeight(150);self.parent_area.setMaximumHeight(200)
        self.parent_area.viewport().setObjectName('noteAncestorsViewport')
        self.parent_body=QWidget();self.parent_body.setObjectName('noteAncestors');self.parent_layout=QVBoxLayout(self.parent_body);self.parent_area.setWidget(self.parent_body)
        self.layout().insertWidget(3,self.parent_area);self.parent_area.hide();self.parent_toggle.toggled.connect(self.refresh_parents)
        self.parent_signature=None;self.parent_views=[];self.editRequested.connect(self.open_editor)
        self.inline_ready=True
        self.compact_controls()

    def compact_controls(self):
        """Reuse the editor's real actions; keep uncommon controls off the page."""
        body=self.layout();bar=body.itemAt(2).layout();editor=self.note_editor
        self.options=QWidget();options=QVBoxLayout(self.options);options.setContentsMargins(0,0,0,0)
        for widget in (self.scene,self.status,self.edit):
            body.removeWidget(widget);options.addWidget(widget)
        for widget in (self.follow,self.reload):bar.removeWidget(widget);options.addWidget(widget)
        for widget in (editor.autosave,editor.status):editor.layout().removeWidget(widget);options.addWidget(widget)
        options.addLayout(editor.layout().takeAt(editor.layout().count()-1).layout())
        editor.layout().setContentsMargins(0,0,0,0);editor.pages.tabBar().hide()
        self.save_state=QLabel();bar.addWidget(self.save_state)
        self.more=QToolButton();self.more.setText('更多操作');self.more.setCheckable(True);bar.addWidget(self.more)
        body.insertWidget(3,self.options);self.options.hide();self.more.toggled.connect(self.options.setVisible)
        self.card=QWidget();self.card.setObjectName('noteCard');card=QVBoxLayout(self.card);card.setContentsMargins(0,0,0,0);card.setSpacing(0)
        self.card_title=QLabel();self.card_title.setObjectName('noteCardTitle');self.card_title.setWordWrap(True)
        for surface in (self,self.card,self.card_title):surface.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        body.replaceWidget(self.stack,self.card);card.addWidget(self.card_title);card.addWidget(self.stack)
        self.preview.setMinimumHeight(90);body.setStretchFactor(self.card,0);body.addStretch(1)
        self.preview.setToolTip('点击正文即可编辑；离开输入区后按自动保存设置处理。也可按回车编辑。')
        self.preview.viewport().installEventFilter(self);self.preview.installEventFilter(self)
        editor.editor.installEventFilter(self)
        self.leave_timer=QTimer(self);self.leave_timer.setSingleShot(True);self.leave_timer.timeout.connect(self.leave_editor)
        self.preview.document().documentLayout().documentSizeChanged.connect(self.fit_content)
        editor.editor.textChanged.connect(self.update_save_state);editor.autosave.toggled.connect(self.update_save_state)
        self.update_save_state()

    def update_save_state(self,*_):
        editor=self.note_editor
        self.save_state.setText('未保存' if editor.dirty else '已保存' if editor.key and editor.store.path(editor.key).is_file() else '自动保存' if editor.autosave.isChecked() else '手动保存')
        self.save_state.setToolTip(editor.status.text())
        content=editor.content if self.stack.currentWidget()is editor else self.context
        self.card_title.setText(content['title'] if content else '选择一份笔记')

    def fit_content(self,*_):
        if not self.inline_ready:return
        available=max(90,self.height()-self.card.y()-self.card_title.height()-20)
        desired=220 if self.stack.currentWidget()is self.note_editor else ceil(self.preview.document().size().height())+30
        self.stack.setFixedHeight(min(available,max(90,desired)))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.fit_content()

    def eventFilter(self,watched,event):
        if watched is self.preview.viewport() and event.type()==QEvent.Type.MouseButtonPress:
            if event.button()==Qt.MouseButton.LeftButton and not self.preview.anchorAt(event.position().toPoint()) and self.context is not None:
                self.request_edit();self.note_editor.editor.setFocus(Qt.FocusReason.MouseFocusReason);return True
        if watched is self.preview and event.type()==QEvent.Type.KeyPress and event.key()in(Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_F2)and self.context is not None:
            self.request_edit();self.note_editor.editor.setFocus();return True
        if watched is self.note_editor.editor:
            if event.type()==QEvent.Type.FocusOut:self.leave_timer.start(0)
            elif event.type()==QEvent.Type.FocusIn:self.leave_timer.stop()
        return super().eventFilter(watched,event)

    def leave_editor(self):
        if self.stack.currentWidget()is self.note_editor and not self.note_editor.editor.hasFocus():
            if self.note_editor.autosave.isChecked():
                if self.finish_edit():
                    self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记');self.refresh(force=True)
                else:self.more.setChecked(True)
            self.update_save_state()

    def open_editor(self,content):
        accepted=self.note_editor.set_context(content)
        if accepted:self.editor_read_stamp=(self.key,self._stamp)if self.key==self.note_editor.key else None
        self.stack.setCurrentWidget(self.note_editor);self.note_editor.show()
        self.edit.setText('返回阅读')
        if not accepted:
            self.status.setText('另有未保存的笔记；请先在这里保存或放弃，再切换。');self.more.setChecked(True)
        self.refresh_parents()
        self.fit_content();self.update_save_state()
        return accepted

    def request_edit(self):
        if self.stack.currentWidget()is self.note_editor:
            if not self.finish_edit():return
            self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记');self.refresh(force=True)
        else:super().request_edit()

    def finish_edit(self):
        editor=self.note_editor
        if editor.dirty and editor.autosave.isChecked():editor.save_pending()
        if editor.dirty:
            self.open_editor(editor.content)
            editor.status.setText('修改尚未保存，请保存或放弃后切换或关闭。')
            return False
        return True

    def select_context(self,content):
        editing=self.inline_ready and self.stack.currentWidget()is self.note_editor
        if self.inline_ready and self.note_editor.dirty and content_key(content)!=self.note_editor.key:
            if not self.finish_edit():return False
        if content.get('kind')=='note-scope':
            # A scope comes only from the current picker, not a game observation.
            from .player_note_scopes import scope_parts
            parts=scope_parts(content,self.selector.rows)
            if parts is None:return False
            floor,node=parts
            self.selector.floor.setCurrentIndex(self.selector.floor.findData(floor));self.selector.node.setCurrentIndex(self.selector.node.findData(node));self.selector.scene.setCurrentIndex(0)
        super().select_context(content)
        if self.context!=content:self.more.setChecked(True);return False
        self.archived_key=None
        if content.get('kind')!='note-scope':
            row=next((r for r in self.selector.rows if content_key(r['context'])==content_key(content)),None)
            if row is not None:
                for combo,values in((self.selector.floor,row['floors']),(self.selector.node,row['nodes'])):
                    if combo.currentData()not in values:combo.setCurrentIndex(combo.findData(values[0]if len(values)==1 else None))
                self.selector.filter();self.selector.scene.setCurrentIndex(self.selector.scene.findData(content))
            else:self.selector.scene.setCurrentIndex(-1)
        if editing:return self.open_editor(content)
        return True

    def open_for_context(self,content,*,allow_archived=False):
        if not self.select_context(content):
            key=content_key(content)
            if not allow_archived or self.note_editor.dirty or key is None or not self.store.path(key).is_file():return False
            # Explicitly reopening a saved local file does not require the old
            # reference to remain in today's menu, and never adopts a new key.
            with QSignalBlocker(self.follow):self.follow.setChecked(False)
            self.selector.floor.setCurrentIndex(0);self.selector.node.setCurrentIndex(0);self.selector.scene.setCurrentIndex(-1)
            self.context=deepcopy(content);self._run_id=self.run.state.get('id');self.archived_key=key;self.refresh(force=True)
            return self.open_editor(content)
        if self.stack.currentWidget()is self.note_editor:return True
        return self.open_editor(content)

    def refresh(self,*,force=False):
        super().refresh(force=force)
        if not self.inline_ready:return
        editor=self.note_editor
        if self.context and self.context.get('kind')=='note-scope':
            self.scene.setText('通用笔记：'+self.context['title'])
            self.status.setText('手选范围的本机笔记；不表示本局已到达该楼层或节点，不会上传。')
        if self.key is not None and self.key==self.archived_key:
            self.scene.setText('已保存笔记：'+self.context['title']+'（原分类暂不可核对）')
            self.status.setText('仅按原身份读取、编辑本机笔记；没有改挂到当前资料或同名场景。')
        if self.stack.currentWidget()is editor:
            # Follow may advance, but a draft never changes owner. Clean editors
            # return to reading on a new scene rather than showing a stale title.
            if editor.isHidden():
                self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记')
            elif self.key==editor.key:
                stamp=(self.key,self._stamp)
                if not editor.dirty and(force or stamp!=self.editor_read_stamp):
                    if editor.set_context(self.context):self.editor_read_stamp=stamp
                if self.key!=self.archived_key and self.context.get('kind')!='note-scope':
                    self.status.setText('按所选资料或已读身份分别保存；不表示本局当前所在位置。自动保存由上方选项控制。')
            elif not editor.dirty:
                self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记')
            else:
                self.status.setText('上方是最近读取的场景；正在编辑的笔记仍对应“'+editor.content['title']+'”，未随读取转移。')
                self.edit.setEnabled(True)
                self.more.setChecked(True)
            editor.context.setVisible(self.key!=editor.key)
        self.refresh_parents()
        self.fit_content()
        if hasattr(self,'save_state'):self.update_save_state()

    def refresh_parents(self,*_):
        if not self.inline_ready:return
        visible=self.parent_toggle.isChecked();self.parent_area.setVisible(visible)
        if not visible:return
        content=self.note_editor.content if self.stack.currentWidget()is self.note_editor else self.context
        contexts=parents(content,self.selector.rows,self.selector.floor.currentData(),self.selector.node.currentData())
        values=[]
        for context in contexts:
            try:text,_=self.store.read(content_key(context));error=None
            except(OSError,ValueError,UnicodeError)as exc:
                from .player_file_messages import file_issue
                text='';error=file_issue(exc)
            values.append((context,text,error))
        signature=repr(values)
        if signature==self.parent_signature:return
        self.parent_signature=signature
        while self.parent_layout.count():
            item=self.parent_layout.takeAt(0)
            if item.widget():item.widget().hide();item.widget().deleteLater()
        self.parent_views=[]
        if not values:self.parent_layout.addWidget(QLabel('当前场景没有可唯一对应的上级范围；可手选楼层或节点后查看通用笔记。'))
        for context,text,error in values:
            title=QPushButton(context['title']);title.setToolTip('打开此范围的通用笔记');title.clicked.connect(lambda _checked=False,c=context:self.open_scope(c));self.parent_layout.addWidget(title)
            view=NotePreview();view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            view.document().documentLayout().documentSizeChanged.connect(lambda size,v=view:v.setFixedHeight(max(70,ceil(size.height())+32)))
            view.read_markdown(error or text or '此范围尚无笔记。');view.linkBlocked.connect(lambda:self.status.setText('上级笔记中的链接不会自动打开。'))
            self.parent_layout.addWidget(view);self.parent_views.append(view)

    def open_scope(self,content):
        if not self.finish_edit():return False
        return self.open_for_context(content)

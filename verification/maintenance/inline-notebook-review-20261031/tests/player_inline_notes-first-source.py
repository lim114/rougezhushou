"""One notebook window, reusing the exact existing editor and local note store."""
from PySide6.QtCore import Qt,QSignalBlocker
from PySide6.QtWidgets import QStackedWidget,QCheckBox,QScrollArea,QWidget,QVBoxLayout,QLabel,QPushButton
from .player_recent_notes import RecentNotesPanel
from .player_notes import content_key
from .player_note_preview import NotePreview
from .player_note_scopes import parents


class InlineNotesPanel(RecentNotesPanel):
    def __init__(self,run,editor,parent=None):
        self.inline_ready=False;self.note_editor=editor
        super().__init__(run,editor.store,parent)
        self.stack=QStackedWidget(self)
        self.layout().replaceWidget(self.preview,self.stack)
        self.stack.addWidget(self.preview)
        # One-time embedding; all entry points subsequently present this notebook.
        editor.setParent(self.stack,Qt.WindowType.Widget)
        self.stack.addWidget(editor)
        self.stack.setCurrentWidget(self.preview)
        self.parent_toggle=QCheckBox('显示上级内容');self.layout().itemAt(2).layout().insertWidget(1,self.parent_toggle)
        self.parent_area=QScrollArea();self.parent_area.setWidgetResizable(True);self.parent_area.setMaximumHeight(200)
        self.parent_body=QWidget();self.parent_layout=QVBoxLayout(self.parent_body);self.parent_area.setWidget(self.parent_body)
        self.layout().insertWidget(3,self.parent_area);self.parent_area.hide();self.parent_toggle.toggled.connect(self.refresh_parents)
        self.parent_signature=None;self.parent_views=[];self.editRequested.connect(self.open_editor)
        self.inline_ready=True

    def open_editor(self,content):
        accepted=self.note_editor.set_context(content)
        self.stack.setCurrentWidget(self.note_editor);self.note_editor.show()
        self.edit.setText('返回阅读')
        if not accepted:self.status.setText('另有未保存的笔记；请先在这里保存或放弃，再切换。')
        self.refresh_parents()
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
        if self.inline_ready and self.note_editor.dirty and content_key(content)!=self.note_editor.key:
            if not self.finish_edit():return
        if content.get('kind')=='note-scope':
            # A scope comes only from the current picker, not a game observation.
            from .player_note_scopes import scope_parts
            parts=scope_parts(content,self.selector.rows)
            if parts is None:return
            floor,node=parts
            self.selector.floor.setCurrentIndex(self.selector.floor.findData(floor));self.selector.node.setCurrentIndex(self.selector.node.findData(node));self.selector.scene.setCurrentIndex(0)
        super().select_context(content)
        if self.inline_ready and self.stack.currentWidget()is self.note_editor:self.open_editor(content)

    def refresh(self,*,force=False):
        super().refresh(force=force)
        if not self.inline_ready:return
        editor=self.note_editor
        if self.context and self.context.get('kind')=='note-scope':
            self.scene.setText('通用笔记：'+self.context['title'])
            self.status.setText('手选范围的本机笔记；不表示本局已到达该楼层或节点，不会上传。')
        if self.stack.currentWidget()is editor:
            # Follow may advance, but a draft never changes owner. Clean editors
            # return to reading on a new scene rather than showing a stale title.
            if editor.isHidden():
                self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记')
            elif self.key==editor.key:
                if not editor.dirty:editor.set_context(self.context)
            elif not editor.dirty:
                self.stack.setCurrentWidget(self.preview);self.edit.setText('编辑这份笔记')
            else:
                self.status.setText('上方是最近读取的场景；正在编辑的笔记仍对应“'+editor.content['title']+'”，未随读取转移。')
                self.edit.setEnabled(True)
        self.refresh_parents()

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
            if item.widget():item.widget().deleteLater()
        self.parent_views=[]
        if not values:self.parent_layout.addWidget(QLabel('当前场景没有可唯一对应的上级范围；可手选楼层或节点后查看通用笔记。'))
        for context,text,error in values:
            title=QPushButton(context['title']);title.setToolTip('打开此范围的通用笔记');title.clicked.connect(lambda _checked=False,c=context:self.open_scope(c));self.parent_layout.addWidget(title)
            view=NotePreview();view.setMinimumHeight(70);view.setMaximumHeight(140);view.read_markdown(error or text or '此范围尚无笔记。');view.linkBlocked.connect(lambda:self.status.setText('上级笔记中的链接不会自动打开。'))
            self.parent_layout.addWidget(view);self.parent_views.append(view)

    def open_scope(self,content):
        if not self.finish_edit():return False
        # Explicit parent navigation, unlike choosing an exact entry from the
        # picker; no new live-state declaration and no automatic parent writes.
        with QSignalBlocker(self.follow):self.follow.setChecked(False)
        self._run_id=self.run.state.get('id');self.context=content;self.refresh(force=True)
        return self.open_editor(content)

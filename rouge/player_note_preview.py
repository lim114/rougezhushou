"""Local Markdown presentation. Resource loading is denied, never delegated."""
from PySide6.QtCore import QByteArray,Signal
from PySide6.QtGui import QTextDocument,QImage,QColor
from PySide6.QtWidgets import QTextBrowser
from mistune import HTMLRenderer, create_markdown
from .ui_state import _reading_state, _restore_reading


class NotebookHTML(HTMLRenderer):
    def task_list_item(self,text,checked=False):
        # Qt rich text has no HTML input widgets; retain the task state as text.
        return '<li>'+('☑ 'if checked else'☐ ')+text+'</li>\n'


render_note=create_markdown(renderer=NotebookHTML(escape=False),hard_wrap=True,
    plugins=['strikethrough','table','task_lists','url'])

class NoExternalResources(QTextDocument):
    def __init__(self,parent=None):
        super().__init__(parent);self.blocked=[]
    def loadResource(self,kind,url):
        self.blocked.append((kind,url.toString()))
        if kind==QTextDocument.ResourceType.ImageResource:
            image=QImage(1,1,QImage.Format.Format_ARGB32);image.fill(QColor('transparent'))
            self.addResource(kind,url,image)
            return image
        return QByteArray(b'')

class NotePreview(QTextBrowser):
    linkBlocked=Signal()
    def __init__(self,parent=None):
        super().__init__(parent);self._text=None;self.safe_document=NoExternalResources(self);self.setDocument(self.safe_document);self.setOpenExternalLinks(False);self.setOpenLinks(False);self.anchorClicked.connect(self._anchor)
    def _anchor(self,url):
        if not url.scheme()and not url.path()and url.fragment():self.scrollToAnchor(url.fragment())
        else:self.linkBlocked.emit()
    def loadResource(self,kind,url):
        return self.safe_document.loadResource(kind,url)
    def read_markdown(self,text,*,preserve=True):
        if preserve and text==self._text:return
        self._text=text
        state=_reading_state(self)if preserve else None
        self.setHtml(render_note(text).strip())
        if state is not None:_restore_reading(self,state,False)

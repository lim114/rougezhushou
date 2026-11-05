"""Markdown preview with explicit browser links and controlled resource loading."""
from pathlib import Path
from PySide6.QtCore import QByteArray,Signal,QUrl
from PySide6.QtGui import QTextDocument,QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager,QNetworkRequest,QNetworkReply
from PySide6.QtWidgets import QTextBrowser
from mistune import HTMLRenderer, create_markdown
from .ui_state import _reading_state, _restore_reading


class NotebookHTML(HTMLRenderer):
    def task_list_item(self,text,checked=False):
        # Qt rich text has no HTML input widgets; retain the task state as text.
        return '<li>'+('☑ 'if checked else'☐ ')+text+'</li>\n'


render_note=create_markdown(renderer=NotebookHTML(escape=False),hard_wrap=True,
    plugins=['strikethrough','table','task_lists','url'])

class NotePreview(QTextBrowser):
    linkBlocked=Signal()
    def __init__(self,parent=None,*,folder=None):
        super().__init__(parent)
        self._text='';self._resources={};self._pending=set()
        self.network=QNetworkAccessManager(self);self.network.finished.connect(self._resource_finished)
        if folder is not None:self.document().setBaseUrl(QUrl.fromLocalFile(str(Path(folder).resolve())+'/'))
        self.setOpenExternalLinks(False);self.setOpenLinks(False);self.anchorClicked.connect(self._anchor)
    def _anchor(self,url):
        if not url.scheme()and not url.path()and url.fragment():self.scrollToAnchor(url.fragment())
        elif url.scheme()in('http','https'):QDesktopServices.openUrl(url)
        else:self.linkBlocked.emit()
    def loadResource(self,kind,url):
        url=self.document().baseUrl().resolved(url)
        if kind not in (QTextDocument.ResourceType.ImageResource,QTextDocument.ResourceType.HtmlResource,QTextDocument.ResourceType.StyleSheetResource)or url.scheme()not in ('file','http','https'):
            return QByteArray()
        key=url.toString()
        if key in self._resources:return self._resources[key]
        if key not in self._pending:
            self._pending.add(key)
            reply=self.network.get(QNetworkRequest(url));reply.setProperty('resource_url',key)
        return QByteArray()
    def _resource_finished(self,reply):
        key=reply.property('resource_url');self._pending.remove(key)
        if reply.error()==QNetworkReply.NetworkError.NoError:self._resources[key]=reply.readAll()
        else:
            self._resources[key]=QByteArray()
            self.setToolTip('资源未载入：'+key+'\n'+reply.errorString())
        reply.deleteLater()
        self.read_markdown(self._text,reload_resources=True)
    def read_markdown(self,text,*,preserve=True,reload_resources=False):
        if preserve and not reload_resources and text==self._text:return
        state=_reading_state(self)if preserve else None
        self.setHtml(render_note(text).strip())
        if state is not None:_restore_reading(self,state,False)
        self._text=text

from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread,Event
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl,QByteArray
from PySide6.QtGui import QTextDocument,QTextCursor,QDesktopServices,QImage,QColor
from PySide6.QtTest import QTest
from rouge.player_note_preview import NotePreview
from rouge.player_notes import NoteStore,NotesDialog

class NotePreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])

    def test_markdown_preview_renders_words_and_keeps_unchanged_reading(self):
        view=NotePreview();text='# 关卡笔记\n\n- 注意机制\n\n**重点**'
        try:
            view.read_markdown(text);self.assertIn('关卡笔记',view.toPlainText());self.assertIn('重点',view.toPlainText());self.assertNotIn('**',view.toPlainText())
            cursor=view.textCursor();cursor.setPosition(1);cursor.setPosition(3,QTextCursor.MoveMode.KeepAnchor);view.setTextCursor(cursor);selected=cursor.selectedText()
            view.read_markdown(text);self.assertEqual(view.textCursor().selectedText(),selected)
        finally:view.close()

    def test_local_picture_resource_is_empty_and_not_replaced_by_file_contents(self):
        with TemporaryDirectory()as tmp:
            path=Path(tmp)/'private-fixture.png';picture=QImage(4,4,QImage.Format.Format_ARGB32);picture.fill(QColor('red'));self.assertTrue(picture.save(str(path)))
            view=NotePreview()
            try:
                url=QUrl.fromLocalFile(str(path));view.read_markdown('![本机示例]('+url.toString()+')');resource=view.document().resource(QTextDocument.ResourceType.ImageResource,url)
                self.assertIsInstance(resource,QImage);self.assertEqual((resource.width(),resource.height()),(1,1));self.assertEqual(resource.pixelColor(0,0).alpha(),0);self.assertTrue(view.safe_document.blocked)
            finally:view.close()

    def test_network_image_does_not_request_even_a_local_owned_server(self):
        calls=[]
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):calls.append(self.path);self.send_response(200);self.end_headers()
            def log_message(self,*_):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=Thread(target=lambda:server.serve_forever(poll_interval=.01),daemon=True);thread.start();view=NotePreview()
        try:
            url=QUrl(f'http://127.0.0.1:{server.server_port}/owned-fixture.png');view.read_markdown('![外部示例]('+url.toString()+')');view.document().resource(QTextDocument.ResourceType.ImageResource,url);QTest.qWait(80)
            self.assertEqual(calls,[]);self.assertFalse(view.openExternalLinks());self.assertFalse(view.openLinks())
        finally:view.close();server.shutdown();server.server_close();thread.join(2)

    def test_links_are_not_opened_as_external_browser_actions(self):
        view=NotePreview();seen=[];view.linkBlocked.connect(lambda:seen.append(True))
        try:
            with patch.object(QDesktopServices,'openUrl',return_value=False)as opened:
                view.anchorClicked.emit(QUrl('https://example.invalid/notes'));self.gui.processEvents();opened.assert_not_called();self.assertEqual(seen,[True])
        finally:view.close()

    def test_preview_preserves_dirty_edit_binding_and_exact_saved_markdown(self):
        with TemporaryDirectory()as tmp:
            notes=NotesDialog(tmp)
            try:
                self.assertTrue(notes.set_context({'kind':'battle','title':'遗忘时间'}));key=notes.key
                notes.editor.setPlainText('# 私有示例\n\n**只在本机**');notes.pages.setCurrentIndex(1);self.gui.processEvents()
                self.assertTrue(notes.dirty);self.assertEqual(notes.key,key);self.assertIn('只在本机',notes.preview.toPlainText())
                self.assertFalse(notes.set_context({'kind':'battle','title':'另一个示例'}));self.assertEqual(notes.key,key)
                self.assertTrue(notes.save());self.assertFalse(notes.dirty);self.assertEqual(notes.store.read(key)[0],'# 私有示例\n\n**只在本机**')
            finally:notes.discard();notes.close()

    def test_two_assistant_writers_cannot_overwrite_each_other_in_flight(self):
        with TemporaryDirectory()as tmp:
            first,second=NoteStore(tmp),NoteStore(tmp);key='owned-key';expected=first.read(key)[1];entered=Event();release=Event();results=[]
            import rouge.player_notes as module
            original=module.os.replace
            def hold(source,destination):entered.set();release.wait(3);return original(source,destination)
            def save_first():
                try:results.append(first.save(key,'第一窗口',expected))
                except Exception as error:results.append(error)
            with patch.object(module.os,'replace',side_effect=hold):
                thread=Thread(target=save_first);thread.start()
                try:
                    self.assertTrue(entered.wait(2))
                    with self.assertRaises(OSError):second.save(key,'第二窗口',expected)
                finally:release.set();thread.join(3)
            self.assertFalse(thread.is_alive());self.assertEqual(len(results),1);self.assertIsInstance(results[0],str);self.assertEqual(first.read(key)[0],'第一窗口')
            with self.assertRaises(ValueError):second.save(key,'第二窗口',expected)
            self.assertEqual(first.read(key)[0],'第一窗口')

    def test_external_edit_during_byte_preparation_is_not_overwritten(self):
        with TemporaryDirectory()as tmp:
            store=NoteStore(tmp);key='owned-key';expected=store.read(key)[1];expected=store.save(key,'原文',expected)
            with patch('rouge.player_notes.os.fsync',side_effect=lambda _:store.path(key).write_text('其他软件的新内容','utf8')):
                with self.assertRaises(ValueError):store.save(key,'助手的新内容',expected)
            self.assertEqual(store.read(key)[0],'其他软件的新内容')

    def test_player_error_text_explains_file_problem_without_required_system_terms(self):
        from rouge.player_file_messages import file_issue
        for error,expected in [(PermissionError('access denied'),'占用'),(FileNotFoundError('not found'),'不存在'),(FileExistsError('exists'),'未自动覆盖'),(OSError('disk error'),'无法读写'),(ValueError('笔记在保存期间被修改'),'保存期间被修改')]:
            self.assertIn(expected,file_issue(error));self.assertNotIn('access denied',file_issue(error))

if __name__=='__main__':unittest.main()

"""D32 resources through real Qt rendering and isolated HTTP/TLS servers."""
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import ssl
from tempfile import TemporaryDirectory
from threading import Thread
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QBuffer, QIODevice, QPoint, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QImage, QTextDocument
from PySide6.QtNetwork import QSslCertificate
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.player_note_preview import NotePreview


class NoteResourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory()))
        image = QImage(32, 24, QImage.Format.Format_ARGB32)
        image.fill(QColor('#ff0000'))
        buffer = QBuffer(); buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, 'PNG'); self.png = bytes(buffer.data())
        self.view = NotePreview(folder=self.root)
        self.view.resize(560, 360); self.view.show()
        self.addCleanup(self.dispose_view)

    def dispose_view(self):
        self.view.close(); self.view.deleteLater(); QTest.qWait(20)

    def wait_loaded(self):
        QTest.qWait(20)
        deadline = time.monotonic() + 4
        while self.view._pending and time.monotonic() < deadline:
            QTest.qWait(10)
        self.assertFalse(self.view._pending, self.view.toolTip())
        QTest.qWait(20)

    def server(self, *, tls=False):
        calls = []; png = self.png
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                calls.append((self.command, self.path))
                if self.path == '/slow.png': time.sleep(.2)
                if self.path == '/missing':
                    self.send_response(404); self.end_headers(); return
                body = (b'p {color:#123456;}' if self.path.endswith('.css') else
                        '<p>中文资料</p>'.encode() if self.path.endswith('.html') else png)
                self.send_response(200); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        if tls:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.x509.oid import NameOID
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
            now = datetime.now(timezone.utc)
            cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                    .public_key(key.public_key()).serial_number(x509.random_serial_number())
                    .not_valid_before(now-timedelta(minutes=1)).not_valid_after(now+timedelta(days=1))
                    .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]), critical=False)
                    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
                    .sign(key, hashes.SHA256()))
            cert_path = self.root/'server.pem'; key_path = self.root/'key.pem'
            cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); context.load_cert_chain(cert_path, key_path)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            real_get = self.view.network.get
            def get(request):
                config = request.sslConfiguration()
                config.setCaCertificates(QSslCertificate.fromPath(str(cert_path)))
                request.setSslConfiguration(config)
                return real_get(request)
            self.enterContext(patch.object(self.view.network, 'get', side_effect=get))
        thread = Thread(target=lambda: server.serve_forever(poll_interval=.01), daemon=True); thread.start()
        def stop():
            server.shutdown(); server.server_close(); thread.join(2)
        self.addCleanup(stop)
        return f"{'https' if tls else 'http'}://{'localhost' if tls else '127.0.0.1'}:{server.server_port}", calls

    def test_relative_local_image_and_css_are_actually_rendered(self):
        (self.root/'图片.png').write_bytes(self.png)
        (self.root/'theme.css').write_text('p {color:#123456;}', encoding='utf-8')
        self.view.read_markdown('<html><head><link rel="stylesheet" type="text/css" href="theme.css"></head><body><p>样式文字</p><img src="图片.png"></body></html>')
        self.wait_loaded()
        cursor = self.view.document().find('样式文字')
        self.assertEqual(cursor.charFormat().foreground().color().name(), '#123456')
        shot = self.view.viewport().grab().toImage()
        red = sum(shot.pixelColor(x,y).name() == '#ff0000' for x in range(shot.width()) for y in range(shot.height()))
        self.assertGreaterEqual(red, 32*24)
        self.assertTrue(all(key.startswith(QUrl.fromLocalFile(str(self.root)+'/').toString()) for key in self.view._resources))

    def test_http_css_and_picture_render_without_duplicate_requests(self):
        base, calls = self.server()
        self.view.read_markdown(f'<html><head><link rel="stylesheet" type="text/css" href="{base}/theme.css"></head><body><p>联网样式</p><img src="{base}/image.png"></body></html>')
        self.wait_loaded()
        self.assertEqual(sorted(calls), [('GET','/image.png'), ('GET','/theme.css')])
        self.assertEqual(self.view.document().find('联网样式').charFormat().foreground().color().name(), '#123456')
        shot = self.view.viewport().grab().toImage()
        self.assertGreaterEqual(sum(shot.pixelColor(x,y).name() == '#ff0000' for x in range(shot.width()) for y in range(shot.height())), 32*24)

    def test_https_image_uses_real_tls_with_fixture_trust_only(self):
        base, calls = self.server(tls=True)
        self.view.read_markdown(f'![加密图片]({base}/image.png)')
        self.wait_loaded()
        self.assertEqual(calls, [('GET','/image.png')])
        data = self.view.loadResource(QTextDocument.ResourceType.ImageResource, QUrl(base+'/image.png'))
        self.assertEqual(QImage.fromData(data).size().width(), 32)

    def test_html_resource_local_and_http_utf8_contents(self):
        base, calls = self.server()
        body = '<p>中文资料</p>'.encode(); (self.root/'text.html').write_bytes(body)
        for url in (QUrl('text.html'), QUrl(base+'/text.html')):
            self.view.loadResource(QTextDocument.ResourceType.HtmlResource, url)
        self.wait_loaded()
        for url in (QUrl('text.html'), QUrl(base+'/text.html')):
            self.assertEqual(bytes(self.view.loadResource(QTextDocument.ResourceType.HtmlResource, url)), body)
        self.assertEqual(calls, [('GET','/text.html')])

    def test_slow_image_keeps_event_loop_and_new_note_reading(self):
        base, calls = self.server(); ticks = []
        timer = QTimer(); timer.timeout.connect(lambda: ticks.append(True)); timer.start(10)
        self.addCleanup(timer.stop)
        self.view.read_markdown(f'![延迟]({base}/slow.png)')
        self.view.read_markdown('\n\n'.join(f'新笔记第{i}行' for i in range(100)))
        cursor = self.view.document().find('第10行'); self.view.setTextCursor(cursor)
        selected = self.view.textCursor().selectedText(); self.view.verticalScrollBar().setValue(120)
        self.wait_loaded()
        self.assertGreater(len(ticks), 5)
        self.assertIn('新笔记第99行', self.view.toPlainText())
        self.assertEqual(self.view.textCursor().selectedText(), selected)
        self.assertEqual(self.view.verticalScrollBar().value(), 120)
        self.assertEqual(calls, [('GET','/slow.png')])

    def test_missing_resource_finishes_once_with_readable_error(self):
        base, calls = self.server()
        self.view.read_markdown(f'![缺图]({base}/missing)')
        self.wait_loaded()
        self.assertIn('资源未载入', self.view.toolTip())
        self.view.read_markdown(self.view._text, preserve=False); QTest.qWait(30)
        self.assertEqual(calls, [('GET','/missing')])

    def test_page_anchor_click_with_directory_base_stays_in_note(self):
        self.view.read_markdown('<a href="#end">跳到末尾</a><p>正文</p><a name="end">末尾</a>')
        QTest.qWait(20)
        position = next(QPoint(x,y) for y in range(3,70,3) for x in range(3,240,3) if self.view.anchorAt(QPoint(x,y)))
        with patch.object(self.view, 'scrollToAnchor') as scroll:
            QTest.mouseClick(self.view.viewport(), Qt.MouseButton.LeftButton, pos=position)
            self.qt.processEvents()
            scroll.assert_called_once_with('end')

    def test_script_media_and_custom_protocol_are_not_executed(self):
        base, calls = self.server()
        with patch('rouge.player_note_preview.QDesktopServices.openUrl') as opened:
            self.view.read_markdown(f'<script src="{base}/script.js"></script>\n<audio src="{base}/audio.mp3"></audio>\n[附件]({base}/file.zip)\n[应用](custom-app:run)')
            QTest.qWait(40); opened.assert_not_called(); self.assertEqual(calls, [])
            self.view.anchorClicked.emit(QUrl('custom-app:run')); opened.assert_not_called()
            self.view.loadResource(QTextDocument.ResourceType.UserResource, QUrl(base+'/font.woff'))
            self.view.loadResource(QTextDocument.ResourceType.ImageResource, QUrl('custom-app:image'))
            self.assertFalse(self.view._pending)


if __name__ == '__main__': unittest.main()

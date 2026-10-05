"""Offline 0.23 acceptance: saved native frame through the public Qt UI seam.

All mutable account/run/settings/desktop state is isolated. This script does not
discover, capture, or operate a game window, and does not start a chat bridge.
"""
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton

import rouge.app as module


class OfflineWindow(module.MainWindow):
    def refresh_windows(self):
        self.windows.clear()


def source_hashes():
    paths = sorted(path for path in (ROOT / 'rouge').rglob('*')
                   if path.suffix in ('.py', '.json') and '__pycache__' not in path.parts)
    paths += [Path(__file__), ROOT / 'pyproject.toml']
    return {str(path.relative_to(ROOT)).replace('\\', '/'):
            hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def click_source(view, x, y, width, height):
    # Independent aspect-fit calculation using measured source-image positions,
    # not MapView's coordinate helper or the recognition graph's centers.
    rectangle = view.contentsRect()
    scale = min(rectangle.width() / width, rectangle.height() / height)
    point = QPoint(round(rectangle.x() + (rectangle.width() - width * scale) / 2 + x * scale),
                   round(rectangle.y() + (rectangle.height() - height * scale) / 2 + y * scale))
    QTest.mouseClick(view, Qt.MouseButton.LeftButton, pos=point)
    QApplication.processEvents()
    return [point.x(), point.y()]


def verify():
    before = source_hashes()
    sample = ROOT / 'samples/native-client/live-0.23.png'
    payload = sample.read_bytes()
    image = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
    assert image is not None
    height, width = image.shape[:2]
    client_rect = [2, 45, 2050, 1125]
    app = QApplication.instance() or QApplication([])
    font_path = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/msyh.ttc'
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            app.setFont(QFont(families[0], 9))
    with tempfile.TemporaryDirectory(prefix='rouge-sampling-ui-') as directory:
        isolated = Path(directory)
        module.SETTINGS = isolated / 'settings.json'
        module.RUN_STATE = isolated / 'run.json'
        module.OPERATOR_STATE = isolated / 'operators.json'
        backend_type = module.DesktopBackend
        module.DesktopBackend = lambda _path, callback: backend_type(isolated / 'desktop', callback)
        window = OfflineWindow()
        try:
            assert isinstance(window.auto, QCheckBox)
            assert isinstance(window.sample_button, QPushButton)
            assert window.period.value() == .1
            assert not window.auto.isChecked() and not window.timer.isActive()
            assert window.capture.target is None
            assert window.desktop.data_dir == isolated / 'desktop'
            assert window.desktop.process is None
            window.centralWidget().setCurrentIndex(3)
            window.show()
            app.processEvents()

            # The saved fixture's original capture time is not known. This is
            # the timestamp assigned to this offline replay, before recognition.
            captured_at = time.time()
            observation = window.reader.read(image, client_rect=client_rect)
            observation['captured_at'] = captured_at
            window.sample_received((image, observation))
            app.processEvents()

            summary = window.run_summary.text()
            assert '特勤分队' in summary and '保密等级 15' in summary, summary
            assert window.difficulty.currentData() == 15
            assert not window.difficulty.isEnabled()
            graph = window.map_view.graph
            assert graph and graph['template_id'] == '1c', graph
            assert graph['current_node'] == '1,2', graph.get('current_node')
            assert not window.map_view.historical
            assert window.map_view.image is not None
            assert (window.map_view.image.width(), window.map_view.image.height()) == (width, height)

            nodes = {node['id']: node for node in graph['nodes']}
            expected = {'1,2': (1026, 584), '1,3': (1284, 584), '2,3': (1284, 844)}
            for identity in expected:
                assert nodes[identity]['observed_type'] == '林间空地', (identity, nodes[identity])
            assert nodes['1,2'].get('visited'), nodes['1,2']
            mapped = []
            for size in ((1050, 830), (780, 1000), (1450, 750)):
                window.resize(*size)
                app.processEvents()
                for identity, (x, y) in expected.items():
                    point = click_source(window.map_view, x, y, width, height)
                    assert window.map_view.selected == identity, (size, identity, window.map_view.selected)
                    detail = window.map_detail.toPlainText()
                    assert '本帧可见：林间空地' in detail, detail
                    assert '类型未确认' not in detail and '类型未读到' not in detail, detail
                    if identity == '1,2':
                        assert '当前确认位置' in detail, detail
                    mapped.append({'window_size': list(size), 'node_id': identity,
                                   'source_pixel': [x, y], 'ui_click': point,
                                   'detail': detail})

            stamp = time.strftime('%H:%M:%S', time.localtime(captured_at))
            caption = window.capture_status.text()
            assert '画面' + stamp in caption and '秒前' in caption, caption
            assert stamp in window.map_mode.text() and '当前画面' in window.map_mode.text()
            cache_caption = window.sampling_status.text()
            assert '待识别0帧' in cache_caption and '缓存0.0 MiB' in cache_caption, cache_caption
            # Presentation of pending work uses the real bounded frame buffer.
            window.capture.buffer.offer(image, captured_at + .1, client_rect)
            window.update_sampling_status()
            pending_caption = window.sampling_status.text()
            assert '待识别1帧' in pending_caption and '缓存' in pending_caption, pending_caption

            window.resize(1050, 830)
            app.processEvents()
            screenshot = ROOT / '.cache/sampling-ui-0.23.png'
            assert window.grab().save(str(screenshot))
            assert window.desktop.process is None
            assert not (isolated / 'desktop').exists()
            after = source_hashes()
            assert before == after, 'Production source changed during UI verification'
            receipt = {'version': '0.23.0', 'verified_at': time.time(),
                       'sample': str(sample.relative_to(ROOT)).replace('\\', '/'),
                       'sample_sha256': hashlib.sha256(payload).hexdigest(),
                       'image_size': [width, height], 'client_rect': client_rect,
                       'offline_replay_timestamp': captured_at,
                       'default_check_seconds': window.period.value(),
                       'automatic_and_manual_controls_present': True,
                       'summary': summary, 'difficulty_control': window.difficulty.currentData(),
                       'template_id': graph['template_id'], 'current_node': graph['current_node'],
                       'clearings': {identity: {'observed_type': nodes[identity]['observed_type'],
                                              'visited': nodes[identity].get('visited', False)}
                                     for identity in expected},
                       'source_coordinate_clicks': mapped, 'current_image_paired': True,
                       'caption': caption, 'empty_queue_caption': cache_caption,
                       'pending_queue_caption': pending_caption,
                       'screenshot': str(screenshot.relative_to(ROOT)).replace('\\', '/'),
                       'all_mutable_state_isolated': True, 'native_game_capture': False,
                       'game_input_events': 0, 'chat_requests': 0,
                       'source_hashes_before': before, 'source_hashes_after': after,
                       'source_hashes_unchanged': True}
            (ROOT / 'SAMPLING_UI_0.23_VERIFICATION.json').write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({key: receipt[key] for key in
                              ('version', 'difficulty_control', 'template_id', 'current_node',
                               'clearings', 'source_hashes_unchanged', 'chat_requests')},
                             ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()
            module.DesktopBackend = backend_type


if __name__ == '__main__':
    verify()

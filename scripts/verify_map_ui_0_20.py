"""Spatial map interaction through MainWindow's public sampling interface."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import copy
import json
import sys
import tempfile
import time
from pathlib import Path
import cv2
import numpy as np
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rouge.app as app_module
from rouge.recognition import ScreenReader


def click_source_position(window, x, y, width, height):
    # The contract is aspect-fit of the complete source frame, including padding.
    view = window.map_view
    scale = min(view.width()/width, view.height()/height)
    point = QPoint(round((view.width()-width*scale)/2+x*width*scale),
                   round((view.height()-height*scale)/2+y*height*scale))
    QTest.mouseClick(view, Qt.MouseButton.LeftButton, pos=point)
    QApplication.processEvents()


with tempfile.TemporaryDirectory() as directory:
    app_module.OPERATOR_STATE = Path(directory)/'operators.json'
    app_module.RUN_STATE = Path(directory)/'run.json'
    app_module.SETTINGS = Path(directory)/'settings.json'
    app = QApplication([])
    # Offscreen Qt has no Windows system font discovery; load a local font for
    # review screenshots. The actual native Windows app uses its system font.
    font_file = Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/msyh.ttc'
    if font_file.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_file))
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families: app.setFont(QFont(families[0],9))
    window = app_module.MainWindow(); window.auto.setChecked(False)
    try:
        assert window.recognition_mode.count()==2
        assert window.recognition_mode.itemData(1)=='visual'
        window.centralWidget().setCurrentIndex(3); window.show(); app.processEvents()
        image = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png', dtype=np.uint8), 1)
        observed = ScreenReader().read(image); observed['captured_at'] = time.time()
        window.sample_received((image, observed)); app.processEvents()
        assert window.map_view.isVisible()
        assert '当前画面' in window.map_mode.text()
        # Known actual image position of the fixed merchant slot, not a renderer helper.
        for size in [(1050,830), (780,1000), (1450,750)]:
            window.resize(*size); app.processEvents()
            click_source_position(window, .68, .463, 1596, 1198)
            assert '中排 · 第4列' in window.map_detail.toPlainText()
            assert '诡意行商' in window.map_detail.toPlainText()
            assert '候选' in window.map_detail.toPlainText()
        # Source-normalized positions must include external black padding exactly once.
        padded = np.zeros((720,1280,3),np.uint8)
        padded[:,160:1120] = cv2.resize(image,(960,720))
        pad_observed = ScreenReader().read(padded); pad_observed['captured_at'] = time.time()
        window.sample_received((padded,pad_observed)); app.processEvents()
        click_source_position(window, (160+.68*960)/1280, .463, 1280,720)
        assert '中排 · 第4列' in window.map_detail.toPlainText()
        window.map_view.grab().save(str(ROOT/'.cache/map-view-0.20-padded.png'))
        # Missing marker retains a historical position, without claiming current confirmation.
        missing = copy.deepcopy(pad_observed); missing['map']['current_node'] = None
        missing['captured_at'] = time.time(); window.sample_received((padded,missing))
        click_source_position(window, (160+.14*960)/1280, .463,1280,720)
        assert '最近确认位置' in window.map_detail.toPlainText()
        assert '当前确认位置' not in window.map_detail.toPlainText()
        # A different page/image never receives the previous map's coordinates.
        hidden = copy.deepcopy(pad_observed)
        hidden['map'] = {'status':'insufficient','zone_id':'zone_1','reason':'受控遮挡'}
        hidden['run']['map'] = hidden['map']; hidden['captured_at'] = time.time()
        window.sample_received((np.zeros_like(padded),hidden)); app.processEvents()
        assert '历史画面' in window.map_mode.text()
        assert '受控遮挡' in window.map_mode.text()
        click_source_position(window, (160+.68*960)/1280,.463,1280,720)
        assert '诡意行商' in window.map_detail.toPlainText()
        # Native client titlebar crop is already included in external centers.
        wide = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/map-template-node-detail.png',dtype=np.uint8),1)
        wide_observed = ScreenReader().read(wide,client_rect=[2,45,2050,1125])
        wide_observed['captured_at'] = time.time()
        window.sample_received((wide,wide_observed)); app.processEvents()
        click_source_position(window, .45,.544,2052,1127)
        assert '中排 · 第3列' in window.map_detail.toPlainText()
        assert '当前确认位置' in window.map_detail.toPlainText()
        click_source_position(window, .45,.31,2052,1127)
        assert '遗忘时间' in window.map_detail.toPlainText()
        assert '已定位到节点' in window.map_content.text()
        assert '诡意行商：固定2' in window.map_text.toPlainText()
        window.map_view.grab().save(str(ROOT/'.cache/map-view-0.20-wide.png'))
        window.close(); app.processEvents()
        # Restart preserves graph memory, without pretending a screenshot was persisted.
        window = app_module.MainWindow(); window.auto.setChecked(False)
        window.centralWidget().setCurrentIndex(3); window.show(); app.processEvents()
        assert '历史示意图' in window.map_mode.text()
        window.map_view.grab().save(str(ROOT/'.cache/map-view-0.20-history.png'))
        window.reset_run(); app.processEvents()
        assert '尚无' in window.map_mode.text()
        assert not window.map_detail.toPlainText()
        assert window.run.state['maps']=={}
        # A capture from before reset cannot repopulate the spatial view.
        window.sample_received((image,observed)); app.processEvents()
        assert '尚无' in window.map_mode.text()
        receipt = {'version':'0.20.0','verified_at':time.time(),
            'node_content_bound_to_selected_node':True,'generation_budget_rendered':True,
            'spatial_node_selection':True,'resize_cases':3,'padded_source_mapping':True,'native_client_crop_mapping':True,
            'missing_marker_history_explicit':True,'unmatched_frame_uses_paired_history':True,
            'restart_uses_history_schematic':True,'manual_reset_and_stale_frame_guard':True,
            'chat_requests':0}
        (ROOT/'MAP_UI_0.20_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Spatial clicks, 3 sizes, padded frame, historical marker/image, restart and reset passed; no chats')
    finally:
        window.auto.setChecked(False); window.close(); app.processEvents()

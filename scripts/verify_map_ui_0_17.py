"""Replay real map captures through the public Qt sampling interface."""
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
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rouge.app as app_module
from rouge.recognition import ScreenReader

with tempfile.TemporaryDirectory() as directory:
    app_module.OPERATOR_STATE = Path(directory)/'operators.json'
    app_module.RUN_STATE = Path(directory)/'run.json'
    app_module.SETTINGS = Path(directory)/'settings.json'
    app = QApplication([]); window = app_module.MainWindow(); window.auto.setChecked(False)
    try:
        image = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png',dtype=np.uint8),1)
        observed = ScreenReader().read(image); observed['captured_at'] = time.time()
        window.sample_received((image,observed))
        text = window.map_text.toPlainText()
        assert '模板 1b' in text and '当前节点：1,0' in text
        assert '社区约束候选' in text and '紧急作战' in text and '诡意行商' in text
        assert window.desktop_context()['observation']['map']['template_id']=='1b'
        missing_marker=copy.deepcopy(observed);missing_marker['map']['current_node']=None
        missing_marker['captured_at']=time.time();window.sample_received((image,missing_marker))
        assert '当前节点：未确认' in window.map_text.toPlainText()
        assert '最近确认位置：1,0（历史' in window.map_text.toPlainText()
        hidden = copy.deepcopy(observed)
        hidden['map'] = {'status':'insufficient','zone_id':'zone_1','reason':'受控遮挡'}
        hidden['run']['map'] = hidden['map']; hidden['captured_at'] = time.time()
        window.sample_received((image,hidden))
        assert '历史参考' in window.map_text.toPlainText() and '模板 1b' in window.map_text.toPlainText()
        window.reset_run()
        assert '模板 1b' not in window.map_text.toPlainText()
        assert window.run.state['maps']=={}
        receipt = {'version':'0.17.0','verified_at':time.time(),'template_and_candidates_rendered':True,
            'partial_frame_history_explicit':True,'manual_reset_clears_map':True,
            'missing_marker_last_position_explicit':True,'chat_context_has_map':True,'chat_requests':0}
        (ROOT/'MAP_UI_0.17_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Map template/candidates rendered; partial history explicit; reset and chat context passed; no chats')
    finally:
        window.auto.setChecked(False); window.close(); app.processEvents()

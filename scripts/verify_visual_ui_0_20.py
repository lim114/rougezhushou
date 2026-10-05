"""Pure-visual evidence enters the public Qt sampling seam without erasing history."""
import os,sys,tempfile,time,json
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
import rouge.app as app_module
from rouge.recognition import ScreenReader
from rouge.visual_recognition import VisualReader
import cv2,numpy as np
with tempfile.TemporaryDirectory() as directory:
    app_module.OPERATOR_STATE=Path(directory)/'operators.json'
    app_module.RUN_STATE=Path(directory)/'run.json'
    app_module.SETTINGS=Path(directory)/'settings.json'
    app=QApplication([]);window=app_module.MainWindow();window.auto.setChecked(False)
    try:
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/operator-mechanist.png',np.uint8),1)
        full=ScreenReader().read(image);full['captured_at']=time.time()
        window.sample_received((image,full));app.processEvents()
        window.recognition_mode.setCurrentIndex(1)
        pure=VisualReader().read(image);pure['captured_at']=time.time()
        window.sample_received((image,pure));app.processEvents()
        assert window.recognition_mode.currentData()=='visual'
        assert '本帧纯视觉' in window.operator_summary.toPlainText()
        assert '以前已确认记录' in window.operator_summary.toPlainText()
        assert window.operator_observations['mechanist']['fields']['level']==90
        assert pure['operator']['fields']=={'potential':6}
        assert pure['performance']['ocr_model_calls']==0
        (ROOT/'VISUAL_UI_0.20_VERIFICATION.json').write_text(json.dumps({'version':'0.20.0','verified_at':time.time(),
            'backend_selector':True,'image_only_partial_fields_explicit':True,'account_history_preserved':True,
            'fresh_numeric_values_fabricated':False,'ocr_model_calls_in_visual_reader':0,'chat_requests':0},indent=2),encoding='utf8')
        print('Visual mode selection, partial-field warning and retained cultivation history passed.')
    finally:window.close();app.processEvents()

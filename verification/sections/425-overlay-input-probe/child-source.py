from pathlib import Path
import sys,os,json
assert sys.platform=='win32'
os.environ['QT_QPA_PLATFORM']='windows'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt,QTimer
app=QApplication([]);w=QWidget(None,Qt.WindowType.Tool|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowDoesNotAcceptFocus);w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);w.setWindowTitle('隔离输入穿透验证，不是游戏');w.setStyleSheet('background:#354b4a');w.resize(800,500);w.move(80,80);w.show();app.processEvents();Path(sys.argv[1]).write_text(json.dumps({'hwnd':int(w.winId()),'pid':os.getpid()}),'utf8');QTimer.singleShot(12000,app.quit);code=app.exec();w.close();app.processEvents()
from qt_verification_cleanup import shutdown_verification_qt
shutdown_verification_qt()
raise SystemExit(code)

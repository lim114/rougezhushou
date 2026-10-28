from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();window.compact_window.open_map()
# Original project state, manual test window only. No automatic sampling or chat.
raise SystemExit(app.exec())

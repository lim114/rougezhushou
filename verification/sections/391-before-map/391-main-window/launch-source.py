from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact()
# Actual project window for manual acceptance. No automatic game or chat calls.
raise SystemExit(app.exec())

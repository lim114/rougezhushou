"""Actual project test window; manual controls only, no automatic capture/chat."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
app=QApplication([]);window=MainWindow();window.show_compact();window.compact_window.open_inventory();panel=window.compact_window.inventory_popup.panel;panel.held.setChecked(False);panel.search.setText('精选兽肉罐头');panel.entries.setCurrentRow(0)
raise SystemExit(app.exec())

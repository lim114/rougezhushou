"""Record the real font and run the original synthetic OCR regression case."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import __version__ as qt_binding_version
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])
native = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msyh.ttc"
configured = os.environ.get("ROUGE_TEST_CJK_FONT")
paths = {"native": native}
if configured:
    paths["configured"] = Path(configured)
fonts = {}
for kind, path in paths.items():
    font_id = QFontDatabase.addApplicationFont(str(path))
    fonts[kind] = {
        "path": str(path),
        "file_exists": path.is_file(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "application_font_id": font_id,
        "application_font_families": list(QFontDatabase.applicationFontFamilies(font_id)),
    }

case_name = (
    "tests.test_node_content.NodeContentTests."
    "test_event_same_title_and_description_preserve_ambiguous_scene_ids"
)
suite = unittest.defaultTestLoader.loadTestsFromName(case_name)
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
receipt = {
    "case": case_name,
    "platform": platform.platform(),
    "python": sys.executable,
    "PySide6": qt_binding_version,
    "wine_compatibility": os.name == "nt" and bool(os.environ.get("WINEPREFIX")),
    "native_windows_integration_verified": False,
    "QT_QPA_PLATFORM": os.environ.get("QT_QPA_PLATFORM"),
    "ROUGE_TEST_CJK_FONT": configured,
    "fonts": fonts,
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "successful": result.wasSuccessful(),
}
Path(sys.argv[1]).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)

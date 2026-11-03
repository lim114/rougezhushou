"""Visible native dialog check using public literals and no application state."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=60000)
    args = parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog
    app = QApplication([])
    dialog = SupplementalTokenModuleDialog('char_2023_ling', {'elite': 2, 'level': 90})
    dialog.setWindowTitle('第262节 · 令三技能形态测试（公共声明条件）')
    dialog.phase.setCurrentIndex(dialog.phase.findData(2))
    dialog.endpoint.setCurrentIndex(dialog.endpoint.findData('last'))
    dialog.ling_rank.setCurrentIndex(dialog.ling_rank.findData(10))
    dialog.calculate_button.click()
    dialog.resize(1600, 1000); dialog.show(); dialog.raise_(); dialog.activateWindow()
    def snapshot():
        receipt = {'scope': 'native_public_literal_dialog_only', 'pid': os.getpid(),
            'qpa': app.platformName(), 'visible': dialog.isVisible(),
            'rows': dialog.ling_forms.rowCount(), 'hp': dialog.ling_forms.item(15, 4).text(),
            'attack': dialog.ling_forms.item(15, 5).text(),
            'private_state_read': False, 'game_operated': False, 'chat_sent': False,
            'native_mainwindow_or_game_acceptance': False}
        Path(args.receipt).parent.mkdir(parents=True, exist_ok=True)
        Path(args.receipt).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    QTimer.singleShot(700, snapshot)
    QTimer.singleShot(args.visible_ms, dialog.close)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())

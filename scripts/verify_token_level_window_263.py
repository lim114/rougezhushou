"""Visible changed dialog from public level60 literals; no private state."""
import argparse
import json
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
    dialog = SupplementalTokenModuleDialog('char_2023_ling', {'elite': 2, 'level': 60})
    dialog.setWindowTitle('第263节 · 培养等级与原生分支测试（公共声明）')
    dialog.cultivation_mode.setCurrentIndex(dialog.cultivation_mode.findData('host_level'))
    dialog.ling_rank.setCurrentIndex(dialog.ling_rank.findData(10))
    dialog.calculate_button.click()
    dialog.resize(1600, 1000); dialog.show(); dialog.raise_(); dialog.activateWindow()
    def snapshot():
        numeric = next(r for r in dialog.level_result['ling_forms'] if
            r['module_level'] == 3 and r['cultivation_branch'] == 'numeric_lerp'
            and r['form'] == 'advanced' and r['skill_active_declared'])
        result = {'qpa': app.platformName(), 'visible': dialog.isVisible(),
            'token_rows': dialog.table.rowCount(), 'form_rows': dialog.ling_forms.rowCount(),
            'captured_public_level': dialog.training['level'], 'numeric_hp_reference': numeric['values']['hp'],
            'numeric_attack_reference': numeric['values']['attack'],
            'endpoint_controls_hidden': not dialog.phase.isVisible() and not dialog.endpoint.isVisible(),
            'actual_full_panel': dialog.level_result['full_current_panel'],
            'scope': 'native public-literal changed dialog, not game/native full suite',
            'game_operated': False, 'chat_sent': False, 'private_state_read': False}
        p = Path(args.receipt); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    QTimer.singleShot(700, snapshot)
    QTimer.singleShot(args.visible_ms, dialog.close)
    return app.exec()


if __name__ == '__main__': raise SystemExit(main())

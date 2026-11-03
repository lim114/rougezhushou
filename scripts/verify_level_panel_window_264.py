"""Visible public-literal level diagnostic in the actual paired workspace."""
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
    from rouge.calibration import panel_layers
    from rouge.paired_calibration_view import PairedCalibrationPanel
    app = QApplication([])
    panel = PairedCalibrationPanel()
    panel.setWindowTitle('第264节 · 等级面板偏差测试（公共声明）')
    panel.resize(1350, 1000)
    scenario = {'operator': 'mechanist', 'elite': 2, 'level': 90, 'skill': 1, 'skill_rank': 7}
    record = {'scenario': scenario, 'observation': {
        'context_token': panel_layers(scenario)['context_token'], 'panel': '培养与模组',
        'evidence_kind': 'formula_reference',
        'source': '机械师精二60、满信赖、潜能1、无模组的公开固定算术参考；原声明90用于排查，非游戏实录',
        'values': {'hp': 3288, 'attack': 543, 'defense': 701}}}
    panel._write(panel.before_editor, record)
    unchanged = panel.before_editor.toPlainText()
    panel.show()
    panel.before_levels_button.click()
    dialog = panel.level_dialog
    dialog.raise_(); dialog.activateWindow()
    def snapshot():
        result = {'qpa': app.platformName(), 'visible': dialog.isVisible(),
            'rows': dialog.table.rowCount(), 'compatible_levels': dialog.result['compatible_levels'],
            'conclusion': dialog.result['conclusion'],
            'actual_level': dialog.result['actual_level'],
            'observation_unchanged': panel.before_editor.toPlainText() == unchanged,
            'original_declared_level': dialog.result['original_level'],
            'scope': 'Windows public-literal paired workspace and independent diagnostic; not game calibration/full suite',
            'game_operated': False, 'chat_sent': False, 'private_state_read': False}
        path = Path(args.receipt); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    QTimer.singleShot(700, snapshot)
    QTimer.singleShot(args.visible_ms, panel.close)
    return app.exec()


if __name__ == '__main__': raise SystemExit(main())

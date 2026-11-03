"""Actual fixed-map window with public branch position references only."""
import argparse
import json
import hashlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True)
    parser.add_argument('--visible-ms',type=int,default=60000);args=parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge.battle_view import BattlePreviewPanel
    app=QApplication([]);panel=BattlePreviewPanel()
    loaded_sha={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
        ('rouge/battle_view.py','rouge/branch_reference_view.py','rouge/branch_position_overview.py')}
    panel.setWindowTitle('第265节 · 固定分支位置总览（公共资料）')
    panel.resize(1600,1300);panel.set_stage('ro6_n_1_2');panel.branch_toggle.setChecked(True)
    panel.show();panel.raise_();panel.activateWindow()
    def snapshot():
        result={'qpa':app.platformName(),'visible':panel.isVisible(),'stage_id':panel.current_stage,
            'grid_markers':len(panel.grid.branch_positions),
            'original_projected_markers':len(panel.original.projected_branch_positions()),
            'marker_labels':[panel.branch_panel.location.itemText(i) for i in range(panel.branch_panel.location.count())],
            'actual_activation':None,'loaded_source_sha256':loaded_sha,
            'scope':'Windows fixed-source changed preview only; not full UI/game validation',
            'game_operated':False,'chat_sent':False,'private_state_read':False}
        p=Path(args.receipt);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    QTimer.singleShot(750,snapshot);QTimer.singleShot(args.visible_ms,panel.close)
    return app.exec()


if __name__=='__main__':raise SystemExit(main())

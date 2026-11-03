"""Native fixed battle/directory fit checks in the existing isolated UI harness."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse, json, sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check;images=[]

    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QDialog,QVBoxLayout
        from PySide6.QtTest import QTest
        from rouge import current_battle_reference as model
        from rouge.expansion_view import ExpansionUpdatePanel
        original(section,window,gui,require)
        dialog=window.compact_window.map_popup.panel.reference_popup;panel=dialog.panel
        require(panel.result is not None,'exact_battle_from_map_is_available')
        identity=panel.stage_id

        def save(widget,name):
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_snapshot_saved')
            images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})

        def fits(widget,label):
            pix=widget.pixmap()
            require(pix is not None and not pix.isNull(),label+'_has_fixed_original')
            require(pix.width()<=widget.contentsRect().width() and pix.height()<=widget.contentsRect().height(),label+'_full_image_fits_actual_area')
            require(abs(pix.width()/pix.height()-widget.original.width()/widget.original.height())<.03,label+'_preserves_original_aspect')

        panel.notice.setText('隔离固定关卡样例，不是本局读取。'+model.NOTICE)
        for width in (680,1120):
            dialog.resize(width,690);QTest.qWait(80);gui.processEvents()
            fits(panel.map_image,'battle_'+str(width));save(dialog,'battle-'+str(width))
        enemy=panel.result['enemies'][0];panel.enemy_choices.select_value(enemy['key']);panel.tabs.setCurrentIndex(1);gui.processEvents()
        require(enemy['name'] in panel.enemy_player.toPlainText(),'enemy_reference_and_chinese_mechanism_remain_matched')
        require('不以白值替代' in panel.enemy_player.toPlainText(),'unverified_complete_enemy_panel_is_not_fabricated')
        save(dialog,'enemy')
        action=next((r for r in panel.result['actions']if r['raw'].get('actionType')in('SPAWN','ACTIVATE_PREDEFINED')),None)
        require(action is not None and panel.focus_action(action),'exact_action_navigation_survives_queue_refactor')
        require(panel.action_key==action['key'],'focused_action_keeps_exact_identity')
        save(dialog,'action')
        with patch.object(model,'stage_reference',return_value=None):
            require(panel.refresh_reference() is False,'unavailable_stage_still_clears_all_child_readers')
            dialog.resize(900,670);gui.processEvents()
            require(panel.map_image.pixmap() is None or panel.map_image.pixmap().isNull(),'resize_after_source_loss_does_not_restore_old_image')
            require(panel.rewards.result is None and panel.settlement.result is None,'reward_and_settlement_cleared_with_parent_source')
        require(panel.refresh_reference(),'manual_recheck_restores_source')
        require(panel.enemy_key is None and panel.action_key is None,'restored_source_does_not_restore_invalid_old_selection')
        panel.notice.setText('隔离固定关卡样例，不是本局读取。'+model.NOTICE)
        other=QDialog(window,Qt.WindowType.Tool);other.setWindowTitle('隔离目录地图验证');other.resize(1000,720)
        body=QVBoxLayout(other);directory=ExpansionUpdatePanel(categories=('stages',));body.addWidget(directory)
        try:
            other.show();directory.category.setCurrentIndex(directory.category.findData('stages'))
            directory.scope.setCurrentIndex(directory.scope.findData(False))
            for i in range(directory.entries.count()):
                if directory.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity:directory.entries.setCurrentRow(i);break
            require(directory.result is not None and directory.result['row']['id']==identity,'directory_selects_same_exact_fixed_stage')
            raw=directory.image_raw;directory.notice.setText('隔离目录样例，不是本局读取；仅核对同一固定地图的显示。')
            for width in (720,1120):
                other.resize(width,700);QTest.qWait(80);gui.processEvents()
                fits(directory.map_image,'directory_'+str(width))
                require(directory.image_raw==raw,'directory_resize_keeps_source_bytes_'+str(width))
                save(other,'directory-'+str(width))
        finally:
            other.close();gui.processEvents()
        panel.tabs.setCurrentIndex(0);dialog.show();gui.processEvents();window.player_validation_target=dialog

    player_acceptance.check=check
    code=run(431,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'kind':'maintenance_not_new_section','images':images,
        'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)

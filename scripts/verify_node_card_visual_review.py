"""Video card layout, native input and unchanged exact navigation; isolated public fixtures."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,sys,os
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
    original=player_acceptance.check;images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from rouge.player_map_acceptance import fixtures
        from rouge.player_map_hover import NodeEntryButton
        import win32gui,win32process
        original(section,window,gui,require)
        before=deepcopy(window.run.state)
        def save(widget,name):
            gui.processEvents();h=int(widget.winId())
            require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_visible_owned')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_image_saved')
            images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        try:
            graphs,identity,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in graphs}
            bar=window.compact_window;bar.open_map();gui.processEvents();panel=bar.map_popup.panel;panel.hover_timer.stop();panel.leave_timer.stop()
            graph=panel.view.graph;binding=(panel.epoch,graph['zone_id'],graph['template_id'],identity);card=panel.hover_card
            card.pin.setChecked(False);card.source_toggle.setChecked(False);card.install(binding,graph,identity,{},panel.view,force=True);card.show();gui.processEvents()
            require(card.summary.isVisible()and not card.notice.isVisible(),'limits_visible_without_long_source_paragraph')
            require(card.scroll.frameShape()==card.scroll.Shape.NoFrame,'scroll_has_no_separate_black_frame')
            require(all(isinstance(b,NodeEntryButton)and b.caption_rect().bottom()<b.height()for _,_,b in card.entry_buttons),'names_overlay_their_own_tiles')
            require(all(b.accessibleName()==b.text()and not b.icon().isNull()for _,_,b in card.entry_buttons),'full_names_and_exact_art_or_node_icons_remain')
            card.title.setText('隔离布局样例 · 不是本局地图识别');save(card,'compact-card')
            choices=[(k,i,b.text())for k,i,b in card.entry_buttons]
            card.pin.click();QTest.mouseClick(card.source_toggle,Qt.MouseButton.LeftButton);gui.processEvents()
            require(card.notice.isVisible()and card.source_toggle.isChecked(),'source_explanation_expands_by_native_click')
            card.install(binding,graph,identity,{},panel.view,force=True);gui.processEvents()
            require(card.pinned and card.binding==binding and card.notice.isVisible(),'same_node_update_keeps_pin_and_open_explanation')
            require(choices==[(k,i,b.text())for k,i,b in card.entry_buttons],'visual_change_preserves_exact_entry_ids_names_and_order')
            card.title.setText('隔离布局样例 · 已展开统计说明');save(card,'source-details')
            card.source_toggle.click();card.resize(460,600);gui.processEvents();card.title.setText('隔离布局样例 · 加宽后图片等比裁切');save(card,'wide-card')
            kind,entry,button=next(row for row in card.entry_buttons if row[0]=='event')
            button.setFocus();QTest.keyClick(button,Qt.Key.Key_Space);gui.processEvents()
            require(panel.selected_reference[1:]==(kind,entry),'native_keyboard_opens_exact_event_not_a_nearby_title')
            node=next(n for n in graph['nodes']if n['id']==identity)
            node['prediction']={'candidates':['诡意行商','秘境行商','失与得','误入奇境','安全的角落','不期而遇','得偿所愿','应急助力']}
            card.pin.setChecked(False);card.resize(card.sizeHint());card.install(binding,graph,identity,{},panel.view,force=True);card.show();gui.processEvents()
            card.title.setText('隔离布局样例 · 8类声明，非本局预测');save(card,'three-column-card')
            require(len(card.type_values)==8,'three_column_layout_handles_eight_explicit_test_types')
            card.source_toggle.setChecked(True);card.hide();card.show();gui.processEvents()
            require(card.source_toggle.isChecked()and card.notice.isVisible(),'source_details_survive_hide_and_restore')
            missing=next((b for _,_,b in card.entry_buttons if b.artwork.isNull()),None)
            require(missing is not None and not missing.icon().isNull(),'unmapped_art_has_explicit_icon_fallback_not_borrowed_image')
            card.scroll.ensureWidgetVisible(missing,0,0);gui.processEvents()
            require(not missing.visibleRegion().isEmpty(),'fallback_tile_scrolled_into_visible_viewport')
            save(card,'missing-art-card')
            window.player_validation_target=bar.map_popup
        finally:window.run.state=before
    player_acceptance.check=check
    code=run(392,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixture_only':True,'eight_types_are_layout_fixture_not_inferred_game_state':True,'event_probabilities_not_invented':True,'base_node_hover_png_is_diagnostic_not_visibility_proof':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)

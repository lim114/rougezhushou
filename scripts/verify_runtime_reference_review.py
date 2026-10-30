"""Actual player-reader navigation after restoring public reference loaders."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from tempfile import TemporaryDirectory
from unittest.mock import patch
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[]
    def check(section,window,gui,require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        from shiboken6 import isValid
        import win32gui,win32process
        from rouge import node_catalog as catalog,battle_event_references as battle,named_reward_items as items,ritual_weakening as ritual
        state=deepcopy(window.run.state);node=window.node_catalog;preview=window.battle_preview
        def save(widget,name):
            gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
            path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest(),'visible_owned_at_save':True})
        def event(identity):
            row=next(e for e in catalog.all_events(include_indirect=True)['rows']if e['id']==identity)
            node.kind.setCurrentIndex(node.kind.findData('event'));node.floor.setCurrentIndex(0);node.node_type.setCurrentIndex(0);node.search.setText(row['title']);node.refresh()
            index=next(i for i,e in enumerate(node.entries)if e['kind']=='event'and e['record']['id']==identity);node.list.setCurrentRow(index)
            window.centralWidget().setCurrentWidget(node);window.show();gui.processEvents();require(node.isVisible(),'normal_player_event_page_visible')
        def first(combo):
            combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home);gui.processEvents();require(combo.currentIndex()==0,'actual_keyboard_chooses_first_reference')
        event(items.EVENT_IDS[0]);require(node.named_reward_button.isVisible()and node.named_reward_button.isEnabled(),'named_reward_entry_restored_in_actual_player_page')
        QTest.mouseClick(node.named_reward_button,Qt.MouseButton.LeftButton);gui.processEvents();named=node.named_reward_window
        require(named.isVisible()and named.choice.count()==3 and named.choice.currentData()is None,'named_reward_open_starts_unselected_with_three_exact_choices');first(named.choice)
        require('他缚'in named.player_text.toPlainText()and named.icon.isVisible(),'relic_name_and_image_visible_after_explicit_choice');save(named,'named-item')
        event('community_group_007');QTest.mouseClick(node.named_reward_button,Qt.MouseButton.LeftButton);gui.processEvents();first(named.choice)
        require('笼控器'in named.player_text.toPlainText()and'零件'in named.player_text.toPlainText(),'scrap_reward_keeps_its_own_kind_and_description');save(named,'named-scrap');named.close()
        event(ritual.EVENT_ID);require(node.ritual_weakening_button.isVisible()and node.ritual_weakening_button.isEnabled(),'ritual_entry_restored_in_actual_player_page')
        QTest.mouseClick(node.ritual_weakening_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=node.ritual_weakening_window
        require(dialog.isVisible()and dialog.choice.count()==6 and dialog.choice.currentData()is None,'ritual_retains_all_six_manual_choices_without_auto_selection');first(dialog.choice)
        require(dialog.open_stage_button.isEnabled()and'弱化'in dialog.player_text.toPlainText(),'ritual_condition_effect_and_explicit_fixed_battle_entry_visible');save(dialog,'ritual')
        QTest.mouseClick(dialog.open_stage_button,Qt.MouseButton.LeftButton);gui.processEvents();old=dialog.battle_window
        require(old is not None and old.isVisible()and dialog.battle_preview.current_stage=='ro6_b_6','manual_ritual_button_opens_exact_fixed_battle_without_applying_effect');save(old,'ritual-battle')
        with TemporaryDirectory(prefix='rouge-reference-loss-')as folder,patch.object(ritual,'ROOT',Path(folder)):
            dialog.refresh_reference();gui.processEvents();require(dialog.choice.count()==0 and not dialog.open_stage_button.isEnabled(),'source_loss_clears_choices_and_action')
            require(not isValid(old)or not old.isVisible(),'source_loss_closes_owned_old_related_battle');save(dialog,'source-unavailable')
        dialog.refresh_reference();require(dialog.choice.count()==6 and dialog.choice.currentData()is None,'restored_source_requires_new_manual_choice');dialog.close()
        preview.set_stage('ro6_t_1');window.centralWidget().setCurrentWidget(preview);window.show();gui.processEvents();require(preview.isVisible(),'normal_player_battle_page_visible')
        QTest.mouseClick(preview.entry_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();entry=preview.entry_reference_window
        require(entry.isVisible()and entry.event_choice.count()==1 and entry.event_choice.currentData()is None,'exact_battle_event_reader_restored_without_auto_choice');first(entry.event_choice);save(entry,'battle-entry')
        token=battle.stage_event_references('ro6_t_1')['rows'][0]['token'];QTest.mouseClick(entry.open_event_button,Qt.MouseButton.LeftButton);gui.processEvents()
        require(node.isVisible()and node.event_scene_filter.currentData()==token['scene_key']and node.event_choice_filter.currentData()==token['choice_key'],'actual_battle_entry_button_maps_to_exact_event_scene_and_choice');save(node,'exact-event-choice')
        require(window.run.state==state,'all_reference_navigation_preserves_owned_fixture_run');window.player_validation_target=node
    player_acceptance.check=check;code=run(419,args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'isolated_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
    raise SystemExit(code)

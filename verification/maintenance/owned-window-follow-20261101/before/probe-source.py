from pathlib import Path
import sys,json
from copy import deepcopy
from unittest.mock import patch
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/owned-window-follow-20261101/before';B.mkdir(exist_ok=False)
from rouge import player_acceptance
from player_ui_verification import run
from PySide6.QtCore import QRect,QPoint
from PySide6.QtWidgets import QDialog

def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.run.state['last_node_content']={'kind':'event','title':'呼吸的红苔'};window.show_compact();c=window.compact_window;c.game_binding.timer.stop();c.game_hover.timer.stop();c.game_overlay.timer.stop();c.open_scene_battle();p=c.scene_popup.panel;p.event_choices.setCurrentIndex(1);require(p.open_event(),'before_real_event_dialog_opens');gui.processEvents();d=p.event_dialog;b=c.game_binding
 snap={'key':(123,456),'active':True,'logical_client':QRect(100,100,1000,600),'screen':gui.primaryScreen()};b.apply(snap);d.move(200,200);start=d.pos();snap=dict(snap,logical_client=snap['logical_client'].translated(17,11));b.apply(snap);gui.processEvents();rows={'dynamic_event_in_surfaces':d in b.surfaces(),'actual_event_delta':[d.x()-start.x(),d.y()-start.y()],'expected_event_delta':[17,11]};b.apply(None);gui.processEvents();rows['event_visible_after_binding_unavailable']=d.isVisible()
 # Put the actual event dialog in the old explicit active slot to isolate restore semantics.
 b.apply(snap);c.active_popup=d;d.show();gui.processEvents();b.apply(None);rows['old_active_event_in_suspended']=d in b.suspended;rows['hidden_event_close_accepted']=d.close();gui.processEvents();b.restore();gui.processEvents();rows['accepted_closed_event_was_reopened']=d.isVisible()
 modal=QDialog(c);modal.setModal(True);modal.show();gui.processEvents();rows['actual_modal_before_follow']=gui.activeModalWidget()is modal;b.apply(None);gui.processEvents();rows['toolbar_remained_visible_during_modal']=c.isVisible();modal.close();b.enabled=False;b.snapshot=None;b.previous=None;b.ever_bound=False;d.show();gui.processEvents();window.player_validation_target=d;window.run.state=before
 rows.update(actual_game_or_chat=False,temporary_state_only=True);(B/'observed.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');print(rows,flush=True)
with patch.object(player_acceptance,'check',check):code=run(447,B/'window.json')
(B/'probe-source.py').write_bytes(Path(__file__).read_bytes());raise SystemExit(code)

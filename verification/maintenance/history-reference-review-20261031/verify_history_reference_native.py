from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import player_acceptance
from rouge.player_replay_archive import reload_history
from player_ui_verification import run
out=R/'verification/maintenance/history-reference-review-20261031/native';out.mkdir(exist_ok=False);images=[]
def check(section,w,gui,require):
    before=deepcopy(w.run.state)
    try:
        w.run.state['history']=[{'kind':'relic_confirmed','id':'rogue_6_relic_cargo_15','at':1}]
        w.show_compact();bar=w.compact_window;bar.open_replay();gui.processEvents();popup=bar.replay_popup;p=popup.panel
        p.tabs.setCurrentWidget(p.evidence);p.history_views_button.setChecked(True);gui.processEvents()
        entries=p.evidence.lists['relic'];QTest.mouseClick(entries.viewport(),Qt.MouseButton.LeftButton,pos=entries.visualItemRect(entries.item(0)).center());gui.processEvents()
        state=deepcopy(w.run.state)
        def image(name):
            gui.processEvents();file=out/(name+'.png');assert popup.grab().save(str(file));images.append({'path':file.relative_to(R).as_posix(),'sha256':sha256(file.read_bytes()).hexdigest()})
        require('装饰性佯谬'in p.evidence.detail.toPlainText(),'compact_current_reference_readable');image('current-reference')
        with patch('rouge.expansion_reference.packet',return_value=None):
            bar.refresh();gui.processEvents()
            require('固定资料名称未核对'in p.evidence.detail.toPlainText(),'compact_same_history_source_loss_clears_name')
            require(entries.item(0).icon().pixmap(46,46).isNull(),'compact_source_loss_clears_image')
            require(entries.currentRow()==0,'compact_source_loss_keeps_exact_record');image('current-source-unavailable')
        bar.refresh();gui.processEvents();require('装饰性佯谬'in p.evidence.detail.toPlainText(),'compact_reference_recovers_without_history_change')
        item=entries.item(0)
        from rouge import player_evidence_history as module
        with patch.object(module,'evidence_rows',wraps=module.evidence_rows)as projection:
            for _ in range(3):bar.refresh();gui.processEvents()
        require(projection.call_count==0 and entries.item(0)is item,'stable_refresh_validates_source_without_rebuilding_rows')
        old=deepcopy(state);old['id']='isolated-reference-archive';p.history_store.archive(old);reload_history(p)
        p.sessions.setCurrentIndex(p.sessions.findData('archive:'+old['id']));p.tabs.setCurrentWidget(p.evidence);entries.setCurrentRow(0);gui.processEvents()
        files={q.name:q.read_bytes()for q in p.history_store.folder.iterdir()}
        with patch('rouge.expansion_reference.packet',return_value=None):
            bar.refresh();gui.processEvents();require('固定资料名称未核对'in p.evidence.detail.toPlainText(),'compact_archive_lost_reference_cleared');image('archive-source-unavailable')
        bar.refresh();gui.processEvents();require('装饰性佯谬'in p.evidence.detail.toPlainText(),'compact_archive_reference_recovers');image('archive-reference-restored')
        require(p.snapshot['id']==old['id']and entries.currentRow()==0,'archive_selection_kept_after_source_restore')
        require(w.run.state==state,'live_run_untouched_by_archive_reference_refresh')
        require(files=={q.name:q.read_bytes()for q in p.history_store.folder.iterdir()},'source_refresh_does_not_rewrite_archive')
        w.player_validation_target=popup
    finally:w.run.state=before
with patch.object(player_acceptance,'check',check):code=run(999,out/'receipt.json')
(out/'images.json').write_text(json.dumps({'images':images,'isolated_records_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(code)

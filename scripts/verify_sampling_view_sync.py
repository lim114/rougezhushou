"""Native-window checks for deferred hidden views, in the existing isolated harness."""
from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]

def main():
    out=Path(sys.argv[1])
    if len(sys.argv)==2:
        out.mkdir(parents=True,exist_ok=False)
        with(out/'stdout.txt').open('wb')as a,(out/'stderr.txt').open('wb')as b:
            child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,str(out),'child'],stdout=a,stderr=b);code=child.wait()
        (out/'process.json').write_text(json.dumps({'actual_PID':child.pid,'actual_exit':code},indent=2)+'\n','utf8',newline='\n')
        (out/'run-source.py').write_bytes(Path(__file__).read_bytes())
        print((out/'stdout.txt').read_text('utf8')[-800:]);print((out/'stderr.txt').read_text('utf8')[-800:]);return code
    from copy import deepcopy
    from unittest.mock import patch
    import time,numpy as np
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QDialog
    from rouge import player_acceptance
    from rouge.observation_timeline import ObservationTimeline
    from rouge.player_inventory import inventory_rows
    import player_ui_verification as ui
    def check(section,w,gui,require):
        before=deepcopy(w.run.state);account=deepcopy(w.account_cache.records)
        w.show_compact();c=w.compact_window;c.reference_window.close()
        for timer in w.findChildren(QTimer):timer.stop()
        require(not w.node_catalog.isVisible()and not w.inventory_panel.isVisible(),'catalog_and_inventory_hidden_with_toolbar_only')
        at=max(time.time(),before['started_at']+1);image=np.full((24,36,3),65,np.uint8)
        w.observation_timeline=ObservationTimeline(w.run,w.account_cache)
        def deliver(seq,gold):
            observation={'page':'unknown','nodes':[],'captured_at':at+seq,
                         'run':{'resources':{'gold':{'value':gold}}}}
            observation['_timeline_result']=w.observation_timeline.prepare(observation,seq,None)
            w.sample_received((image,observation));gui.processEvents()
        with patch.object(w.node_catalog,'refresh',wraps=w.node_catalog.refresh)as catalog_refresh,patch.object(w.inventory_panel,'refresh',wraps=w.inventory_panel.refresh)as inventory_refresh:
            deliver(1,3);deliver(2,9);deliver(3,51)
            require(catalog_refresh.call_count==0,'hidden_catalog_skips_three_tree_rebuilds')
            require(inventory_refresh.call_count==0,'hidden_inventory_skips_three_rebuilds')
        require(w.run.state['resources']['gold']['value']==51,'run_resource_updates_while_views_hidden')
        require(w.node_catalog.runtime_context['gold']==51,'catalog_model_updates_while_hidden')
        c.open_full(page=w.node_catalog);gui.processEvents()
        require(w.node_catalog.isVisible(),'original_catalog_visible_in_shared_workspace')
        require(all(e['qualification']['context']['gold']==51 for e in w.node_catalog.entries if e['kind']=='event'),'catalog_opens_with_latest_conditions')
        w.node_catalog.search.setText('货从口出');gui.processEvents();key=w.node_catalog.list.selected_key()
        with patch.object(w.node_catalog,'refresh',wraps=w.node_catalog.refresh)as refresh:
            deliver(4,4);require(refresh.call_count>0,'visible_catalog_updates_on_next_sample')
        require(w.node_catalog.search.text()=='货从口出'and w.node_catalog.list.selected_key()==key,'visible_catalog_preserves_search_and_selection')
        c.reference_window.close();dialog=QDialog(w.node_catalog);w.node_catalog.destination_window=dialog;dialog.show();gui.processEvents()
        with patch.object(w.node_catalog,'refresh')as refresh:
            w.node_catalog.set_map_context(None,runtime_context={'gold':7},defer_refresh=True)
            require(dialog.isVisible()and refresh.call_count==1,'visible_independent_reader_prevents_hidden_parent_deferral')
        dialog.close();w.node_catalog.destination_window=None
        item=inventory_rows({},held_only=False)[0]['id']
        w.run.state['relics'][item]={'held':True,'captured_at':at,'source':'isolated_native_case'}
        c.open_full(page=w.inventory_panel);gui.processEvents()
        require(w.inventory_panel.isVisible()and item in w.inventory_panel.rows,'inventory_opens_with_new_holding')
        w.inventory_panel.search.setText('攻击');query=w.inventory_panel.search.text()
        with patch.object(w.inventory_panel,'refresh',wraps=w.inventory_panel.refresh)as refresh:
            w.sync_run_config();require(refresh.call_count>0,'visible_inventory_refreshes_immediately')
        require(w.inventory_panel.search.text()==query,'inventory_search_survives_visible_refresh')
        w.run.state=before;w.account_cache.records=account;w.operator_observations=account
        w.observation=None;w.map_frame=None
        w.player_validation_target=c.reference_window
    player_acceptance.check=check
    return ui.run(472,out/'window.json')

if __name__=='__main__':raise SystemExit(main())

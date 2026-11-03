"""Targeted before/after GUI-handler timing in temporary synthetic run state."""
from pathlib import Path
from types import ModuleType
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
from hashlib import sha256
import json,statistics,subprocess,sys,time
import numpy as np
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
BASE='d06efce62ba746599fd1c7375949b888dd86f182'

def main():
    output=Path(sys.argv[1]);output.mkdir(parents=True,exist_ok=False)
    from tests import test_sampling_flow as fixture
    from rouge.app import MainWindow
    from rouge.node_catalog_view import NodeCatalogPanel
    from rouge.player_inventory import InventoryPanel
    from rouge.observation_timeline import ObservationTimeline
    originals={}
    for name in ('app','node_catalog_view','player_inventory'):
        module=ModuleType('rouge._sampling_before_'+name);module.__package__='rouge';module.__file__=str(ROOT/'rouge'/f'{name}.py')
        source=subprocess.check_output(['git','show',BASE+':rouge/'+name+'.py'],cwd=ROOT)
        exec(compile(source,module.__file__,'exec'),module.__dict__);originals[name]=module
    fixture.SamplingFlowTests.setUpClass()
    image=np.full((1127,2000,3),65,np.uint8);at=time.time()+1000
    frozen={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('rouge/app.py','rouge/node_catalog_view.py','rouge/player_inventory.py')}
    rows=[];states={};common=None
    for mode in ('before','after'):
        with ExitStack() as stack:
            if mode=='before':
                stack.enter_context(patch.object(MainWindow,'render_map',originals['app'].MainWindow.render_map))
                stack.enter_context(patch.object(MainWindow,'sync_run_config',originals['app'].MainWindow.sync_run_config))
                stack.enter_context(patch.object(NodeCatalogPanel,'set_map_context',originals['node_catalog_view'].NodeCatalogPanel.set_map_context))
                stack.enter_context(patch.object(NodeCatalogPanel,'showEvent',QWidget.showEvent))
                stack.enter_context(patch.object(InventoryPanel,'showEvent',QWidget.showEvent))
            case=fixture.SamplingFlowTests();case.setUp()
            try:
                w=case.window;w.show_compact()
                for timer in w.findChildren(QTimer):timer.stop()
                if common is None:common=deepcopy(w.run.state)
                else:w.run.state=deepcopy(common)
                w.observation_timeline=ObservationTimeline(w.run,w.account_cache)
                for i in range(10):
                    content={'kind':'battle','title':'遗忘时间','stage_id':'ro6_n_1_1'}
                    packet={'page':'node_detail','nodes':[],'captured_at':at+i,'node_content':content,
                            'run':{'resources':{'gold':{'value':9}},'node_content':content}}
                    packet['_timeline_result']=w.observation_timeline.prepare(packet,i+1,None)
                    t=time.perf_counter();w.sample_received((image,packet));ms=(time.perf_counter()-t)*1000
                    rows.append({'mode':mode,'sample':i,'handler_ms':round(ms,3)})
                states[mode]=deepcopy(w.run.state)
            finally:case.doCleanups()
    value={'passed':states['before']==states['after'],'baseline_commit':BASE,
           'same_final_run_state':states['before']==states['after'],
           'warm_handler_median_ms':{name:statistics.median(x['handler_ms'] for x in rows if x['mode']==name and x['sample']>0) for name in ('before','after')},
           'timings':rows,'source_sha256':frozen,
           'scope':'Owned compact toolbar, hidden catalog/inventory, identical synthetic observations in isolated state. Handler only; no capture, OCR, paint/compositor or real-game latency measurement.',
           'game_operated':False,'chat_sent':False,'private_files_read_or_copied':False}
    assert frozen=={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in frozen}
    (output/'summary.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8',newline='\n')
    print(json.dumps({k:v for k,v in value.items() if k not in ('timings','source_sha256')},ensure_ascii=False),flush=True)
    return 0 if value['passed'] else 1

if __name__=='__main__':raise SystemExit(main())

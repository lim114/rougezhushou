"""Compare actual hidden readers against a caller-supplied, frozen old module.

Temporary run/settings only. Does not capture game frames, send chat or fetch data.
This is a focused UI benchmark, not end-to-end recognition performance.
"""
from pathlib import Path
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from unittest.mock import patch
from hashlib import sha256
from statistics import median
from time import perf_counter
import argparse, importlib.util, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def run(previous, output):
    from PySide6.QtWidgets import QApplication
    from rouge import app as a, public_archive, public_node_statistics
    from rouge.player_compact import CompactAssistant
    from rouge.player_map_acceptance import fixtures
    gui=QApplication.instance() or QApplication([])
    spec=importlib.util.spec_from_file_location('rouge._frozen_compact_review',previous)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows=[];forbidden_calls=[]
    def forbidden(name):
        def fail(*args,**kwargs):
            forbidden_calls.append(name);raise AssertionError(name)
        return fail
    for label,cls in (('before',module.CompactAssistant),('after',CompactAssistant)):
        with TemporaryDirectory(prefix='rouge-popover-review-') as folder,ExitStack() as stack:
            root=Path(folder)
            for key,path in {'ROOT':root,'SETTINGS':root/'settings.json','RUN_STATE':root/'run.json','OPERATOR_STATE':root/'operators.json'}.items():stack.enter_context(patch.object(a,key,path))
            backend=a.DesktopBackend
            stack.enter_context(patch.object(a,'DesktopBackend',lambda _path,callback:backend(root/'chat',callback)))
            stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
            for name in ('connect','capture','next_frame'):stack.enter_context(patch.object(a.GameCapture,name,side_effect=forbidden(name)))
            for name in ('start','request'):stack.enter_context(patch.object(backend,name,side_effect=forbidden('desktop_'+name)))
            stack.enter_context(patch.object(a,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(a,'read_key',side_effect=forbidden('credential_read')))
            stack.enter_context(patch.object(public_archive,'fetch',side_effect=forbidden('public_archive_fetch')))
            stack.enter_context(patch.object(public_node_statistics,'fetch',side_effect=forbidden('public_statistics_fetch')))
            owner=a.MainWindow();bar=None
            try:
                graphs,*_=fixtures();owner.run.state['maps']={g['zone_id']:g for g in graphs}
                bar=cls(owner);owner.compact_window=bar
                for open_reader in (bar.open_inventory,bar.open_map,bar.open_scene_battle,bar.open_team,bar.open_replay):open_reader()
                bar.present(bar.settings_popup);gui.processEvents()
                popups=(bar.inventory_popup,bar.map_popup,bar.scene_popup,bar.team_popup,bar.replay_popup)
                assert not any(p.isVisible() for p in popups)
                bar.refresh()  # Warm existing catalog/source caches in both versions.
                readers=[bar.inventory_popup.panel,bar.inventory_popup.parts,bar.inventory_popup.tools,bar.inventory_popup.shop,*[p.panel for p in popups[1:]]]
                with ExitStack() as counters:
                    spies=[counters.enter_context(patch.object(p,'refresh',wraps=p.refresh)) for p in readers]
                    samples=[]
                    for _ in range(3):
                        start=perf_counter();bar.refresh();samples.append((perf_counter()-start)*1000)
                    calls=sum(spy.call_count for spy in spies)
                rows.append({'version':label,'hidden_reader_refresh_calls_over_3_updates':calls,'samples_ms':samples,'median_ms':median(samples),'hidden_reader_count':len(readers),'actual_readers_executed':True})
            finally:
                owner.close();gui.processEvents()
    assert not forbidden_calls and rows[1]['hidden_reader_refresh_calls_over_3_updates']==0
    result={'passed':True,'scope':'actual existing hidden UI readers with public fixture maps and temporary empty run; not total application or recognition speed','previous_source_sha256':sha256(previous.read_bytes()).hexdigest(),'current_source_sha256':sha256((ROOT/'rouge/player_compact.py').read_bytes()).hexdigest(),'qpa':gui.platformName(),'samples':rows,'forbidden_external_calls':forbidden_calls,'private_state_used':False,'same_frozen_public_inputs':True}
    output.parent.mkdir(parents=True,exist_ok=True);assert not output.exists()
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--previous',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();run(args.previous,args.output)

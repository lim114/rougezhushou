"""Observed offline recognition/reuse checks; no game, chat, or private settings."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import argparse
import copy
import hashlib
import importlib.util
import json
import statistics
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.recognition import ScreenReader
from rouge.run_state import RunState
from rouge.run_config import config_data
from rouge import run_badges
from tests.test_relic_grade_sync_032 import icon,bar,grade,BASE

FILES=('rouge/relic_recognition.py','rouge/run_state.py','rouge/run_config.py',
    'rouge/run_recognition.py','rouge/recognition.py','rouge/visual_recognition.py',
    'rouge/app.py','rouge/data/run-config.json','rouge/data/relic-reference-equivalence.json',
    'rouge/data/relic-mechanics.json','scripts/build_run_config.py',
    'tests/test_relic_grade_sync_032.py','tests/test_run_reuse_guards_032.py',
    'scripts/verify_relic_grade_sync_032.py')

TARGETED_MODULES=('test_relic_grade_sync_032','test_run_reuse_guards_032',
    'test_difficulty_relics','test_inventory_tools','test_sampling_flow')


def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def baseline_behaviors():
    def load(name,file):
        spec=importlib.util.spec_from_file_location('rouge.'+name,ROOT/'.cache/batch-032-before'/file)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    old_icons=load('_previous_relic_recognition_032','rouge/relic_recognition.py')
    old=load('_previous_run_state_032','rouge/run_state.py')
    old.resolve_difficulty_icons=old_icons.resolve_difficulty_icons
    old.resolve_owned_icons=old_icons.resolve_owned_icons
    with tempfile.TemporaryDirectory() as folder:
        previous=old.RunState(Path(folder)/'old.json');now=RunState(Path(folder)/'new.json')
        for run in (previous,now):
            at=run.state['started_at']+1;run.apply(bar([icon()],1),at);run.apply(grade(10),at+1)
        assert previous.held_relic_ids()==[] and now.held_relic_ids()==[BASE+'_c']
        for run in (previous,now):
            at=run.state['last_read']+1;run.apply({**bar([icon()],1),**grade(10)},at);run.apply(grade(3),at+1)
        assert previous.held_relic_ids()==[BASE+'_c'] and now.held_relic_ids()==[BASE+'_a']
    return {'late_grade_before':[],'late_grade_after':[BASE+'_c'],
        'grade_correction_before':[BASE+'_c'],'grade_correction_after':[BASE+'_a']}


def meaning(observation):
    run=observation.get('run') or {}
    cfg=run.get('config',{})
    return {'page':observation['page'],'nodes':observation['nodes'],'stage':observation['stage'],
        'operator':observation['operator'],'map':observation['map'],'node_content':observation['node_content'],
        'relics':run.get('relics'),'tools':run.get('tactical_tools'),'crew_count':run.get('crew_count'),
        'operators':run.get('operators'),'resources':run.get('resources'),
        'config':{k:{x:y for x,y in v.items() if x not in ('captured_at','reused_from_run','badge')}
                  for k,v in cfg.items()}}


def paired_replays():
    rows=[]
    with tempfile.TemporaryDirectory() as folder:
        for name in ('run-map-closed.png','exploration-map.png'):
            image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,np.uint8),1)
            baseline=ScreenReader();reused=ScreenReader()
            first=baseline.read(image)
            memory=RunState(Path(folder)/(name+'.json'));memory.apply(first['run'],memory.state['started_at']+1)
            context=memory.recognition_context();reused.read(image,run_context=context)
            cold=[];warm=[];baseline_calls=memory_calls=0
            before=len(memory.state['history']);settings=copy.deepcopy(memory.state['config'])
            for attempt in range(3):
                changed=image.copy();changed[400:408,40:48]=50+attempt*60
                with patch('rouge.run_badges.find_squad_badge',wraps=run_badges.find_squad_badge) as searched:
                    old=baseline.read(changed)
                    baseline_calls+=searched.call_count
                with patch('rouge.run_badges.find_squad_badge',wraps=run_badges.find_squad_badge) as searched:
                    current=reused.read(changed,run_context=context)
                    memory_calls+=searched.call_count
                assert meaning(old)==meaning(current),name
                assert current['run']['config_reuse']['fields']==['difficulty','squad'],name
                memory.apply(current['run'],memory.state['started_at']+2+attempt)
                for key in ('difficulty','squad'):
                    assert memory.state['config'][key]==settings[key],(name,key)
                # Zone remains a current observation, with its own fresh timestamp.
                # Neither repeated settings nor this unchanged zone invent history.
                assert len(memory.state['history'])==before,name
                cold.append(old['performance']['total_ms']);warm.append(current['performance']['total_ms'])
            assert baseline_calls==3 and memory_calls==0
            row={'sample':name,'trials':3,'without_run_memory_ms':cold,'with_run_memory_ms':warm,
                 'without_memory_median_ms':statistics.median(cold),'with_memory_median_ms':statistics.median(warm),
                 'badge_searches_before':baseline_calls,'badge_searches_after':memory_calls,
                 'semantic_equal':True,'original_config_timestamps_preserved':True}
            rows.append(row);print(json.dumps({'replay':name,'before_ms':row['without_memory_median_ms'],
                'after_ms':row['with_memory_median_ms'],'badge_searches':[baseline_calls,memory_calls]}),flush=True)
        # Explicitly visible current information corrects cached settings.
        panel=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-info-trade.png',np.uint8),1)
        observed=ScreenReader().read(panel,run_context=context)
        assert observed['run']['config']['difficulty']['value']==10
        assert observed['run']['config']['squad']['id']=='rogue_6_band_20'
        assert not observed['run']['config']['difficulty'].get('reused_from_run')
        assert not observed['run']['config']['squad'].get('reused_from_run')
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--targeted',action='store_true')
    args=parser.parse_args()
    start=time.perf_counter();folder=ROOT/'.cache/relic-032';folder.mkdir(parents=True,exist_ok=True)
    hashes={name:sha(name) for name in FILES}
    print('Running current-source targeted checks.' if args.targeted else
          'Running full current suite with explicit historical skips.',flush=True)
    names=['tests.'+n for n in TARGETED_MODULES] if args.targeted else [
        'tests.'+p.stem for p in sorted((ROOT/'tests').glob('test_*.py'))]
    suite=unittest.defaultTestLoader.loadTestsFromNames(names)
    log_name='targeted-tests.log' if args.targeted else 'tests.log'
    with (folder/log_name).open('w',encoding='utf-8') as log:
        tested=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    assert tested.wasSuccessful(),str(folder/log_name)
    print(json.dumps({'current_tests_passed':tested.testsRun-len(tested.skipped),
        'historical_skipped':len(tested.skipped)}),flush=True)
    paired=baseline_behaviors();replays=paired_replays()
    evidence=json.loads((ROOT/'.cache/research/relics-032/evidence.json').read_text(encoding='utf-8'))
    assert evidence['groups']==config_data()['difficulty_upgrade_relic_groups']
    assert evidence['derived_config_sha256']==sha('rouge/data/run-config.json')
    assert hashes=={name:sha(name) for name in FILES}
    assert sha('rouge/data/relic-mechanics.json')==json.loads((ROOT/'FINAL_0.31_VERIFICATION.json').read_text(encoding='utf-8'))['source_sha256']['rouge/data/relic-mechanics.json']
    receipt={'version':'0.32.0','passed':True,'verified_at':time.time(),
        'tests_run':tested.testsRun,'current_tests_passed':tested.testsRun-len(tested.skipped),
        'test_scope':'current_source_targeted' if args.targeted else 'full_current_suite',
        'test_modules':names,'test_log':str((folder/log_name).relative_to(ROOT)),
        'test_log_sha256':sha(str((folder/log_name).relative_to(ROOT))),
        'new_tests':26,'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':t.id(),'reason':r} for t,r in tested.skipped],
        'failures':len(tested.failures),'errors':len(tested.errors),
        'difficulty_groups':13,'family_variants':52,'grade_cases':208,'paired_behaviors':paired,
        'paired_replays':replays,'explicit_visible_panel_overrides_memory':True,
        'source_hashes':hashes,'relic_mechanics_unchanged':True,
        'chat_requests':0,'game_actions':0,'new_live_capture_measurements':0,
        'elapsed_seconds':time.perf_counter()-start,
        'limits':['Paired historical replay timings are not live all-page performance or full-inventory accuracy.',
            'Only confirmed same-run squad and difficulty skip repeat badge work; changing fields remain current reads.',
            'Exact owned descriptions override grade inference with a discrepancy; missing grade/cross-family ambiguity remains unknown.']}
    if args.targeted:
        full_file='.cache/relic-032/full-suite-before-guards.json'
        full=json.loads((ROOT/full_file).read_text(encoding='utf-8'))
        assert full['passed'] and full['test_log_sha256']==sha(full['test_log'])
        changed=[n for n,h in full['source_hashes'].items() if sha(n)!=h]
        assert set(changed)=={'rouge/run_state.py','rouge/run_config.py','scripts/verify_relic_grade_sync_032.py'},changed
        assert all(sha(n.replace('.','/')+'.py')==h for n,h in full['test_module_sha256'].items())
        receipt['full_regression_before_final_guards']={
            'receipt':full_file,'sha256':sha(full_file),'current_tests_passed':full['current_tests_passed'],
            'historical_combat_tests_skipped':full['historical_combat_tests_skipped'],
            'changed_source_files_since_full_suite':changed}
        receipt['limits'].append('334 full regression passes precede the final run-ID/geometry guards; '
            'current-source targeted checks, replay and UI checks cover those final changes separately.')
    (ROOT/'RECOGNITION_0.32_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','historical_combat_tests_skipped','grade_cases','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()

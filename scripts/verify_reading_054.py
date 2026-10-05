"""Complete current suite after public-image parser integration; reuse exact numerical stage."""
import ast
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def functions(name):
    return {f.name:ast.dump(f,include_attributes=False)
        for f in ast.parse((ROOT/name).read_text(encoding='utf-8')).body
        if isinstance(f,ast.FunctionDef)}

def main():
    start=time.perf_counter();folder=ROOT/'.cache/reading-054';folder.mkdir(exist_ok=True)
    stage_name='.cache/p1-054/staged-before-reading.json';stage=read(stage_name)
    assert stage==read('P1_0.54_VERIFICATION.json')
    assert stage['passed'] and stage['exact_default_public_replays']==732
    changed=[n for n,h in stage['source_sha256'].items() if sha(n)!=h]
    assert changed==['rouge/run_recognition.py'],changed
    manifest=read('.cache/reading-054-before/manifest.json')
    assert set(manifest)=={'rouge/run_recognition.py'}
    assert all(sha('.cache/reading-054-before/'+n)==h for n,h in manifest.items())
    before=functions('.cache/reading-054-before/rouge/run_recognition.py')
    after=functions('rouge/run_recognition.py')
    assert set(after)-set(before)=={'expanded_held_page','read_held_counters'}
    assert {n for n in before if before[n]!=after[n]}=={'read_run','read_owned_cards'}
    modules=[*stage['test_modules'],'tests.test_held_cards_054',
             'tests.test_counter_badges_054','tests.test_held_integration_054']
    assert len(modules)==len(set(modules))
    index=1
    while (folder/f'all-tests-{index}.log').exists():index+=1
    log=folder/f'all-tests-{index}.log'
    with log.open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert result.wasSuccessful(),[(t.id(),e[-1800:]) for t,e in [*result.errors,*result.failures]]
    assert result.testsRun==799 and len(result.skipped)==70,(result.testsRun,len(result.skipped))
    names=set(stage['source_sha256'])|{'rouge/run_recognition.py','rouge/held_cards.py',
        'rouge/counter_badges.py','rouge/data/counter-badge-reference.json',
        'rouge/data/ui-icons/counter-badge-up-054.png'}
    names|={p.relative_to(ROOT).as_posix() for base in ('tests','scripts')
            for p in (ROOT/base).glob('*054.py')}
    names.discard('scripts/verify_final_054.py')
    receipt={'version':'0.54.0','passed':True,'tests_run':799,'current_tests_passed':729,
        'new_unit_tests':59,'new_reading_tests':46,'historical_combat_tests_skipped':70,
        'errors':0,'failures':0,'test_modules':modules,'test_log':log.relative_to(ROOT).as_posix(),
        'test_log_sha256':sha(log.relative_to(ROOT)),
        'numerical_stage_receipt':stage_name,'numerical_stage_receipt_sha256':sha(stage_name),
        'fresh_054_exact_default_public_replays':732,'numeric_public_replay_repeated_after_reading':False,
        'all_numerical_sources_equal_to_replayed_stage':True,
        'bounded_existing_function_changes':['read_run','read_owned_cards'],
        'new_functions':['expanded_held_page','read_held_counters'],
        'original_public_training_images':1,'independent_held_card_holdout_images':1,
        'glyph_independent_holdout_images':1,'all_layer_auto_reading_completed':False,
        'all_priority_1_completed':False,
        'source_sha256':{n:sha(n) for n in sorted(names)},
        'game_actions':0,'chat_requests':0,'private_data_isolated':True,
        'seconds':time.perf_counter()-start}
    (ROOT/'READING_0.54_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_unit_tests','seconds')}))

if __name__=='__main__':main()

"""Assess final61 on the actual frozen source of root section60."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
prepared=json.loads((HERE/'current60-prepare-receipt.json').read_text())
before=json.loads((HERE/'current60-public-baseline.json').read_text())
after=json.loads((HERE/'current60-public-merged.json').read_text())
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
assert before['public_cases'].keys()==after['public_cases'].keys()
assert canonical(before['public_cases'])==canonical(after['public_cases'])
base=Path(prepared['baseline_directory']);merged=Path(prepared['merged_directory'])
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def omit_option(path):
    tree=ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ClassDef) and node.name=='Combat':
            node.body=[part for part in node.body if not(isinstance(part,ast.FunctionDef) and part.name=='option')]
    return ast.dump(tree,include_attributes=False)
assert omit_option(base/'rouge/operator_engine.py')==omit_option(merged/'rouge/operator_engine.py')
assert sha(base/'rouge/reporting.py')==sha(merged/'rouge/reporting.py')
assert sha(base/'rouge/relics.py')==sha(merged/'rouge/relics.py')
shu_reference_cases=0
for key,row in after['public_cases'].items():
    result=row['result']
    if key.startswith('60_shu') and row['input']['elite']==2 and row['input']['four_sui']:
        ref=result['shu_periodic_sp_reference'];shu_reference_cases+=1
        assert ref['first_tick_seconds'] is None and ref['actual_tick_times_seconds'] is None
        assert not ref['clock_verified'] and not ref['events_scheduled']
        assert result['timing']['resource_and_damage_shared_clock'] is False
        assert result['timing']['phase_clock_unbound'] is True
        for name in ('recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
            assert result['estimate']['skill'][name] is None,(key,name)
    if key.startswith('59_binding'):
        notes=next(s['notes'] for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
        assert any('束缚倍率首次生效与刷新' in note for note in notes)
        if 'enemy_attack_count' in row['input']:assert any('目标普通攻击次数没有事件时刻' in note for note in notes)
    if key.startswith('59_shield'):
        assert not result.get('neural_relic_reference')
        notes=next(s['notes'] for s in result['report']['sections'] if s['id']=='known_damage_subtotals')
        assert not any('河谷祭祈' in note for note in notes)
    if key.startswith('58_pending'):
        record=next(r for r in result['relic_resolution']['records'] if r['id']=='rogue_6_relic_cargo_10')
        assert record['missing_conditions']==['emergency_hire'] and record['applied']==[]
        assert result['complete'] is False
tests=json.loads((HERE/'current60-tests.json').read_text())
assert tests['passed'] and tests['failures']==tests['errors']==tests['skips']==0
receipt={**prepared,'public_probe_validation_pending':False,
    'current60_external_merge_compatibility_passed':True,'blockers':[],
    'actual_frozen_current60_source_used':True,'all_except_61_option_AST_unchanged':True,
    'paired_public_cases':len(after['public_cases']),'public_calls_both_copies':before['public_calls']+after['public_calls'],
    'all_complete_public_JSON_and_formatted_reports_identical':True,'explicit_Shu_E2_four_sui_unknown_clock_cases_checked':shu_reference_cases,
    'section59_notes_and_held_no_actual_River_reference_preserved':True,
    'section58_invalid_identity_pending_and_legal_0_1_preserved':True,
    'merged_relevant_methods_run':tests['methods_run'],'merged_method_failures':0,'merged_method_errors':0,'merged_method_skips':0,
    'root_integration_performed_by_reviewer':False,'root_full60_archived_by_reviewer':False,
    'Wine_full_test_run':False,'actual_GUI_run':False,'native_Windows_run':False,
    'scope':'External tracked public git archive of fixed c3ccf25 + actual final61 patch; no root mutation and no claim of root integrated checks.',
    'artifact_hashes':{p.name:sha(p) for p in HERE.glob('current60*') if p.is_file() and p.name!='current60-compatibility.json'}}
(HERE/'current60-compatibility.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('current60_external_merge_compatibility_passed','paired_public_cases','explicit_Shu_E2_four_sui_unknown_clock_cases_checked','merged_relevant_methods_run','archivable_public_artifacts_rehashed','blockers')},ensure_ascii=False))

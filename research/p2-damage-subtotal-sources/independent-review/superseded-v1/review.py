"""Independent small-probe comparison and pinned-source review."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-derived-report-059')
AUDIT=Path('/workspace/.continuation/p2-after-055-audit/derived-report')
BASE=AUDIT/'frozen'; DRAFT=AUTHOR/'draft'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((AUDIT/'freeze-manifest.json').read_text())
baseline_drift=[name for name,expected in freeze['files'].items() if sha(BASE/name)!=expected]
draft_changes=[name for name,expected in freeze['files'].items() if sha(DRAFT/name)!=expected]
assert not baseline_drift,baseline_drift
assert draft_changes==['rouge/reporting.py'],draft_changes
assert sha(BASE/'rouge/reporting.py')==sha(AUTHOR/'reporting.baseline-055.py')
assert sha(DRAFT/'rouge/reporting.py')==sha(AUTHOR/'reporting.draft-055.py')
patch=AUTHOR/'section59.patch'
assert sha(patch)=='701007affd57b992ef6390b4cf5cae65e140bf09c18d29e4f63a7bceab6aee2d'
patch_text=patch.read_text()
assert [line for line in patch_text.splitlines() if line.startswith('+++ ')]==[
    '+++ b/rouge/reporting.py','+++ b/tests/test_damage_subtotal_sources.py']

source=json.loads((AUDIT/'source-receipt.json').read_text())
tables={}
for key,entry in source['tables'].items():
    path=Path(entry['reused_local_path'])
    assert sha(path)==entry['sha256']
    assert path.stat().st_size==entry['bytes']
    tables[key]=json.loads(path.read_text())
selectors=source['selectors']
skill_key='skill_table.skchr_phatm2_1.levels[9]'
assert tables['skill_table']['skchr_phatm2_1']['levels'][9]==selectors[skill_key]
for i in (0,1):
    key=f'character_table.char_1042_phatm2.talents[{i}].candidates[PHASE_2,potentialRank=0]'
    selected=[c for c in tables['character_table']['char_1042_phatm2']['talents'][i]['candidates']
              if c['unlockCondition']['phase']=='PHASE_2' and c['requiredPotentialRank']==0]
    assert selected==[selectors[key]],(key,len(selected))

old=json.loads((HERE/'public-baseline.json').read_text())
new=json.loads((HERE/'public-draft.json').read_text())
assert old['cases'].keys()==new['cases'].keys()
changed=[];unchanged=[];cases={}
def subtotal_notes(row):
    matches=[s for s in row['result']['report']['sections'] if s['id']=='known_damage_subtotals']
    assert len(matches)<=1
    return matches[0]['notes'] if matches else None
def remove_allowed_notes(result):
    cloned=deepcopy(result)
    for section in cloned['report']['sections']:
        if section['id']=='known_damage_subtotals':section['notes']=[]
    return cloned
for key,after in new['cases'].items():
    before=old['cases'][key]
    assert before['input']==after['input'],key
    assert remove_allowed_notes(before['result'])==remove_allowed_notes(after['result']),key
    notes=subtotal_notes(after)
    old_notes=subtotal_notes(before)
    if before==after:unchanged.append(key)
    else:
        assert old_notes!=notes,key
        changed.append(key)
    if notes:
        assert any('不能当作完整' in note for note in notes),key
        if after['result'].get('neural_s1_reference'):
            assert any('束缚倍率首次生效与刷新' in note for note in notes),key
        if after['result'].get('neural_incoming_reference'):
            assert any('目标普通攻击次数没有事件时刻' in note for note in notes),key
        if after['result'].get('neural_relic_reference'):
            assert sum('河谷祭祈' in note for note in notes)==1,key
        if after['result'].get('neural_skill_reference') or after['result'].get('neural_bait_reference'):
            assert old_notes[0]==notes[0],key
    if 'rogue_6_relic_fight_22' not in after['input']['relic_ids']:
        assert '河谷祭祈' not in after['formatted'],key
    cases[key]={'input':after['input'],'before_result':before['result'],'after_result':after['result'],
                'before_formatted':before['formatted'],'after_formatted':after['formatted'],
                'subtotal_notes_before':old_notes,'subtotal_notes_after':notes,'all_non_note_fields_equal':True}
tests=json.loads((HERE/'independent-tests.json').read_text())
assert tests['passed'] and not tests['failures'] and not tests['errors'] and not tests['skips']
(HERE/'public.json').write_text(json.dumps({'frozen_head':freeze['head'],'paired_public_cases':len(cases),
    'cases':cases,'caller_inputs_preserved':True},ensure_ascii=False,indent=2)+'\n')
receipt={'independent_review_passed':True,'findings':[],'blockers':[],
    'baseline_head':freeze['head'],'reviewed_patch':str(patch),'reviewed_patch_sha256':sha(patch),
    'frozen_manifest_files_checked':len(freeze['files']),'baseline_source_drift':baseline_drift,'draft_source_changes':draft_changes,
    'pinned_game_commit':source['source_commit'],'pinned_tables_fresh_local_hash_check':True,
    'exact_pinned_selectors_checked':list(selectors),'source_scope':'Already-known reference flags/unknown causes only; no mechanism addition',
    'paired_small_public_cases':len(cases),'public_calls_both_packages':len(cases)*2,
    'changed_subtotal_notes_only':len(changed),'unchanged_full_public_cases':len(unchanged),
    'all_numeric_timing_None_scope_non_note_fields_equal':True,'caller_inputs_preserved':True,
    'binding_incoming_River_combination_notes_visible':True,'S3_bait_primary_notes_preserved':True,
    'tests_run':tests['tests_run'],'new_tests_passed':tests['tests_run'],
    'independent_large_matrix_rerun':False,'author_large_matrix_reused_as_read_only_evidence':False,
    'root_tracked_edits':0,'draft_edits':0,'private_state_read':False,'game_actions':0,
    'native_Windows_tested':False,'Wine_tested':False,'actual_GUI_tested':False,
    'remaining_validation':'Frozen HEAD55 draft review; root must run fresh integration after sections 56–58 and required batch checks.',
    'artifacts':{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='receipt.json'}}
(HERE/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ['independent_review_passed','frozen_manifest_files_checked','paired_small_public_cases','changed_subtotal_notes_only','unchanged_full_public_cases','tests_run','blockers']},ensure_ascii=False))

"""Source-derived eligibility, complete saved JSON proof, and independent probes."""
import ast
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-four-sui-text-input-062')
AUDIT=Path('/workspace/.continuation/p2-boolean-option-audit-062')
BASE=AUTHOR/'baseline060';DRAFT=AUTHOR/'draft062';COMBINED=AUTHOR/'combined061062'
ERROR={'type':'ValueError','message':'four_sui 不接受文本条件；请使用布尔值。'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
canonical=lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
freeze=json.loads((AUTHOR/'freeze-receipt060.json').read_text())
drift=[rel for rel,expected in freeze['files'].items() if sha(BASE/rel)!=expected]
changes=[rel for rel,expected in freeze['files'].items() if sha(DRAFT/rel)!=expected]
assert not drift and changes==['rouge/operator_engine.py']
patch=AUTHOR/'section62.patch'
assert sha(patch)=='82ab295699731f83b7c6ad3caaed64e77a9c42d6e2df7e7803de870892f58200'
assert freeze['declared_error_literal']==ERROR['message']
assert [line for line in patch.read_text().splitlines() if line.startswith('+++ ')]==[
    '+++ b/rouge/operator_engine.py','+++ b/tests/test_four_sui_text_input.py']
base_engine=(BASE/'rouge/operator_engine.py').read_bytes()
draft_engine=(DRAFT/'rouge/operator_engine.py').read_bytes()
addition=("            if '天有四时' in self.tv and isinstance(self.s.get('four_sui'),str):\r\n"
          "                raise ValueError('four_sui 不接受文本条件；请使用布尔值。')\r\n").encode()
assert addition in draft_engine and draft_engine.replace(addition,b'',1)==base_engine
source=json.loads((AUDIT/'source-receipt.json').read_text())
raw={}
for name,entry in source['sources'].items():
    p=Path(entry['path']);assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
    raw[name]=json.loads(p.read_text())
original=raw['character_table']['char_2025_shu']['talents'][1]['candidates'][0]
assert raw['character_table']['char_2025_shu']['talents'][1]['candidates']==source['selectors']['character_table.char_2025_shu.talents[1].candidates']
assert original['unlockCondition']=={'phase':'PHASE_2','level':1}
assert original['requiredPotentialRank']==0 and original['name']=='天有四时'
assert original['prefabKey']=='2' and original['isHideTalent'] is False
assert {e['key']:e['value'] for e in original['blackboard']}=={
    'max_hp':.12,'attack_speed':12.0,'atk':.12,'interval':4.0,'sp':1.0}
profile=json.loads((BASE/'rouge/data/catalog.json').read_text())['operators']['char_2025_shu']
assert len(profile['talents'][1])==1
normalized=profile['talents'][1][0]
assert normalized['name']=='天有四时' and normalized['phase']==2 and normalized['level']==1 and normalized['potential_rank']==0
assert canonical(normalized['values'])==canonical({e['key']:e['value'] for e in original['blackboard']})
options=next(ast.literal_eval(n.value) for n in ast.parse((BASE/'rouge/operator_options.py').read_text()).body
             if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets))
four_controls=[row for row in options['char_2025_shu'] if row[0]=='four_sui']
assert len(four_controls)==1 and four_controls[0][2] is False and four_controls[0][4]==(1,2,3)
def methods(path):
    tree=ast.parse(path.read_text())
    combat=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Combat')
    return {n.name:ast.dump(n,include_attributes=False) for n in combat.body if isinstance(n,ast.FunctionDef)}
base_methods=methods(BASE/'rouge/operator_engine.py')
draft_methods=methods(DRAFT/'rouge/operator_engine.py')
assert [key for key in base_methods if base_methods[key]!=draft_methods[key]]==['apply_self_talents']
combined_methods=methods(COMBINED/'rouge/operator_engine.py')
assert combined_methods['apply_self_talents']==draft_methods['apply_self_talents']
final61_methods=methods(Path('/workspace/.continuation/p2-integer-option-audit-061/draft/rouge/operator_engine.py'))
assert combined_methods['option']==final61_methods['option']
assert [key for key in base_methods if base_methods[key]!=combined_methods[key]]==['option','apply_self_talents']

small_old=json.loads((HERE/'public-baseline062.json').read_text())
small_new=json.loads((HERE/'public-draft062.json').read_text())
assert small_old['cases'].keys()==small_new['cases'].keys()
small_changed=[];small_preserved=[]
for key,before in small_old['cases'].items():
    after=small_new['cases'][key]
    assert canonical(before['input'])==canonical(after['input'])
    if before['expected_new_text_error']:
        assert before['outcome']['error'] is None
        assert after['outcome']=={'result':None,'error':ERROR},key
        small_changed.append(key)
    else:
        assert canonical(before['outcome'])==canonical(after['outcome']),key
        small_preserved.append(key)
        result=after['outcome']['result']
        if result and result.get('shu_periodic_sp_reference'):
            ref=result['shu_periodic_sp_reference']
            assert ref['first_tick_seconds'] is None and not ref['events_scheduled']
            assert result['estimate']['skill']['recharge_seconds'] is None

with gzip.open(AUTHOR/'baseline-matrix.json.gz','rt',encoding='utf-8') as stream:old=json.load(stream)
with gzip.open(AUTHOR/'draft-matrix.json.gz','rt',encoding='utf-8') as stream:new=json.load(stream)
assert old['cases'].keys()==new['cases'].keys() and len(old['cases'])==5189
large_changed=[];large_preserved=[];olderrors=0
for key,before in old['cases'].items():
    after=new['cases'][key];args=before['scenario']
    assert canonical(args)==canonical(after['scenario'])
    # Eligibility is derived from the checked original phase/level/potential
    # and an already successful baseline public input, never a result flag.
    eligible=(args['operator']=='char_2025_shu' and args.get('elite',2)==2
              and isinstance(args.get('four_sui'),str) and before['outcome']['error'] is None)
    if eligible:
        assert after['outcome']=={'result':None,'error':ERROR},key
        large_changed.append(key)
    else:
        assert canonical(before)==canonical(after),key
        large_preserved.append(key)
        if before['outcome']['error'] is not None:olderrors+=1
assert len(large_changed)==420 and len(large_preserved)==4769 and olderrors==7
comparison=json.loads((AUTHOR/'matrix-comparison.json').read_text())
assert set(comparison['changed_cases'])==set(large_changed)
assert sha(AUTHOR/'baseline-matrix.json.gz')==comparison['baseline_gzip_sha256']
assert sha(AUTHOR/'draft-matrix.json.gz')==comparison['draft_gzip_sha256']
tests_draft=json.loads((HERE/'tests-draft062.json').read_text())
tests_combined=json.loads((HERE/'tests-combined061062.json').read_text())
for tests in (tests_draft,tests_combined):assert tests['passed'] and not tests['failures'] and not tests['errors'] and not tests['skips']
receipt={
 'independent_review_passed':True,'findings':[],'blockers':[],
 'baseline_head':freeze['baseline_head'],'reviewed_patch_sha256':sha(patch),'reviewed_patch_bytes':patch.stat().st_size,
 'baseline_manifest_files_rehashed':len(freeze['files']),'baseline_source_drift':drift,'draft_changed_existing_source_files':changes,
 'only_exact_2line_guard_added_to_engine':True,
 'raw_pinned_game_commit':source['source_commit'],'source_tables_freshly_rehashed':True,
 'exact_talent_selector':'character_table.char_2025_shu.talents[1].candidates[0]',
 'exact_talent_candidate':original,'qualification_source':'PHASE_2, level1, requiredPotentialRank0, selected_talents existing eligibility; not result-reference flags',
 'UI_checkbox_default_False_and_skills_1_2_3_verified':True,
 'historical_readonly_audit_implemented_policy_false_preserved':source['implemented_policy'] is False,
 'independent_paired_public_cases':len(small_old['cases']),
 'independent_public_calls_both_packages':small_old['public_calls']+small_new['public_calls'],
 'independent_qualified_text_exact_errors':len(small_changed),'independent_complete_outcomes_preserved':len(small_preserved),
 'large_completed_JSON_pairs_independently_recompared_no_calculation_rerun':5189,
 'large_qualified_raw_text_exact_errors_verified':420,'large_complete_JSON_outcomes_preserved':4769,'large_old_errors_preserved':7,
 'independent_draft_test_methods_run':tests_draft['methods_run'],'independent_combined61_62_test_methods_run':tests_combined['methods_run'],
 'combined61_guard_option_AST_exact_match':True,'combined62_selected_talent_guard_AST_exact_match':True,
 'root_tracked_edits':0,'author_draft_edits':0,'prior_readonly_audit_edits':0,'private_state_read':False,'game_actions':0,
 'Wine_validated':False,'actual_GUI_validated':False,'native_Windows_validated':False,
 'remaining_validation':'Frozen HEAD60 draft and author external combined61/62 only; root fresh integration and scheduled batch checks remain separately required.',
 'source_receipt_and_prior_audit_hashes':{'source-receipt.json':sha(AUDIT/'source-receipt.json'),'NOTE.md':sha(AUDIT/'NOTE.md')},
 'artifact_hashes':{p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='receipt062.json'},
}
(HERE/'receipt062.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('independent_review_passed','independent_paired_public_cases','independent_qualified_text_exact_errors','independent_complete_outcomes_preserved','independent_draft_test_methods_run','independent_combined61_62_test_methods_run','blockers')},ensure_ascii=False))

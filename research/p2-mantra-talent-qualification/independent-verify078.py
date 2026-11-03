"""Independent source/patch/full JSON verification; uses saved matrix results only."""
import ast,collections,copy,hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;REPO=Path('/workspace/rougezhushou')
COMMIT='225cb66dc89143a3cd3a884bd6c62f47ed9d36bc'
PATCH='947a2805987af8b5e33a40b9b247e4f152f6c6a9d3538d68db986b4c51d885f8'
ENGINE='80b19e19950b45fa058d5ecb7b94d4991c06f5f9a70cac9e3854c3c429aa72d8'
TEST='fcc2b2176e3642e7d86083039fcdc1955db8efc611587335dd65922876a1ef94'
OP='char_4204_mantra';NAME='麻痹触发天赋';LABEL='声明当前目标麻痹触发次数'
def read(name):return json.loads((P/name).read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return sha(canonical(v).encode())

raw=(P/'section78.patch').read_bytes();assert sha(raw)==PATCH and raw.count(b'diff --git ')==2
old=(P/'baseline/rouge/operator_engine.py').read_bytes();new=(P/'draft078/rouge/operator_engine.py').read_bytes()
before="                emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers)\r\n".encode()
after="                emit('麻痹触发天赋',attack*self.talent('噤声限域','atk_scale'),'elemental',triggers if '噤声限域' in self.tv else 0.0)\r\n".encode()
assert old.count(before)==1 and old.replace(before,after,1)==new
assert sha(new)==ENGINE and sha((P/'test_mantra_talent_qualification.py').read_bytes())==TEST
assert new.count(b'\r\n')==old.count(b'\r\n')==old.count(b'\n')
freeze=read('baseline-freeze078.json');assert freeze['commit']==COMMIT and freeze['file_count']==len(freeze['files'])==2372
tree=subprocess.run(['git','ls-tree','-r','-z',COMMIT],cwd=REPO,check=True,stdout=subprocess.PIPE).stdout
blobs={}
for row in tree.split(b'\0'):
    if not row:continue
    header,name=row.split(b'\t',1);_,kind,oid=header.decode().split(' ')
    if kind=='blob':blobs[name.decode()]=oid
for name,meta in freeze['files'].items():
    raw=(P/'baseline'/name).read_bytes()
    assert len(raw)==meta['bytes'] and sha(raw)==meta['sha256'],name
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[name],name
    if name!='rouge/operator_engine.py':assert raw==(P/'draft078'/name).read_bytes(),name
apply_dir=P/'independent-patch-application078'
if not apply_dir.exists():
    (apply_dir/'rouge').mkdir(parents=True);(apply_dir/'tests').mkdir()
    (apply_dir/'rouge/operator_engine.py').write_bytes(old);commands=[]
    for args in (['git','apply','--check',str(P/'section78.patch')],['git','apply',str(P/'section78.patch')]):
        result=subprocess.run(args,cwd=apply_dir,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        commands.append({'args':args,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==0,commands[-1]
else:
    commands=read('independent-patch-application078.json')['commands']
    assert len(commands)==2 and all(c['returncode']==0 for c in commands)
assert (apply_dir/'rouge/operator_engine.py').read_bytes()==new
assert (apply_dir/'tests/test_mantra_talent_qualification.py').read_bytes()==(P/'test_mantra_talent_qualification.py').read_bytes()
(P/'independent-patch-application078.json').write_text(json.dumps({'commands':commands,'two_files_exactly_rebuilt':True},indent=2)+'\n')

source=read('source-receipt078.json');assert source['baseline_commit']==COMMIT
tables={}
for name,meta in source['sources'].items():
    raw=Path(meta['path']).read_bytes()
    assert len(raw)==meta['bytes'] and sha(raw)==meta['sha256']
    tables[name]=json.loads(raw)
original=read('selected-original-objects078.json');owner=tables['character_table'][OP]
assert original['character_table_complete_selected_character']==owner
profile=read('baseline/rouge/data/catalog.json')['operators'][OP]
talents=owner['talents'][0]['candidates'];assert len(talents)==4
assert [(c['unlockCondition'],c['requiredPotentialRank'])for c in talents]==[
    ({'phase':'PHASE_1','level':1},0),({'phase':'PHASE_1','level':1},4),
    ({'phase':'PHASE_2','level':1},0),({'phase':'PHASE_2','level':1},4)]
assert [{b['key']:b['value']for b in c['blackboard']}for c in talents]==[
    {'atk_scale':1.0,'prob':.08},{'atk_scale':1.1,'prob':.11},
    {'atk_scale':1.35,'prob':.1},{'atk_scale':1.45,'prob':.13}]
for raw,n in zip(talents,profile['talents'][0],strict=True):
    assert n=={'phase':int(raw['unlockCondition']['phase'][-1]),'level':raw['unlockCondition']['level'],
              'potential_rank':raw['requiredPotentialRank'],'name':raw['name'],'description':raw['description'],
              'values':{b['key']:b['value']for b in raw['blackboard']}}
for number,(character_skill,normal)in enumerate(zip(owner['skills'],profile['skills'],strict=True),1):
    saved=original['skills_complete'][str(number)];skill=tables['skill_table'][character_skill['skillId']]
    assert saved['character_skill_complete']==character_skill and saved['skill_table_complete']==skill
    assert normal['id']==character_skill['skillId']
    assert normal['unlock_elite']==int(character_skill['unlockCond']['phase'][-1])
    assert len(normal['levels'])==len(skill['levels'])==10
    for raw,n in zip(skill['levels'],normal['levels'],strict=True):
        assert n['name']==raw['name']and n['duration']==raw['duration']and n['description']==raw['description']
        assert n['duration_type']==raw['durationType']and n['sp_type']==raw['spData']['spType']
        assert n['sp_cost']==raw['spData']['spCost']and n['initial_sp']==raw['spData']['initSp']
        assert n['sp_increment']==raw['spData']['increment']and n['max_charges']==raw['spData']['maxChargeTime']
        assert n['values']=={b['key']:b['value']for b in raw['blackboard']}
options_tree=ast.parse((P/'baseline/rouge/operator_options.py').read_text())
assignment=next(n for n in options_tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OPTIONS'for t in n.targets))
options=ast.literal_eval(assignment.value)
control=next(r for r in options[OP]if r[0]=='palsy_triggers')
assert control==('palsy_triggers','窗口内目标麻痹触发次数',0,10000,(1,2,3))
assert type(control[2])is int
app=(P/'baseline/rouge/app.py').read_text()
assert 'elif isinstance(default,int):'in app and 'widget=QSpinBox();widget.setRange(0,maximum);widget.setValue(default)'in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()'in app

def compare(left,right,key):
    index={canonical(r['request']):r for r in left};counts=collections.Counter()
    assert len(left)==len(right)
    for a,b in zip(left,right,strict=True):
        assert a['request']==b['request']
        if 'group'in a:assert a['group']==b['group']
        if 'label'in a:assert a['label']==b['label']
        if 'error'in a or 'error'in b:
            assert canonical(a.get('error'))==canonical(b.get('error'))
            counts['prior_complete_errors_unchanged']+=1;continue
        old=a[key];new=b[key]
        if 'full_result_sha256'in a:
            assert digest(old)==a['full_result_sha256']and digest(new)==b['full_result_sha256']
        req=a['request'];locked=req['operator']==OP and req.get('elite',2)==0 and float(req.get('palsy_triggers',0))>0
        if locked:
            zero=index[canonical({**req,'palsy_triggers':0})]
            expected=copy.deepcopy(zero[key]);declared=float(req['palsy_triggers'])
            refs=[expected['external_event_reference']]
            if 'window_reference'in refs[0]:refs.append(refs[0]['window_reference'])
            for ref in refs:
                matches=[r for r in ref['parameter_rows']if r[0]==LABEL]
                assert len(matches)==1;matches[0][1]=declared
            sections=[s for s in expected['report']['sections']if s['id']=='external_events'];assert len(sections)==1
            metrics=[m for m in sections[0]['metrics']if m['key']=='parameter_0'and m['label']==LABEL]
            assert len(metrics)==1;metrics[0]['value']=declared
            assert canonical(expected)==canonical(new)
            c=next(c for c in new['components']if c['name']==NAME)
            assert c['hits']==c['per_hit']==c['total']==0 and 'actual_total'not in c
            counts['locked_matches_complete_old_zero_count_plus_only_raw_metadata']+=1
        else:
            assert canonical(old)==canonical(new)
            counts['complete_json_unchanged']+=1
        if req['operator']==OP and req.get('elite',2)>0 and float(req.get('palsy_triggers',0))>0 and (req.get('base_attack')==0 or req.get('enemy_elemental_resistance')==100):
            c=next(c for c in new['components']if c['name']==NAME)
            assert c['hits']>0 and c['per_hit']==0 and c['actual_total']is None and new['total_damage']is None
    return {'paired_scenarios':len(left),'counts':dict(counts)}

main_before=read('baseline-results078.json');main_after=read('draft-results078.json')
extra_before=read('supplement-baseline-results078.json');extra_after=read('supplement-draft-results078.json')
assert main_before['paired_scenario_records']==main_after['paired_scenario_records']==1225
assert extra_before['paired_scenario_records']==extra_after['paired_scenario_records']==132
main=compare(main_before['records'],main_after['records'],'full_result')
extra=compare(extra_before['records'],extra_after['records'],'full_result')
aggregate=collections.Counter(main['counts']);aggregate.update(extra['counts'])
assert dict(aggregate)=={'locked_matches_complete_old_zero_count_plus_only_raw_metadata':106,
                        'complete_json_unchanged':982,'prior_complete_errors_unchanged':269}
for name in ('matrix-comparison078.json','supplement-matrix-comparison078.json'):
    assert read(name)['mismatches']==[]
summary=read('matrix-summary078.json')
assert summary['paired_scenarios']==1357 and summary['final_source_and_matrices_actual_public_calls']==2714
assert summary['total_actual_author_public_calls_including_initial_type_contract_draft']==3939
own_before=read('independent-baseline-results078.json');own_after=read('independent-draft-results078.json')
assert own_before['public_calls']==own_after['public_calls']==82
own=compare(own_before['records'],own_after['records'],'result')
assert sum(own['counts'].values())==82 and own['counts']['prior_complete_errors_unchanged']==12
tests=read('independent-new-tests078.json')
assert tests['new_tests_run']==tests['new_tests_passed']==9
assert tests['failures']==tests['errors']==tests['skipped']==0
assert tests['source_before_sha256']==tests['source_after_sha256']==ENGINE
related=read('related-tests078.json')
assert related['run']==related['passed']==83 and related['failures']==related['errors']==related['skipped']==0
receipt={
 'status':'independent_review_passed','blockers':[],'baseline_commit':COMMIT,
 'patch_sha256':PATCH,'changed_source_hashes':{'rouge/operator_engine.py':ENGINE},'new_test_sha256':TEST,
 'exact_CRLF_single_production_line_verified':True,
 'baseline_public_files_git_blob_verified':2372,'other_draft_public_files_unchanged':2371,
 'actual_patch_check_apply_two_files_exact_rebuild':True,
 'fresh_paired_scenarios':82,'public_calls':164,'fresh_outcome_counts':own,
 'new_tests_passed':9,'new_tests_skipped':0,
 'saved_author_pairs_strictly_recompared':1357,'saved_author_counts':dict(aggregate),
 'saved_main_pairs':1225,'saved_supplement_pairs':132,'saved_author_matrix_API_rerun_by_reviewer':False,
 'author_final_actual_calls_including8_reused_source_calls':2714,
 'initial_author_type_contract_draft_calls_preserved':1225,'total_actual_author_calls_including_initial':3939,
 'related_author_tests_read':{'passed':83,'skipped':0},
 'source_verified':{'fresh_character_table_sha256':source['sources']['character_table']['sha256'],
   'fresh_skill_table_sha256':source['sources']['skill_table']['sha256'],
   'complete_selected_character_all3_skills_match_saved_original_objects':True,
   'all4_exact_talent_candidates_checked':True,'qualification':'E1 level1/P1 or enhanced P5; E2 level1/P1 or enhanced P5',
   'all30_skill_level_projections_checked':True,
   'palsy_control':'Frozen source builds int QSpinBox0..10000 for all3 skills and serializes value(); no Qt execution by reviewer'},
 'bounded_conclusion':'Absent selected 噤声限域 does not create damage events. Positive E0 declarations exactly match the original same-request zero-count full result except the retained top/window parameter row and report declaration metric. Applicable known numerical output can recover from that zero control; actual global clock, source_possible, probabilistic retention, S3 overflow, qualified zero-damage source unknowns, neural/river uncertainty and all prior errors are preserved.',
 'legacy_zero_float_compatibility':'Final absent-talent emission uses0.0. Complete canonical JSON retains original zero-count outputs, including0.0; initial integer0 draft is separately retained, not used for final validation.',
 'initial_author_test_contract_errors':'Tuple metadata mutation and continuous phase/body hardcoded assumptions were corrected in tests. Frozen production remains the final one-line guard; saved histories retained.',
 'gui_executed':False,'wine_executed':False,'tracked_edits':False,'private_state_read':False,
 'artifact_hashes':{name:sha((P/name).read_bytes())for name in (
   'source-receipt078.json','selected-original-objects078.json','baseline-freeze078.json',
   'baseline-results078.json','draft-results078.json','supplement-baseline-results078.json','supplement-draft-results078.json',
   'independent-baseline-results078.json','independent-draft-results078.json',
   'independent-new-tests078.json','independent-new-tests078.log','independent-patch-application078.json')}
}
(P/'independent-review078.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'fresh_paired_scenarios':82,'public_calls':164,
 'new_tests_passed':9,'saved_author_pairs_strictly_recompared':1357,'fresh_counts':own['counts'],
 'receipt_sha256':sha((P/'independent-review078.json').read_bytes())},ensure_ascii=False))

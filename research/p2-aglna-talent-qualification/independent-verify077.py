"""Source, patch and strict saved/full public result verification; no new API calls."""
import collections,copy,hashlib,json,shutil,subprocess
from pathlib import Path

P=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
COMMIT='225cb66dc89143a3cd3a884bd6c62f47ed9d36bc'
PATCH_SHA='feda369157de7fa880b518bf73f2bdb3588d2e3c6c65042cc3042c4f2e55e058'
ENGINE_SHA='4317b5a22406f79ced7af4ae94bb52850143ece06753742cd734223e3dd54b83'
TEST_SHA='a98addaa26504aa3123175e5f67f103bf7f4204c0f380cface1dcb598343ca5d'
TALENT='飘浮大地之上'
def read(name):return json.loads((P/name).read_bytes())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(value):return sha(canonical(value).encode())

patch=(P/'section77.patch').read_bytes()
assert sha(patch)==PATCH_SHA
assert sha((P/'draft077/rouge/operator_engine.py').read_bytes())==ENGINE_SHA
assert sha((P/'test_aglna_talent_qualification.py').read_bytes())==TEST_SHA
assert patch.count(b'diff --git ')==2
old=(P/'baseline/rouge/operator_engine.py').read_bytes()
new=(P/'draft077/rouge/operator_engine.py').read_bytes()
before="            regular('magic',extra,name='飘浮大地之上')\r\n".encode()
after="            regular('magic',extra,times=1 if '飘浮大地之上' in self.tv else 0,name='飘浮大地之上')\r\n".encode()
assert old.count(before)==1 and old.replace(before,after,1)==new
assert old.count(b'\r\n')==new.count(b'\r\n')
assert old.count(b'\n')==old.count(b'\r\n')

freeze=read('baseline-freeze077.json')
assert freeze['commit']==COMMIT and freeze['file_count']==len(freeze['files'])==2408
tree=subprocess.run(['git','ls-tree','-r','-z',COMMIT],cwd=REPO,check=True,stdout=subprocess.PIPE).stdout
blobs={}
for item in tree.split(b'\0'):
    if not item:continue
    header,name=item.split(b'\t',1)
    mode,kind,oid=header.decode().split(' ')
    if kind=='blob':blobs[name.decode()]=oid
for name,meta in freeze['files'].items():
    raw=(P/'baseline'/name).read_bytes()
    assert len(raw)==meta['bytes'] and sha(raw)==meta['sha256'],name
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blobs[name],name
    if name!='rouge/operator_engine.py':assert (P/'draft077'/name).read_bytes()==raw,name

apply_dir=P/'independent-patch-application077'
if not apply_dir.exists():
    (apply_dir/'rouge').mkdir(parents=True)
    (apply_dir/'tests').mkdir()
    (apply_dir/'rouge/operator_engine.py').write_bytes(old)
    commands=[]
    for args in (['git','apply','--check',str(P/'section77.patch')],['git','apply',str(P/'section77.patch')]):
        run=subprocess.run(args,cwd=apply_dir,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        commands.append({'args':args,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
        assert run.returncode==0,commands[-1]
else:
    commands=read('independent-patch-application077.json')['commands']
    assert len(commands)==2 and all(c['returncode']==0 for c in commands)
assert (apply_dir/'rouge/operator_engine.py').read_bytes()==new
assert (apply_dir/'tests/test_aglna_talent_qualification.py').read_bytes()==(P/'test_aglna_talent_qualification.py').read_bytes()
(P/'independent-patch-application077.json').write_text(json.dumps({'commands':commands,'two_files_exactly_rebuilt':True},indent=2)+'\n')

source=read('source-receipt077.json')
assert source['baseline_commit']==COMMIT
original=read('selected-original-objects077.json')
tables={}
for name,meta in source['sources'].items():
    raw=Path(meta['path']).read_bytes()
    assert len(raw)==meta['bytes'] and sha(raw)==meta['sha256'],name
    tables[name]=json.loads(raw)
owner=tables['character_table']['char_1015_aglna2']
assert original['character_table_complete_selected_character']==owner
candidates=owner['talents'][0]['candidates']
assert len(candidates)==4
assert [(c['unlockCondition'],c['requiredPotentialRank']) for c in candidates]==[
 ({'phase':'PHASE_1','level':1},0),({'phase':'PHASE_1','level':1},2),
 ({'phase':'PHASE_2','level':1},0),({'phase':'PHASE_2','level':1},2)]
assert all(c['name']==TALENT and c['prefabKey']=='1' for c in candidates)
profile=read('baseline/rouge/data/catalog.json')['operators']['char_1015_aglna2']
for c,n in zip(candidates,profile['talents'][0],strict=True):
    assert n=={'phase':int(c['unlockCondition']['phase'][-1]),'level':c['unlockCondition']['level'],
              'potential_rank':c['requiredPotentialRank'],'name':c['name'],'description':c['description'],
              'values':{b['key']:b['value'] for b in c['blackboard']}}
for number,(character_skill,normal) in enumerate(zip(owner['skills'],profile['skills'],strict=True),1):
    saved=original['skills_complete'][str(number)]
    skill=tables['skill_table'][character_skill['skillId']]
    assert saved['character_skill_complete']==character_skill and saved['skill_table_complete']==skill
    assert normal['id']==character_skill['skillId']
    assert normal['unlock_elite']==int(character_skill['unlockCond']['phase'][-1])
    assert len(normal['levels'])==len(skill['levels'])==10
    for raw,n in zip(skill['levels'],normal['levels'],strict=True):
        assert n['name']==raw['name'] and n['duration']==raw['duration'] and n['description']==raw['description']
        assert n['duration_type']==raw['durationType'] and n['sp_type']==raw['spData']['spType']
        assert n['sp_cost']==raw['spData']['spCost'] and n['initial_sp']==raw['spData']['initSp']
        assert n['sp_increment']==raw['spData']['increment'] and n['max_charges']==raw['spData']['maxChargeTime']
        assert n['values']=={b['key']:b['value'] for b in raw['blackboard']}
assert owner['skills'][0]['unlockCond']=={'phase':'PHASE_0','level':1}
assert tables['skill_table']['skchr_aglna2_1']['levels'][0]['skillType']=='PASSIVE'
assert tables['skill_table']['skchr_aglna2_1']['levels'][0]['spData']['spType']==8

def compare(left,right,result_key):
    counts=collections.Counter();report_differences=0
    assert len(left)==len(right)
    for a,b in zip(left,right,strict=True):
        assert a['request']==b['request']
        if 'group' in a:assert a['group']==b['group']
        if 'label' in a:assert a['label']==b['label']
        if 'error' in a or 'error' in b:
            assert a.get('error')==b.get('error')
            counts['prior_complete_errors_unchanged']+=1;continue
        old=a[result_key];new=b[result_key]
        if 'full_result_sha256' in a:
            assert a['full_result_sha256']==digest(old) and b['full_result_sha256']==digest(new)
        request=a['request'];locked=request['operator']=='char_1015_aglna2' and request.get('elite',2)==0
        if locked:
            c=[c for c in new['components'] if c['name']==TALENT]
            assert len(c)==1
            assert c[0]['hits']==c[0]['per_hit']==c[0]['total']==0 and c[0]['times_seconds']==[]
            assert new['estimate']['skill']['hit_counts'][TALENT]==0
            restored=copy.deepcopy(new)
            was=next(c for c in old['components'] if c['name']==TALENT)
            now=next(c for c in restored['components'] if c['name']==TALENT)
            now['hits']=was['hits'];now['times_seconds']=copy.deepcopy(was['times_seconds'])
            restored['estimate']['skill']['hit_counts'][TALENT]=old['estimate']['skill']['hit_counts'][TALENT]
            assert canonical(restored)==canonical(old)
        else:assert canonical(old)==canonical(new)
        kind='only_locked_talent_hits_times_skill_count_zeroed' if old!=new else 'complete_json_unchanged'
        counts[kind]+=1
        if 'human_report' in a:
            if a['human_report']!=b['human_report']:
                assert locked;report_differences+=1
        if request['operator']=='char_1015_aglna2' and request.get('elite',2)>0 and request.get('base_attack')==0:
            c=next(c for c in new['components'] if c['name']==TALENT)
            assert c['per_hit']==0 and c['hits']>0 and c['times_seconds']
    return {'paired_scenarios':len(left),'counts':dict(counts),'human_report_differences':report_differences}

saved_before=read('baseline-results077.json');saved_after=read('draft-results077.json')
assert saved_before['paired_scenario_records']==saved_after['paired_scenario_records']==875
saved=compare(saved_before['records'],saved_after['records'],'full_result')
assert saved['counts']=={'only_locked_talent_hits_times_skill_count_zeroed':146,
                        'complete_json_unchanged':570,'prior_complete_errors_unchanged':159}
author=read('matrix-comparison077.json')
assert author['mismatches']==[] and author['paired_scenarios']==875
assert author['matrix_actual_new_public_calls']==1612
assert author['reused_readonly_public_calls_without_rerun']==138
assert author['total_actual_author_public_calls_including_reused_source_audit']==1750
own_before=read('independent-baseline-results077.json');own_after=read('independent-draft-results077.json')
assert own_before['public_calls']==own_after['public_calls']==66
own=compare(own_before['records'],own_after['records'],'result')
assert own['counts']=={'only_locked_talent_hits_times_skill_count_zeroed':25,
                      'complete_json_unchanged':29,'prior_complete_errors_unchanged':12}
tests=read('independent-new-tests077.json')
assert tests['new_tests_run']==tests['new_tests_passed']==9
assert tests['failures']==tests['errors']==tests['skipped']==0
assert tests['source_before_sha256']==tests['source_after_sha256']==ENGINE_SHA
related=read('related-tests077.json')
assert related['run']==related['passed']==38 and related['failures']==related['errors']==related['skipped']==0

receipt={
 'status':'independent_review_passed','blockers':[],'baseline_commit':COMMIT,
 'patch_sha256':PATCH_SHA,'changed_source_hashes':{'rouge/operator_engine.py':ENGINE_SHA},
 'new_test_sha256':TEST_SHA,'exact_CRLF_single_production_line_verified':True,
 'baseline_public_files_git_blob_verified':2408,'other_draft_public_files_unchanged':2407,
 'patch_actual_check_apply_rebuilt_code_and_new_test':True,
 'fresh_paired_scenarios':66,'public_calls':132,'fresh_outcome_counts':own,
 'new_tests_passed':9,'new_tests_skipped':0,
 'saved_author_pairs_strictly_recompared':875,'saved_author_counts':saved,
 'author_total_actual_calls_including138_reused_completed_source_audit':1750,
 'saved_author_API_matrix_rerun_by_reviewer':False,
 'related_author_tests_read':{'passed':38,'skipped':0},
 'source_verified':{'source_commit':source['source_commit'],'fresh_raw_character_sha256':source['sources']['character_table']['sha256'],
   'fresh_raw_skill_sha256':source['sources']['skill_table']['sha256'],
   'complete_original_selected_character_and_all3_skills_match_saved_objects':True,
   'exact_first_talent_candidates':4,'first_unlock':'E1 level1, enhanced coefficient at potential3',
   'all30_skill_level_projections_checked':True,'E0_S1_deployment_passive_spType8_preserved':True},
 'bounded_conclusion':'When the actually selected first talent is absent, its zero component has no hits/timestamps or skill hit counts. Qualified E1/E2 and zero-damage selected talents retain the old events. Numerical totals, independent natural SP on applicable timed skills, complete/status/report schema, AttackTimeline streams, weight validation, old error order and existing unknown S2/S3/native clock boundaries are unchanged.',
 'initial_author_test_contract_error':'Author first expected natural1.2 for deployment-passive E0S1; history is retained and final test correctly uses None plus independent E1S2 natural1.2. No production code was changed to fit that test.',
 'initial_independent_extractor_assumption':'Initial expected fresh classification counted all28 successful E0 cases as changed. Three empty-target controls were already exactly zero in baseline; observed strict counts are25 changed/29 full same/12 errors. Full JSON assertions passed before the mistaken summary-count assertion. No API rerun or product change.',
 'gui_executed':False,'wine_executed':False,'tracked_edits':False,'private_state_read':False,
 'artifact_hashes':{name:sha((P/name).read_bytes()) for name in (
   'source-receipt077.json','selected-original-objects077.json','baseline-freeze077.json',
   'baseline-results077.json','draft-results077.json','independent-baseline-results077.json',
   'independent-draft-results077.json','independent-new-tests077.json','independent-new-tests077.log',
   'independent-patch-application077.json','independent-initial-count-extractor077.json')}
}
(P/'independent-review077.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'fresh_paired_scenarios':66,'public_calls':132,
 'new_tests_passed':9,'saved_author_pairs_strictly_recompared':875,'counts':saved['counts'],
 'receipt_sha256':sha((P/'independent-review077.json').read_bytes())},ensure_ascii=False))

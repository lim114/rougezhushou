from copy import deepcopy
import collections
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT=Path(__file__).parent
AUTHOR=Path('/workspace/.continuation/p2-mei-airborne-module-reference-073')
BASE=Path('/workspace/.continuation/p2-after-070-source-audit/baseline070')
DRAFT=AUTHOR/'draft'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


source=json.loads((OUT/'source-review073.json').read_text())
freeze=json.loads((AUTHOR/'draft-freeze.json').read_text())
assert sha(AUTHOR/'section073.patch')==freeze['patch_sha256']=='e214100047ef879f9bd51bea4da3c8914acf467abe8852ddd1fc1eb982a4743d'
assert set(freeze['draft_files'])=={'rouge/mei_module_reference.py','rouge/operator_engine.py','rouge/reporting.py','tests/test_mei_airborne_module_reference.py'}
for name,row in freeze['draft_files'].items():
    assert sha(DRAFT/name)==row['sha256'] and len((DRAFT/name).read_bytes())==row['bytes']
original=json.loads(Path('/workspace/.continuation/p2-after-070-source-audit/freeze070-receipt.json').read_text())
assert original['commit']==freeze['baseline_commit']==source['baseline_commit']
entries=subprocess.check_output(['git','-C','/workspace/rougezhushou','ls-tree','-r','-z',original['commit']]).split(b'\0')
blobs={}
for row in entries:
    if row:
        meta,name=row.split(b'\t',1);blobs[name.decode()]=meta.split()[2].decode()
assert len(original['files'])==706
for name,row in original['files'].items():
    data=(BASE/name).read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256'] and len(data)==row['bytes']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blobs[name]
    if name not in ('rouge/operator_engine.py','rouge/reporting.py'):
        assert (DRAFT/name).read_bytes()==data
check=OUT/'patch-check'
for name in ('rouge/operator_engine.py','rouge/reporting.py'):
    target=check/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/name,target)
assert not (check/'rouge/mei_module_reference.py').exists()
for args in (['git','apply','--check',str(AUTHOR/'section073.patch')],['git','apply',str(AUTHOR/'section073.patch')]):
    done=subprocess.run(args,cwd=check,capture_output=True,text=True)
    assert done.returncode==0,done.stderr
assert all((check/name).read_bytes()==(DRAFT/name).read_bytes()for name in freeze['draft_files'])
catalog=json.loads((BASE/'rouge/data/catalog.json').read_text())
owner=catalog['operators']['char_133_mm'];module=owner['modules'][0]


def expected(args):
    elite=args.get('elite',2);level=args.get('level')or owner['phases'][elite]['max_level']
    stage=args.get('module_level',0)
    active=(args.get('operator')=='char_133_mm'and args.get('module_id')=='uniequip_002_mm'
            and type(stage)is int and 1<=stage<=3 and elite>=2 and level>=40)
    if not active:return None
    candidate=module['levels'][stage-1]['parts'][0]['overrideTraitDataBundle']['candidates'][0]
    return {'operator_id':'char_133_mm','module_id':'uniequip_002_mm','module_name':module['name'],
        'module_level':stage,'unlock_elite':2,'unlock_level':40,
        'candidate_unlock_condition':candidate['unlockCondition'],'required_potential_rank':0,
        'trait_description':candidate['additionalDescription'],'attack_scale_parameter':1.1,
        'actual_target_is_airborne':None,'actual_conditional_damage':None,
        'reference_only':True,'applied_to_numeric_estimate':False,'native_attachment_verified':False,
        'damage_composition_verified':False,'live_state_verified':False,
        'source_commit':source['game_commit'],'source_selectors':[
            'character_table.char_133_mm','uniequip_table.equipDict.uniequip_002_mm',
            'battle_equip_table.uniequip_002_mm.phases['+str(stage-1)+'].parts[0].overrideTraitDataBundle.candidates[0]']}


def compare(before,after):
    assert len(before)==len(after)
    counts=collections.Counter()
    for old,new in zip(before,after):
        assert old['scenario']==new['scenario']
        if 'label'in old:assert old['label']==new['label']
        if 'error'in old['outcome']:
            assert old==new;counts['old_errors_unchanged']+=1;continue
        assert 'result'in new['outcome']
        result=new['outcome']['result'];reference=expected(new['scenario'])
        blocks=[s for s in result['report']['sections']if s['id']=='mei_airborne_module']
        if reference is None:
            assert 'mei_airborne_module_reference'not in result and blocks==[]
            assert old==new;counts['whole_success_unchanged']+=1
        else:
            assert result['mei_airborne_module_reference']==reference and len(blocks)==1
            metrics={m['key']:m['value']for m in blocks[0]['metrics']}
            assert metrics['target_airborne']is None and metrics['conditional_damage']is None
            assert abs(metrics['attack_scale']-110)<1e-10
            notes='\n'.join(blocks[0]['notes'])
            assert '110%参数未计入当前伤害数值'in notes and '组合层尚未核验'in notes
            assert result['complete_definition']in notes
            trimmed=deepcopy(result);trimmed.pop('mei_airborne_module_reference')
            trimmed['report']['sections']=[s for s in trimmed['report']['sections']if s['id']!='mei_airborne_module']
            assert trimmed==old['outcome']['result']
            counts['qualified_reference_only_changes']+=1
    return dict(counts)


with gzip.open(AUTHOR/'public-baseline.json.gz','rt',encoding='utf-8')as f:before=json.load(f)
with gzip.open(AUTHOR/'public-draft.json.gz','rt',encoding='utf-8')as f:after=json.load(f)
assert len(before)==1830
saved=compare(before,after)
assert saved=={'qualified_reference_only_changes':1524,'whole_success_unchanged':246,'old_errors_unchanged':60}
old=json.loads((OUT/'baseline-results073.json').read_text());new=json.loads((OUT/'draft-results073.json').read_text())
assert old['calls']==new['calls']==80 and old['caller_and_catalog_unchanged']and new['caller_and_catalog_unchanged']
fresh=compare(old['records'],new['records'])
assert fresh=={'qualified_reference_only_changes':50,'whole_success_unchanged':20,'old_errors_unchanged':10}
for name,row in freeze['draft_files'].items():assert sha(DRAFT/name)==row['sha256']
report={
    'status':'independent_review_passed','blockers':[],
    'baseline_commit':source['baseline_commit'],'game_commit':source['game_commit'],
    'raw_source_sha256':source['raw_source_sha256'],
    'patch_sha256':freeze['patch_sha256'],'draft_source_hashes':freeze['draft_files'],
    'baseline_files_rechecked_against_actual_committed_git_blobs':706,'unchanged_draft_old_files':704,
    'patch_apply_check_and_exact_four_file_reconstruction':True,
    'fresh_paired_scenarios':80,'fresh_public_calls':160,'fresh_counts':fresh,
    'saved_author_paired_scenarios_strictly_recompared':1830,'author_calls_not_rerun':3660,'saved_counts':saved,
    'new_tests_independently_passed':8,'author_new_and_related_tests_passed':48,
    'source_exact_owner_module_levels_and_qualifications':True,'source_native_cache_rehashed_exact_search_count':199,
    'bounded_scope':'Qualified Mei MAR-X source parameter reference plus one report section. No checkbox, target classification, formula, complete/scope change or native attachment inferred. Removing only these two additions restores every old output field and prior error.',
    'no_tracked_edits':True,'no_private_state_reads':True,'no_wine_or_gui':True,
    'artifact_sha256':{str(path):sha(path)for path in (OUT/'source_review073.py',OUT/'source-review073.json',OUT/'probe073.py',OUT/'baseline-results073.json',OUT/'draft-results073.json',OUT/'new-tests073.log',OUT/'verify073.py',AUTHOR/'source-receipt.json',AUTHOR/'public-baseline.json.gz',AUTHOR/'public-draft.json.gz',AUTHOR/'matrix-comparison.json',AUTHOR/'section073.patch')},
}
path=OUT/'independent-review073.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'fresh_pairs':80,'fresh_calls':160,'fresh_counts':fresh,'saved_pairs':1830,'saved_counts':saved,'new_tests':8,'receipt_sha256':sha(path)}))

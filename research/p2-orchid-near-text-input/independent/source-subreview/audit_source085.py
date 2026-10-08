"""Independent original-source/late-guard/transport audit; no calculate or tests."""
from pathlib import Path
import copy
import hashlib
import io
import json
import subprocess
import sys
import tarfile

OUT=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-orchid-near-text-085')
SOURCE=AUTHOR/'source-only'
REPO=Path('/workspace/rougezhushou')
BASE='b5a40f30683bfc0945decaabbd4db5914c28427f'
OP='char_1048_orchd2'
MOD='uniequip_002_orchd2'
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def copy_exact(path,name):
    data=path.read_bytes();target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    assert path.read_bytes()==data
    return {'source_path':str(path),'archive_path':name,'bytes':len(data),'sha256':sha(data)}
freeze_path=AUTHOR/'author-freeze085.json'
assert sha(freeze_path.read_bytes())=='96fa448ec78f4021122520a96e6e580289a3e4f113ed3835af2f803204169026'
freeze=json.loads(freeze_path.read_bytes())
assert freeze['fixed_commit']==BASE
assert sha((AUTHOR/'section85.patch').read_bytes())==freeze['patch_sha256']=='a61cf733014a5d2f2b32e39eb75f61ea517785f27804ed3f94d3101c7b5b9736'
assert sha((AUTHOR/'draft/rouge/damage.py').read_bytes())==freeze['draft_damage_sha256']=='29ecf0a145c620e1a96af76019288e7e24dbc02c1ca6695a475931a65a1e285e'
assert sha((AUTHOR/'draft/tests/test_orchid_near_text_input.py').read_bytes())==freeze['new_test_sha256']=='8fd8cdaf383ab54945404ad33c5f610c2fc2e4bb018800b1a8bed3193a0dce86'
bindings=[copy_exact(freeze_path,'fixed-author/author-freeze085.json'),
          copy_exact(AUTHOR/'section85.patch','fixed-author/section85.patch'),
          copy_exact(AUTHOR/'draft/rouge/damage.py','fixed-author/rouge/damage.py'),
          copy_exact(AUTHOR/'draft/tests/test_orchid_near_text_input.py','fixed-author/tests/test_orchid_near_text_input.py')]
manifest_path=SOURCE/'public-artifacts-manifest.json'
assert sha(manifest_path.read_bytes())==freeze['source_manifest_sha256']=='a5047e145b400668b7f27f17ba9087a17b56945d79f567856b0088b619364962'
manifest=json.loads(manifest_path.read_bytes())
assert manifest['format_version']==1 and len(manifest['files'])==22
for record in manifest['files']:
    original=Path(record['source_path']).read_bytes();copied=(SOURCE/record['archive_path']).read_bytes()
    assert len(original)==record['bytes'] and sha(original)==record['sha256'] and copied==original
bindings.append(copy_exact(manifest_path,'source-bindings/public-artifacts-manifest.json'))
receipt=json.loads((SOURCE/'source-receipt085.json').read_bytes())
assert receipt['product_commit']==BASE and receipt['game_commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
bindings.append(copy_exact(SOURCE/'source-receipt085.json','source-bindings/source-receipt085.json'))
raw={}
for record in receipt['fresh_original_files']:
    data=Path(record['path']).read_bytes()
    assert len(data)==record['bytes'] and sha(data)==record['sha256']
    raw[record['table']]=json.loads(data)
assert len(raw)==4
character=json.loads((SOURCE/'original-character-orchid.json').read_bytes())
skills=json.loads((SOURCE/'original-skills-orchid.json').read_bytes())
module=json.loads((SOURCE/'original-module-orchid.json').read_bytes())
assert character==raw['character_table'][OP]
assert skills=={entry['skillId']:raw['skill_table'][entry['skillId']] for entry in character['skills']}
assert module['equip_record']==raw['uniequip_table']['equipDict'][MOD]
assert module['battle_record']==raw['battle_equip_table'][MOD]
for name in ['original-character-orchid.json','original-skills-orchid.json','original-module-orchid.json']:
    bindings.append(copy_exact(SOURCE/name,'fixed-original-selected/'+name))
assert module['equip_record']['charId']==OP and module['equip_record']['tmplId']is None
assert module['equip_record']['unlockEvolvePhase']=='PHASE_2' and module['equip_record']['unlockLevel']==60
named=character['talents'][1]['candidates']
assert len(named)==2 and all(t['name']=='翔虫机动' and t['prefabKey']=='1' for t in named)
for phase,candidate,value in zip(['PHASE_1','PHASE_2'],named,[.10,.15],strict=True):
    assert candidate['unlockCondition']=={'phase':phase,'level':1} and candidate['requiredPotentialRank']==0
    bb={row['key']:row['value'] for row in candidate['blackboard']}
    assert bb['atk']==value and bb['atk_duration']==30
module_candidates=[]
for index,phase in enumerate(module['battle_record']['phases']):
    assert len(phase['parts'])==[1,3,3][index]
    for part_index,part in enumerate(phase['parts']):
        assert part.get('isToken')is False
        candidates=(part.get('addOrOverrideTalentDataBundle')or{}).get('candidates')or[]
        for candidate in candidates:
            if candidate['name']=='翔虫机动':
                assert index in [1,2] and candidate['talentIndex']==1 and candidate['prefabKey']=='1'
                assert part['target']=='TALENT_DATA_ONLY' and candidate['unlockCondition']=={'phase':'PHASE_2','level':60}
                values={row['key']:row['value'] for row in candidate['blackboard']}
                assert values['atk']==.20 and values['atk_duration']==30
            else:
                assert candidate['name']is None and candidate['talentIndex']==3 and candidate['prefabKey']=='3'
                assert candidate['isHideTalent']is True
                assert {row['key']:row['value'] for row in candidate['blackboard']}=={'respawn_time':[-17,-18][index-1]}
            module_candidates.append({'stage':index+1,'part':part_index,'target':part['target'],'candidate':candidate})
assert len(module_candidates)==4

paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'rouge','tests','scripts'],cwd=REPO,text=True).splitlines()
paths=[p for p in paths if p.endswith(('.py','.json'))]
assert len(paths)==720
archive=subprocess.check_output(['git','archive','--format=tar',BASE,*paths],cwd=REPO)
hashes={};public=[]
with tarfile.open(fileobj=io.BytesIO(archive))as f:
    for member in f:
        if not member.isfile():continue
        data=f.extractfile(member).read();assert member.name in paths
        assert (AUTHOR/'baseline'/member.name).read_bytes()==data
        hashes[member.name]={'bytes':len(data),'sha256':sha(data)}
        if member.name!='rouge/damage.py':assert (AUTHOR/'draft'/member.name).read_bytes()==data
        if member.name.startswith('rouge/'):
            target=OUT/'fixed-helper-package'/member.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            public.append(member.name)
assert len(public)==125
profile=json.loads((AUTHOR/'baseline/rouge/data/catalog.json').read_bytes())['operators'][OP]
normal_mod=next(m for m in profile['modules']if m['id']==MOD)
assert normal_mod['unlock_elite']==2 and normal_mod['unlock_level']==60
for original,normalized in zip(module['battle_record']['phases'],normal_mod['levels'],strict=True):assert original['parts']==normalized['parts']
for skill_index,entry in enumerate(character['skills']):
    original=skills[entry['skillId']]['levels'];normalized=profile['skills'][skill_index]['levels']
    assert len(original)==len(normalized)==10
    for raw_level,normal_level in zip(original,normalized,strict=True):
        for field in ['name','description','duration']:assert raw_level[field]==normal_level[field]
        assert {b['key']:b['value']for b in raw_level['blackboard']}==normal_level['values']
before=(AUTHOR/'baseline/rouge/damage.py').read_bytes();after=(AUTHOR/'draft/rouge/damage.py').read_bytes()
insert=("    if (scenario['operator']=='char_1048_orchd2' and\r\n"
        "            isinstance(scenario.get('near_previous_deployment'),str)):\r\n"
        "        from .operator_engine import selected_talents\r\n"
        "        talents,_=selected_talents(catalog()['operators'][scenario['operator']],scenario)\r\n"
        "        if any(t.get('name')=='翔虫机动' for t in talents):\r\n"
        "            raise ValueError('near_previous_deployment 不接受文本条件；请使用布尔值。')\r\n").encode()
assert after.count(insert)==1 and after.replace(insert,b'',1)==before
assert b"    result['report']=build_report(scenario,result)\r\n"+insert+b'    return result\r\n'in after
assert b'\n'not in after.replace(b'\r\n',b'')
engine=(AUTHOR/'baseline/rouge/operator_engine.py').read_bytes()
assert engine==(AUTHOR/'draft/rouge/operator_engine.py').read_bytes()
assert b"if self.s.get('near_previous_deployment'):self.atk_bonus+=self.talent('"in engine
assert "if '翔虫机动' in self.tv:"in engine.decode()
app=(AUTHOR/'baseline/rouge/app.py').read_text()
assert 'if isinstance(default,bool):'in app and 'widget=QCheckBox(label)'in app
assert 'widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()'in app
assert 'if owner==op and self.skill.currentData() in skills:'in app
for rel in ['rouge/app.py','rouge/operator_engine.py','rouge/operator_options.py','rouge/catalog.py','rouge/gnosis_module_reference.py']:
    bindings.append(copy_exact(AUTHOR/'baseline'/rel,'fixed-consumers/'+rel))
patch=AUTHOR/'section85.patch'
numstat=subprocess.run(['git','apply','--numstat',str(patch)],cwd=OUT,text=True,capture_output=True)
save('patch-numstat085.json',{'returncode':numstat.returncode,'stdout':numstat.stdout,'stderr':numstat.stderr,'API_calls':0,'mutations':False})
assert numstat.returncode==0 and numstat.stdout=='6\t0\trouge/damage.py\n137\t0\ttests/test_orchid_near_text_input.py\n'
target=OUT/'readonly-apply-target';(target/'rouge').mkdir(parents=True);(target/'tests').mkdir()
(target/'rouge/damage.py').write_bytes(before)
check=subprocess.run(['git','apply','--check',str(patch)],cwd=target,text=True,capture_output=True)
save('readonly-apply-check085.json',{'returncode':check.returncode,'stdout':check.stdout,'stderr':check.stderr,
    'API_calls':0,'target':'external exact baseline damage only, new test absent','actual_apply_executed':False,'tracked_mutations':False})
assert check.returncode==0
assert (target/'rouge/damage.py').read_bytes()==before and not(target/'tests/test_orchid_near_text_input.py').exists()

sys.dont_write_bytecode=True
sys.path.insert(0,str(OUT/'fixed-helper-package'))
from rouge.operator_engine import selected_talents
qualification=[(0,1,1,0,None),(0,1,6,3,None),(1,1,1,0,.10),(1,1,6,3,.10),
               (2,1,1,0,.15),(2,59,6,3,.15),(2,60,1,1,.15),(2,60,1,2,.20),(2,60,6,3,.20)]
helper_rows=[]
for elite,level,potential,stage,expected_bonus in qualification:
    scenario={'operator':OP,'elite':elite,'level':level,'potential':potential,'module_level':stage}
    if stage:scenario['module_id']=MOD
    original_args=copy.deepcopy(scenario)
    selected,parts=selected_talents(profile,scenario)
    selected_named=[t for t in selected if t.get('name')=='翔虫机动']
    if expected_bonus is None:assert not selected_named
    else:
        assert len(selected_named)==1 and selected_named[0]['values']['atk']==expected_bonus
        assert selected_named[0]['values']['atk_duration']==30
    assert scenario==original_args
    helper_rows.append({'scenario':scenario,'selected_talents':selected,'module_parts':parts,'expected_near_bonus':expected_bonus})
save('selected-helper-qualification085.json',{'actual_selected_talents_calls':9,'calculate_damage_calls':0,
    'helper_source_sha256':sha(engine),'rows':helper_rows,'input_preserved':True})
for rel in public:assert sha((OUT/'fixed-helper-package'/rel).read_bytes())==hashes[rel]['sha256']
save('source-guard-review085.json',{'status':'passed_no_blocker','fixed_commit':BASE,'author_freeze_sha256':sha(freeze_path.read_bytes()),
    'author_damage_sha256':sha(after),'patch_sha256':sha(patch.read_bytes()),'source_only22_manifest_sha256':sha(manifest_path.read_bytes()),
    'source_only22_original_and_authorcopy_all_bytes_verified':True,'raw4_full_files_verified':receipt['fresh_original_files'],
    'complete_selected_original_objects_and_all_module_parts_exact':True,'original_skill_ranks_checked':30,
    'base_named_candidates':named,'four_exact_module_talent_candidates':module_candidates,
    'baseline_720_exact_git_blobs_checked':True,'draft_719_existing_files_unchanged':True,'baseline_public_hashes':hashes,
    'six_line_inverse_restores_full_damage_bytes':True,'late_after_existing_build_report':True,'CRLF_preserved':True,
    'qualification':'actual selected_talents named 翔虫机动; E0 inactive, E1L1 .10, E2L1 .15, X1 .15 and X2/X3 E2L60 .20; locked module retains base qualification',
    'helper_actual_calls':9,'calculate_damage_calls':0,'new_tests_run':0,'GUI':False,'Wine':False,'tracked_mutations':False,
    'transport':'Valid standard unified source6/0 + new test137/0; independent read-only frozen apply-check passed with no actual apply',
    'scope':'Orchid near str plus actual selected named talent only; all legally selected skills and normal initialization; no global validator or string decoding',
    'double_charge':'Unchanged consumer/default/clock. No new guard; S1-only reference and resource consumers remain original.',
    'old_error_priority':'Existing preparation, cultivation, engine, timing, relic, finisher and per-evaluation build_report occur before new guard; numerical formal verifier owns saved pair checks',
    'historical2':'Only source receipt observation; not counted or reused as current baseline by this audit',
    'integration':'Root must insert six lines surgically preserving83/84 late guards; never replace full author damage from old b5 baseline',
    'unknowns_retained':receipt['unknowns'],'no_new_native_attachment_phase_or_probabilities':True,
    'bindings':bindings,
    'preparation_diagnostics':[{'error':'Initial read guessed draft.patch; actual section85.patch located via rg --files','calculate_damage_calls':0,'product_failure':False}]})
print(json.dumps({'status':'passed','raw_original_files':4,'source_manifest_files':22,'raw_skill_ranks':30,
    'actual_helper_calls':9,'calculate_damage_calls':0,'tests_run':0,
    'review_sha256':sha((OUT/'source-guard-review085.json').read_bytes())}))

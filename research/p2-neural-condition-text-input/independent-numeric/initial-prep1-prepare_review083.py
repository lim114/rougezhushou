"""Freeze the narrow fixed-author package and design independent <=40 pairs."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import tarfile

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-neural-condition-text-input-083')
REPO = Path('/workspace/rougezhushou')
BASE = 'b5a40f30683bfc0945decaabbd4db5914c28427f'
OLD = Path('/workspace/.continuation/p2-boolean-consumer-083-independent-source')
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
fixed = json.loads((AUTHOR/'formal-draft-freeze083.json').read_bytes())
assert fixed['baseline_commit'] == BASE
assert fixed['files']['rouge/damage.py']['sha256'] == 'f5a462aa2571a71c288a3f56bc75d1541760d74b187c5fb38ee06715b19c421a'
for rel, record in fixed['files'].items():
    path = AUTHOR/('draft/'+rel if rel.startswith(('rouge/','tests/')) else rel)
    data = path.read_bytes()
    assert len(data)==record['bytes'] and sha(data)==record['sha256']
    target = OUT/'fixed-author-inputs'/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
(OUT/'fixed-author-inputs/formal-draft-freeze083.json').write_bytes((AUTHOR/'formal-draft-freeze083.json').read_bytes())
baseline_paths = subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'rouge','tests','scripts'],cwd=REPO,text=True).splitlines()
baseline_paths = [p for p in baseline_paths if p.endswith(('.py','.json'))]
archive = subprocess.check_output(['git','archive','--format=tar',BASE,*baseline_paths],cwd=REPO)
hashes = {'baseline':{},'draft':{}}
with tarfile.open(fileobj=io.BytesIO(archive)) as f:
    for member in f:
        if not member.isfile():continue
        assert member.name in baseline_paths
        content = f.extractfile(member).read()
        assert (AUTHOR/'baseline'/member.name).read_bytes()==content
        hashes['baseline'][member.name]={'bytes':len(content),'sha256':sha(content)}
for rel in baseline_paths+['tests/test_neural_condition_text_input.py']:
    data = (AUTHOR/'draft'/rel).read_bytes()
    hashes['draft'][rel]={'bytes':len(data),'sha256':sha(data)}
    if rel in hashes['baseline'] and rel!='rouge/damage.py':
        assert hashes['draft'][rel]==hashes['baseline'][rel]
assert len(hashes['baseline'])==720 and len(hashes['draft'])==721
before = (AUTHOR/'baseline/rouge/damage.py').read_bytes()
after = (AUTHOR/'draft/rouge/damage.py').read_bytes()
insert = ("    # Validate the processed neural scenario after preserving legacy errors.\r\n"
          "    if scenario['operator'] in ('char_1042_phatm2','char_4204_mantra'):\r\n"
          "        for field in ('enemy_is_boss','enemy_in_neural_break'):\r\n"
          "            if isinstance(scenario.get(field),str):\r\n"
          "                raise ValueError(field+' 不接受文本条件；请使用布尔值。')\r\n").encode()
assert after.count(insert)==1 and after.replace(insert,b'',1)==before
assert b"    result['report']=build_report(scenario,result)\r\n"+insert+b"    return result\r\n" in after
assert b'\n' not in after.replace(b'\r\n',b'')
public = [p for p in baseline_paths if p.startswith('rouge/')]
assert len(public)==125
for variant in ('baseline','draft'):
    for rel in public+(['tests/__init__.py','tests/test_neural_condition_text_input.py'] if variant=='draft' else []):
        data = (AUTHOR/variant/rel).read_bytes()
        target = OUT/('fixed-'+variant)/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
source = json.loads((AUTHOR/'source-receipt083.json').read_bytes())
for record in source['raw_sources'].values():
    data=Path(record['path']).read_bytes()
    assert len(data)==record['bytes'] and sha(data)==record['sha256']
old_manifest = OLD/'public-artifacts-manifest.json'
assert sha(old_manifest.read_bytes())=='c16724af88468ca36477d1290fe04eac8b1baac9f8f9fde28be92c081d3b71b9'
for row in json.loads(old_manifest.read_bytes())['files']:
    data=Path(row['source_path']).read_bytes()
    assert len(data)==row['bytes'] and sha(data)==row['sha256']
save('formal-freeze-review083.json',{'status':'passed','baseline_commit':BASE,'all_baseline_git_blobs':hashes['baseline'],
    'all_draft_blobs':hashes['draft'],'production_package_copies':125,'old_sealed46_reverified':True,
    'old8_calls_repeated':False,'parent_source_two_owner_all_skill_scope_reused':True,
    'exact_inverse_patch_restores_full_damage_bytes':True,'damage_CRLF_preserved':True,
    'engine_threshold_clock_helpers_unchanged_from_baseline':True,'only_product_change':'five post-build_report str guard lines',
    'new_source_tests_hash':fixed['files']['tests/test_neural_condition_text_input.py']['sha256'],
    'author_metadata':{'path':str(AUTHOR/'formal-draft-freeze083.json'),'sha256':sha((AUTHOR/'formal-draft-freeze083.json').read_bytes())},
    'source_author_receipt_sha256':sha((AUTHOR/'source-receipt083.json').read_bytes()),
    'raw_sources_reverified':source['raw_sources'],'fresh_API_calls':0,'tracked_mutations':False})

cases=[]
def add(name,owner='char_4204_mantra',skill=3,expect='same',field=None,**extra):
    scenario={'operator':owner,'skill':skill,'skill_rank':7,'elite':2,'level':1,'potential':6,
              'base_attack':997,'timing_mode':'frames','window_seconds':3.3,**extra}
    cases.append({'case':name,'scenario':scenario,'expectation':expect,'field':field})
add('phatm-e0-s1-boss-text','char_1042_phatm2',1,'reject','enemy_is_boss',elite=0,enemy_is_boss='false')
add('phatm-e1-s2-break-empty','char_1042_phatm2',2,'reject','enemy_in_neural_break',elite=1,enemy_in_neural_break='',timing_mode='continuous')
add('phatm-e2-s3-both-text','char_1042_phatm2',3,'reject','enemy_is_boss',enemy_is_boss='unknown',enemy_in_neural_break='false')
add('mantra-e0-s1-break-text',skill=1,expect='reject',field='enemy_in_neural_break',elite=0,enemy_in_neural_break='false')
add('mantra-e1-s2-boss-text',skill=2,expect='reject',field='enemy_is_boss',elite=1,enemy_is_boss='0',timing_mode='continuous')
add('mantra-e2-s3-break-text-river',expect='reject',field='enemy_in_neural_break',enemy_in_neural_break='false',relic_ids=['rogue_6_relic_fight_22'])
add('mantra-s3-boss-text-initial1500',expect='reject',field='enemy_is_boss',enemy_is_boss='false',initial_neural_buildup=1500)
add('mantra-s3-boss-false-initial1500',expect='old_error',enemy_is_boss=False,initial_neural_buildup=1500)
add('mantra-s3-boss-true-initial1500',enemy_is_boss=True,initial_neural_buildup=1500)
add('mantra-s3-river-break-false',enemy_in_neural_break=False,relic_ids=['rogue_6_relic_fight_22'])
add('mantra-s3-river-break-true',enemy_in_neural_break=True,relic_ids=['rogue_6_relic_fight_22'])
targets=[{'stage_id':'ro6_e_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
         {'stage_id':'ro6_b_3','enemy_id':'enemy_2143_shwksc','level':0}]
for owner in ['char_1042_phatm2','char_4204_mantra']:
    for index,target in enumerate(targets):
        add(f'{owner}-selected-enemy{index}-overrides-boss-text',owner,3,
            enemy_is_boss='false',target_enemy=target,run_config={'difficulty':{'value':10}})
add('selected-boss-overrides-boss-only-break-still-active',expect='reject',field='enemy_in_neural_break',
    enemy_is_boss='false',enemy_in_neural_break='false',target_enemy=targets[1])
add('mantra-nontext-null-empty-list',enemy_is_boss=None,enemy_in_neural_break=[],relic_ids=['rogue_6_relic_fight_22'])
add('phatm-nontext-float01','char_1042_phatm2',2,enemy_is_boss=0.0,enemy_in_neural_break=1.0,relic_ids=['rogue_6_relic_fight_22'])
add('mantra-nontext-legacy-containers',skill=1,enemy_is_boss=[False],enemy_in_neural_break={'assumed':False})
add('phatm-nontext-legacy-other-numbers','char_1042_phatm2',1,enemy_is_boss=-1,enemy_in_neural_break=2)
errors=[('invalid-rank',{'skill_rank':False}),('unavailable-skill',{'elite':0,'skill':2}),
        ('initial-overrange',{'initial_neural_buildup':2501}),('buildup-resistance',{'enemy_buildup_resistance':101}),
        ('element-resistance',{'enemy_elemental_resistance':101}),('negative-window',{'window_seconds':-1}),
        ('negative-windup',{'timing':{'windup_frames':-2}}),('negative-SP-lockout',{'timing':{'sp_lockout_extra_seconds':-2}})]
for name,extra in errors:
    add('prior-'+name,expect='old_error',enemy_is_boss='false',enemy_in_neural_break='false',**extra)
add('prior-phatm-bool-incoming-count','char_1042_phatm2',3,'old_error',enemy_is_boss='false',enemy_in_neural_break='false',enemy_attack_count=True)
add('prior-mantra-bool-palsy-count',expect='old_error',enemy_is_boss='false',enemy_in_neural_break='false',palsy_triggers=True)
add('prior-invalid-module',expect='old_error',enemy_is_boss='false',enemy_in_neural_break='false',module_id='unknown',module_level=1)
add('mantra-S2-nontext-integer01',skill=2,enemy_is_boss=0,enemy_in_neural_break=1)
add('prior-invalid-run-difficulty',expect='old_error',enemy_is_boss='false',enemy_in_neural_break='false',run_config={'difficulty':{'value':16}})
add('prior-known-false-threshold-before-break-text',expect='old_error',enemy_is_boss=False,enemy_in_neural_break='false',initial_neural_buildup=1500)
for owner,skill in [('char_1037_amiya3',2),('char_1048_orchd2',3),('mechanist',1)]:
    add('otherowner-'+owner,owner,skill,enemy_is_boss='false',enemy_in_neural_break='unknown')
add('mantra-zero-window-text',expect='reject',field='enemy_in_neural_break',enemy_in_neural_break='false',window_seconds=0)
add('phatm-zero-life-boss-text','char_1042_phatm2',2,'reject','enemy_is_boss',enemy_is_boss='false',timing={'target_disappears_seconds':0})
add('mantra-empty-enemy-windows-both-text',expect='reject',field='enemy_is_boss',enemy_is_boss='false',enemy_in_neural_break='false',timing={'target_windows':[]})
assert len(cases)==40
assert len({row['case'] for row in cases})==40
old_requests=[row['scenario'] for row in json.loads((OLD/'public-counterexamples083.json').read_bytes())['rows']]
assert all(row['scenario'] not in old_requests for row in cases)
save('independent-cases083.json',cases)
print(json.dumps({'status':'passed','independent_pairs_planned':40,'fixed_baseline_files':720,
    'fixed_draft_files':721,'fresh_API_calls':0,'source_reconstruction':'exact five-line inverse passed'}))

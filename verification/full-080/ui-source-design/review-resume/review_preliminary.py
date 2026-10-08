"""Independent static review only: no application API, Qt, or Wine calls."""
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

P = Path('/workspace/.continuation/ui-080-draft')
R = P / 'review-resume'
ROOT = Path('/workspace/rougezhushou')
R.mkdir(exist_ok=True)
names = ('public_contracts.py', 'cases080.py', 'supplemental-checks.py.fragment',
         'wine-ui-smoke-080.py', 'build_runner.py', 'runner-static-review.json')
raw = {name: (P / name).read_bytes() for name in names}
assert raw == {name: (P / name).read_bytes() for name in names}, 'concurrent draft mutation'
for name, data in raw.items():
    (R / ('preliminary-' + name.replace('/', '-'))).write_bytes(data)

sha = lambda data: hashlib.sha256(data).hexdigest()
base = Path('/workspace/.compat/wine-ui-smoke-075.py').read_bytes()
assert sha(base) == '645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
runner = raw['wine-ui-smoke-080.py'].decode()
ast.parse(runner)
helpers = raw['public_contracts.py'].decode() + '\n' + raw['cases080.py'].decode()
fragment = raw['supplemental-checks.py.fragment'].decode()
assert runner.count(helpers + '\n\n') == 1, 'runner helpers do not match current design'
assert runner.count(fragment + '\n') == 1, 'runner fragment does not match current design'
restored = runner.replace(fragment + '\n', '', 1).replace(helpers + '\n\n', '', 1)
for name in ('wine-ui-report-difference-075.json', 'wine-window-075.png',
             'wine-ui-075.json', 'wine-ui-failure-075.png',
             'wine-sown-tile-control-075.png', 'wine-movement-reference-075.png'):
    restored = restored.replace(name.replace('-075', '-080'), name)
restored = restored.replace('-(next_end-next_start)', '')
restored = restored.replace("        receipt['preserved_full_075_checks']=len(checks)\n"
    "        assert receipt['preserved_full_075_checks']==1455,receipt['preserved_full_075_checks']\n", '')
assert restored.encode() == base, 'old 1455 complete runner body changed'

case_ns = {}
exec(compile(raw['cases080.py'], '<pure cases only>', 'exec'), case_ns)
cases = [case for case in case_ns['cases080']() if case['section'] in (76, 77, 78)]
counts = Counter(case['section'] for case in cases)
assert counts == {76: 432, 77: 424, 78: 360}, counts
anchors = set()
for case in cases:
    args = case['input']
    section = case['section']
    key = {k:v for k,v in args.items() if k != {76:'bubble_bursts',77:'enemy_weight',78:'palsy_triggers'}[section]}
    key = (section, json.dumps(key, sort_keys=True, ensure_ascii=False))
    field = {76:'bubble_bursts',77:'enemy_weight',78:'palsy_triggers'}[section]
    if args[field] == 0:
        anchors.add(key)
    else:
        assert key in anchors, ('missing earlier zero control', case)

opt_tree = ast.parse((ROOT/'rouge/operator_options.py').read_bytes())
opt = next(ast.literal_eval(n.value) for n in opt_tree.body
    if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets))
options = {(owner,row[0]):row for owner,rows in opt.items() for row in rows}
expected = [('char_4202_haruka','bubble_bursts',int,10000,(1,2,3)),
            ('char_4202_haruka','haruka_repeat',bool,1,(2,)),
            ('char_4202_haruka','levitate_triggers',int,1000,(3,)),
            ('char_1015_aglna2','enemy_weight',int,100,(1,2,3)),
            ('char_4204_mantra','palsy_triggers',int,10000,(1,2,3)),
            ('char_4204_mantra','palsy_overflow_hits',int,10000,(3,)),
            ('char_4204_mantra','enemy_elemental_resistance',float,100,(1,2,3))]
for owner, field, typ, maximum, skills in expected:
    row = options[owner,field]
    assert type(row[2]) is typ and row[3] == maximum and row[4] == skills
for case in cases:
    args = case['input']
    for owner, field, typ, maximum, skills in expected:
        if owner == args['operator'] and field in args:
            assert type(args[field]) is typ and 0 <= args[field] <= maximum and args['skill'] in skills

catalog = json.loads((ROOT/'rouge/data/catalog.json').read_bytes())['operators']
for case in cases:
    args = case['input']; profile = catalog[args['operator']]
    assert 1 <= args['level'] <= profile['phases'][args['elite']]['max_level']
    assert profile['skills'][args['skill']-1]['unlock_elite'] <= args['elite']
for owner, talent, minimum in [('char_4202_haruka','扶摇花火',2),
    ('char_1015_aglna2','飘浮大地之上',1),('char_4204_mantra','噤声限域',1)]:
    selected = [row for group in catalog[owner]['talents'] for row in group if row['name']==talent]
    assert min(row['phase'] for row in selected) == minimum
    assert all(row['level'] == 1 for row in selected)

source77 = json.loads((P/'selected-enemy-source077.json').read_bytes())
battle_raw = (ROOT/'rouge/data/battle-previews.json').read_bytes()
assert sha(battle_raw) == source77['source_sha256']
battle = json.loads(battle_raw)
for row in source77['records']:
    target = row['target_enemy']
    candidates = battle['stages'][target['stage_id']]['enemies']
    exact = [e for e in candidates if e['id']==target['enemy_id'] and e['level']==target['level']]
    assert len(exact)==1 and exact[0]==row['full_public_reference_record']

saved_raw = (P/'public-schema-interim-077.json.gz').read_bytes()
assert sha(saved_raw)=='1f98cffd06a9f6f4e469adb690656f79195e8f866b4b525bc9ae61e36b971ecf'
saved = json.loads(gzip.decompress(saved_raw))
assert saved['calls']==len(saved['records'])==840 and saved['sections']=={'76':432,'77':408}
assert saved['source_drift']==[] and saved['gui_executed'] is False and saved['wine_executed'] is False
receipt = {'status':'preliminary_static_review_passed_final080_pending',
    'scope':'Only 76-78 design and existing 77 API receipt metadata; no new API calls, Qt or Wine',
    'base075_sha256':sha(base), 'runner_sha256':sha(raw['wine-ui-smoke-080.py']),
    'files':{name:sha(data) for name,data in raw.items()},
    'old1455_complete_body_reconstructed_exactly':True, 'runner_syntax_valid':True,
    'design_counts':dict(counts),'earlier_same_context_zero_controls_verified':True,
    'real_options_default_type_range_and_applicable_skills_verified':True,
    'readonly_training_and_existing_skill_unlock_source_verified':True,
    'selected_enemy_exact_roster_records_verified':True,
    'saved_api_receipt_metadata_records':840,'saved_api_receipt_scope':{'76':432,'77':408},
    'pending_design_without_API_proof':{'77_selected_enemy':16,'78':360},
    'root_source_hashes':{name:sha((ROOT/name).read_bytes()) for name in
        ('rouge/app.py','rouge/operator_options.py','rouge/data/catalog.json','rouge/data/battle-previews.json')},
    'blockers':[], 'gui_executed':False,'wine_executed':False,'new_public_api_calls':0,
    'ready_for_actual_execution':False}
(R/'preliminary-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('files','root_source_hashes')},ensure_ascii=False))

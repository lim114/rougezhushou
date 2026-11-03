"""Independent bounded branch/source review of284 caller capture, not native QA."""
from copy import deepcopy
from pathlib import Path
import ast
import hashlib
import importlib
import importlib.machinery
import json
import sys
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'rouge/app.py').is_file())
EXPECTED = {
    'rouge/operator_engine.py':'c724dce00372cb4ca99716ad03a88c547c878087ea3265e89396944b15681a4c',
    'rouge/panel_native_bridge.py':'998e1be1c61139d781a39340f88e513359d4315f5b97a74d4bdd9ae698ff8483'}
OUT = HERE/'independent-capture-review-284.json'
assert not OUT.exists()
for name, expected in EXPECTED.items():
    data = (ROOT/name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    (HERE/('reviewed-'+Path(name).name)).write_bytes(data)
old_sources = {
    'operator_engine.py':(ROOT/'.cache/section283-main-tests/corrected-real-main-10/source/rouge/operator_engine.py',
                          'ab607af94c536ca214dee880145bc72a7e85acc494a07756c254cc66918ec4bf'),
    'panel_native_bridge.py':(ROOT/'.cache/section283-source-review/bridge-reviewed-52800ba9.py',
                              '52800ba9d98a58790ec4a77eabd4eb195516f31ad1716a0fc49ee86909e671a6')}
old_dir = HERE/'old-public-two-files'
assert not old_dir.exists();old_dir.mkdir()
for name,(path,expected) in old_sources.items():
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
    (old_dir/name).write_bytes(raw)

checks, probes = [], []
def check(name, ok):
    checks.append({'name':name,'passed':bool(ok)})

def assignment_sites(raw):
    tree=ast.parse(raw)
    plan=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='plan')
    sites=[]
    def walk(node, conditions):
        if isinstance(node,ast.If):
            test=ast.unparse(node.test)
            for child in node.body:walk(child,conditions+[test])
            for child in node.orelse:walk(child,conditions)
            return
        targets=[]
        if isinstance(node,ast.Assign):targets=node.targets
        elif isinstance(node,ast.AugAssign):targets=[node.target]
        if any(isinstance(t,ast.Name) and t.id in ('attack','speed_reference') for t in targets):
            sites.append({'line':node.lineno,'text':ast.unparse(node),
                          'positive_if_ancestors':conditions,'ast':ast.dump(node,include_attributes=False)})
        for child in ast.iter_child_nodes(node):walk(child,conditions)
    walk(plan,[])
    return sites

old_sites=assignment_sites((old_dir/'operator_engine.py').read_bytes())
new_sites=assignment_sites((ROOT/'rouge/operator_engine.py').read_bytes())
check('source/all18_actor_assignments_unchanged',[s['ast'] for s in old_sites]==[s['ast'] for s in new_sites] and len(new_sites)==18)
check('source/capture_at_plan_inputs', "self.s,self.n,self.a,self.base,self.atk_bonus,self.atk_flat,self.as_bonus,bb)" in (ROOT/'rouge/operator_engine.py').read_text(encoding='utf8'))
check('source/full_plan_not_display_window_is_used', "'skill':full['native_skill_terms']" in (ROOT/'rouge/operator_engine.py').read_text(encoding='utf8'))
check('source/no_numeric_inverse_or_second_catalog_selection', not any(t in (ROOT/'rouge/panel_native_bridge.py').read_text(encoding='utf8').split('def capture_extended_skill_primitives',1)[1].split('def unknown_skill_terms',1)[0] for t in ('catalog(', 'model_value', 'skill_attack', '/base_attack')))

sys.path.insert(0,str(ROOT))
import rouge.damage as current
def load_old():
    name='independent_old283_for284'
    package=types.ModuleType(name);package.__package__=name
    package.__path__=[str(old_dir),str(ROOT/'rouge')]
    package.__spec__=importlib.machinery.ModuleSpec(name,loader=None,is_package=True)
    sys.modules[name]=package
    return importlib.import_module(name+'.damage')
old=load_old()

def selected(result):
    keys=('attack','total_damage','total_healing','attack_speed','attack_speed_reference',
          'base_attack_speed','base_attack_speed_reference','components','complete','warnings')
    return {key:deepcopy(result.get(key)) for key in keys}|{'estimate':{
        key:deepcopy(result['estimate'].get(key)) for key in ('base_stats','skill','training','complete','warnings')}}

# Off-default paired controls, not a repeat of the author's78 default matrix.
cases=[
 ('myrtle_mixed700',{'operator':'char_151_myrtle','skill':2,'effects':[{'kind':'attack_pct','value':.25},{'kind':'attack_speed','value':600}]},True,True),
 ('shu_sown_true',{'operator':'char_2025_shu','skill':3,'enemy_on_sown_tile':True,'three_same_profession':True},False,False),
 ('shu_sown_false',{'operator':'char_2025_shu','skill':3,'enemy_on_sown_tile':False,'three_same_profession':True},True,True),
 ('xiangzi_organ',{'operator':'char_4182_oblvns','skill':2,'organ_mode':True,'fever':True},True,False),
 ('xiangzi_piano',{'operator':'char_4182_oblvns','skill':2,'organ_mode':False,'fever':True},False,True),
 ('angel_steal_failed',{'operator':'char_1041_angel2','skill':2,'steal_success':False},True,True),
 ('angel_steal_success',{'operator':'char_1041_angel2','skill':2,'steal_success':True},True,False),
 ('deepcolor_two_tokens',{'operator':'char_110_deepcl','skill':1,'summon_count':2},False,True),
 ('wisdel_ghost_not_body',{'operator':'char_1035_wisdel','skill':3,'ghost_count':1,'ghost_casts':1},True,True),
 ('chen_post_slash',{'operator':'char_1050_chen3','skill':2,'slash_kills':5},False,True),
 ('medical_amiya_post_opening',{'operator':'char_1037_amiya3','skill':2,'amiya_hit_targets':5},False,True),
 ('yato_external_dash',{'operator':'char_1029_yato2','skill':3,'dash_hits':2},False,True)]
for name, payload, attack, speed in cases:
    pristine=deepcopy(payload)
    before=old.calculate_damage(deepcopy(payload))
    result=current.calculate_damage(payload)
    native=result['panel_native_finalization']
    rows={row['field']:row for row in native['fields'] if row['phase']=='skill'}
    qualifications=native['skill_primitive_qualification']
    probes.append({'name':name,'input':pristine,'old_legacy_selected':selected(before),
                   'new_legacy_selected':selected(result),'native_output':deepcopy(native)})
    check(name+'/caller_unchanged',payload==pristine)
    check(name+'/legacy_exact_same',selected(before)==selected(result))
    check(name+'/source_valid',native['source_valid'] is True)
    for field, expected in [('attack',attack),('attack_speed',speed)]:
        q=qualifications[field];r=rows[field]
        check(name+'/'+field+'/field_qualification',q['common_model_primitives_captured'] is expected)
        check(name+'/'+field+'/reason_and_primitive', (q['reason'] is None and r['references']['input_fp_raw'] is not None) if expected else (bool(q['reason']) and r['references']['input_fp_raw'] is None and r['conditional_complete'] is False))
        check(name+'/'+field+'/actual_unknown',q['actual_activation_or_phase_clock_verified'] is False and r['actual_getter_raw'] is None and r['actual_decoded_value'] is None and r['complete_native_value'] is False)
        check(name+'/'+field+'/same_scope_on_row',r['primitive_qualification']==q)
    check(name+'/full_native_not_claimed',native['complete_native_panel'] is False and native['actual_panel'] is None)
    check(name+'/internal_metadata_consumed',not {'_panel_native_terms','_panel_native_skill_qualification'}&set(result['estimate']))

myrtle=probes[0]['native_output']
mr={row['field']:row for row in myrtle['fields'] if row['phase']=='skill'}
check('myrtle/as_attribute700_literal',mr['attack_speed']['references']['getter_result_raw']==700*4294967296)
check('myrtle/effective_timing600_separate',probes[0]['new_legacy_selected']['estimate']['skill']['skill_attack_speed']==600)
check('field_scope/not_copied_between_opposite_music_modes',probes[3]['native_output']['skill_primitive_qualification']!=probes[4]['native_output']['skill_primitive_qualification'])

source_files=EXPECTED|{'rouge/panel_native_finalization.py':hashlib.sha256((ROOT/'rouge/panel_native_finalization.py').read_bytes()).hexdigest(),
                       'rouge/data/catalog.json':hashlib.sha256((ROOT/'rouge/data/catalog.json').read_bytes()).hexdigest()}
check('review/frozen_two_files_unchanged',all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected for name,expected in EXPECTED.items()))
report={'kind':'SECTION284_INDEPENDENT_LIMITED_CALLER_SOURCE_AND_BRANCH_REVIEW',
        'source_sha256':source_files,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'actor_assignment_sites':new_sites,'assignment_scope':'All18 direct ATK/AS writes in plan:2 initial sites and16 later rewrites; associated positive conditions are source descriptors, not a full path solver.',
        'branch_source_conclusion':'All later field rewrites have matching conservative per-field exclusions. Token attacks, per-hit scales, damage/heal target factors and independent projectile/phase timing are not promoted into body panel primitives.',
        'checks':checks,'check_count':len(checks),'probes':probes,'probe_count':len(probes),
        'failed':[c for c in checks if not c['passed']],
        'scope':'Frozen caller code plus12 selected old/new paired public controls; no repeat of author78-default matrix or283 arithmetic/native proof. Known means existing-model nominal primitive capture only.',
        'new_native_fresh_spans':0,'game_or_chat_operation':False,'private_state_read_or_changed':False,
        'production_or_other_author_cache_modified':False}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'probes':len(probes),'checks':len(checks),'failed':report['failed'],
                  'receipt_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}))
raise SystemExit(bool(report['failed']))

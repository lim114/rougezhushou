"""Prepare explicit cache-only full380 preflight adaptation; never installs/runs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json
R=Path(__file__).resolve().parents[1];B=R/'.cache/full380-prepared';D=R/'.cache/full380-canonical-cache-binding-repair'
D.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(p):raw=p.read_bytes();return{'bytes':len(raw),'sha256':sha256(raw).hexdigest()}
def one(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
review_path=R/'.cache/full380-preflight-canonical-cache-source-review.json';review=json.loads(review_path.read_bytes())
rows=[]
for item in review['explicit_source_rows']:
 public=(item['existing_exact_public_counterparts'][0]['path']if item['existing_exact_public_counterparts']else'verification/full-380/explicit-public-build-inputs/'+item['sha256']+'.json')
 row={'mode':'p3_369','canonical_script':'scripts/verify_current_boss_documents_window_369.py','local_path':item['local_path'],'public_path':public,'sha256':item['sha256'],'bytes':item['bytes'],'origin_manifests':item['original_public_authority_refs']}
 rows.append(row)
rows=sorted(rows,key=lambda x:x['local_path']);assert len(rows)==5
for row in rows:
 assert pin(R/row['local_path'])=={'bytes':row['bytes'],'sha256':row['sha256']}
 for original in row['origin_manifests']:
  assert pin(R/original['path'])=={'bytes':original['bytes'],'sha256':original['sha256']}
  assert json.loads((R/original['path']).read_bytes())['build_authority_files'][row['local_path']]=={'bytes':row['bytes'],'sha256':row['sha256']}

HELPERS='''
# Exactly five original public game-data inputs selected only by canonical369.
# Generic public() remains unchanged and continues to reject every cache path.
CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS = __BINDINGS__


def canonical_binding_plan():
    return json.loads(json.dumps(CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS))


def canonical_local_path(name, mode):
    rows = {row['local_path']: row for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS}
    if mode != 'p3_369' or name not in rows:
        raise ValueError('Only the exact five canonical369 local public originals are permitted.')
    path = ROOT / name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Exact regular canonical369 local original required: ' + name)
    for parent in path.parents:
        if parent == ROOT: break
        if parent.is_symlink(): raise ValueError('Linked canonical369 local parent refused.')
    return path


def canonical_selected_source(name, mode=None):
    if name.startswith('.cache/'):
        return canonical_local_path(name, mode)
    return public(name)


def canonical_inputs(bindings, selected_paths=None):
    if bindings != CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS:
        raise ValueError('Exact original five canonical369 bindings/order/provenance required.')
    expected_names = {row['local_path'] for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS}
    if selected_paths is not None:
        actual = {(mode, name) for mode, names in selected_paths.items() for name in names if name.startswith('.cache/')}
        if actual != {('p3_369', name) for name in expected_names}:
            raise ValueError('Local originals must remain selected exactly by369, never other workflows.')
    observed = {}
    for row in bindings:
        local = canonical_local_path(row['local_path'], row['mode']); other = public(row['public_path'])
        for origin in row['origin_manifests']:
            authority = public(origin['path'])
            if sha(authority) != origin['sha256'] or authority.stat().st_size != origin['bytes']:
                raise ValueError('Original canonical build authority manifest drift: ' + origin['path'])
            document = json.loads(authority.read_bytes())
            if document['build_authority_files'].get(row['local_path']) != {'sha256': row['sha256'], 'bytes': row['bytes']}:
                raise ValueError('Exact canonical original manifest entry changed.')
            expected_pointer = '/build_authority_files/' + row['local_path'].replace('~','~0').replace('/','~1')
            if origin['json_pointer'] != expected_pointer:
                raise ValueError('Original canonical authority pointer changed.')
        local_raw = local.read_bytes(); public_raw = other.read_bytes()
        if (len(local_raw) != row['bytes'] or len(public_raw) != row['bytes']
                or sha256(local_raw).hexdigest() != row['sha256'] or sha256(public_raw).hexdigest() != row['sha256']
                or local_raw != public_raw):
            raise ValueError('Exact whole canonical local/public input bytes differ: ' + row['local_path'])
        observed[row['local_path']] = row['sha256']
    return observed


def canonical_frozen_inputs(data):
    observed = canonical_inputs(data.get('canonical_local_public_input_bindings'), data['p3_script_selected_paths'])
    if observed != data.get('canonical_local_public_input_sha256'):
        raise ValueError('Frozen exact canonical369 local source map differs.')
    for row in CANONICAL_LOCAL_PUBLIC_INPUT_BINDINGS:
        if data['supplemental_public_inputs_sha256'].get(row['public_path']) != row['sha256']:
            raise ValueError('Exact canonical public counterpart absent from supplemental range.')
    return observed

'''.replace('__BINDINGS__',repr(rows))

modified={}
name='tools/full380_common.py';s=(B/name).read_text('utf8')
s=one(s,'def runner_snapshot():',HELPERS+'\ndef runner_snapshot():')
s=one(s,"    actual = runner_snapshot()\n", "    canonical_frozen_inputs(data)\n    actual = runner_snapshot()\n")
modified[name]=s

name='tools/declare_current380.py';s=(B/name).read_text('utf8')
s=one(s,'native_source_snapshot,input_bindings,public,sha,write_new,now,git,tool_pins)', 'native_source_snapshot,input_bindings,public,sha,write_new,now,git,tool_pins,\n    canonical_binding_plan,canonical_inputs,canonical_selected_source)')
s=one(s,'    supplemental=set(old[\'supplemental_public_inputs_sha256\']);selected={};options={}\n', "    canonical_bindings=canonical_binding_plan();canonical_before=canonical_inputs(canonical_bindings)\n    supplemental=set(old['supplemental_public_inputs_sha256']);selected={};options={}\n    supplemental.update(row['public_path']for row in canonical_bindings)\n")
s=one(s,"            if not mapping or any(sha(public(k))!=(v['sha256']if type(v)is dict else v)for k,v in mapping.items()):raise ValueError('Actual public source map differs: '+name)\n", "            if not mapping or any(sha(canonical_selected_source(k,mode))!=(v['sha256']if type(v)is dict else v)for k,v in mapping.items()):raise ValueError('Actual public/canonical explicit source map differs: '+name)\n")
s=one(s,"        supplemental.update(selected[mode]);supplemental.add(name)\n", "        supplemental.update(k for k in selected[mode]if not k.startswith('.cache/'));supplemental.add(name)\n")
s=one(s,"    options['p3_311']['visible_ms']=300000\n", "    if canonical_inputs(canonical_bindings,selected)!=canonical_before:raise ValueError('Canonical369 local/public inputs drifted during discovery.')\n    options['p3_311']['visible_ms']=300000\n")
s=one(s,"        'local_public_input_bindings':bindings,'local_public_input_sha256':locals_before,\n", "        'local_public_input_bindings':bindings,'local_public_input_sha256':locals_before,\n        'canonical_local_public_input_bindings':canonical_bindings,'canonical_local_public_input_sha256':canonical_before,\n")
s=one(s,"    if git('rev-parse','HEAD')!=parent or git('branch','--show-current')!='codex/p2-development':raise ValueError('Parent changed during declaration.')\n", "    if canonical_inputs(canonical_bindings,selected)!=canonical_before:raise ValueError('Exact canonical local/public originals drifted during declaration.')\n    if git('rev-parse','HEAD')!=parent or git('branch','--show-current')!='codex/p2-development':raise ValueError('Parent changed during declaration.')\n")
modified[name]=s

name='tools/review_results380.py';s=(B/name).read_text('utf8')
s=one(s,'from full380_common import BASE, ROOT, bound, public, sha, write_new', 'from full380_common import BASE, ROOT, bound, public, sha, write_new, canonical_selected_source, canonical_frozen_inputs')
s=one(s,'def source_stable(raw, expected, original287=False):', 'def source_stable(raw, expected, original287=False, canonical_mode=None):')
s=one(s,"    require(all(sha(public(name)) == expected_sha for name, expected_sha in after.items()), 'Selected source bytes now differ.')", "    require(all(sha(canonical_selected_source(name, canonical_mode)) == expected_sha for name, expected_sha in after.items()), 'Selected source bytes now differ.')")
s=one(s,"    bound(parent, freeze_sha, sha(BASE / 'activation380.json'))\n", "    bound(parent, freeze_sha, sha(BASE / 'activation380.json'))\n    canonical_sources = canonical_frozen_inputs(data)\n")
s=one(s,"                expected = {name: ({**data['source_sha256'], **data['supplemental_public_inputs_sha256']})[name]\n", "                expected = {name: ({**data['source_sha256'], **data['supplemental_public_inputs_sha256'], **canonical_sources})[name]\n")
s=one(s,"                source_stable(raw, expected, original287=mode == 'p3_287')", "                source_stable(raw, expected, original287=mode == 'p3_287', canonical_mode=mode)")
modified[name]=s

name='seal_summary380.py';s=(B/name).read_text('utf8')
s=one(s,"    expected_sources = {**data['source_sha256'], **data['supplemental_public_inputs_sha256']}\n", "    from full380_common import canonical_frozen_inputs\n    expected_sources = {**data['source_sha256'], **data['supplemental_public_inputs_sha256'], **canonical_frozen_inputs(data)}\n")
s=one(s,"                source_stable(raw, expected, original287=mode == 'p3_287')", "                source_stable(raw, expected, original287=mode == 'p3_287', canonical_mode=mode)")
anchor="    for section in range(366,381):\n"
new="""    from full380_common import canonical_binding_plan, canonical_frozen_inputs
    require(data.get('canonical_local_public_input_bindings') == canonical_binding_plan(),
            'Exactly the five original canonical369 local/public/provenance bindings must be retained separately.')
    canonical = canonical_frozen_inputs(data)
    require(len(canonical) == 5, 'Original canonical369 five local sources are not complete.')
"""
s=one(s,anchor,new+anchor)
s=one(s,"            'prior_results_reused_as_current_PASS':False}\n", "            'canonical369_explicit_original_local_public_bindings':data['canonical_local_public_input_bindings'],\n            'canonical369_exact5_sources_preserved_only_in_mode369':True,\n            'prior_results_reused_as_current_PASS':False}\n")
modified[name]=s

# The ordinary publication guard has no import from a mutable cache module.
# Inline the same exact fixed bindings and original provenance before publication.
guard='''
    _expected_canonical = __BINDINGS__
    assert d.get('canonical_local_public_input_bindings') == _expected_canonical
    _canonical_names = {row['local_path'] for row in _expected_canonical}
    assert {(mode,name) for mode,names in d['p3_script_selected_paths'].items() for name in names if name.startswith('.cache/')} == {('p3_369',name) for name in _canonical_names}
    assert d.get('canonical_local_public_input_sha256') == {row['local_path']:row['sha256'] for row in _expected_canonical}
    for row in _expected_canonical:
        assert row['mode']=='p3_369' and row['canonical_script']=='scripts/verify_current_boss_documents_window_369.py'
        for origin in row['origin_manifests']:
            authority=ROOT/origin['path']
            assert authority.is_file()and not authority.is_symlink()and authority.resolve().is_relative_to(ROOT.resolve())
            assert _sha(origin['path'])==origin['sha256']and authority.stat().st_size==origin['bytes']
            assert _read(origin['path'])['build_authority_files'][row['local_path']]=={'sha256':row['sha256'],'bytes':row['bytes']}
            assert origin['json_pointer']=='/build_authority_files/'+row['local_path'].replace('~','~0').replace('/','~1')
        _raws=[]
        for name in(row['local_path'],row['public_path']):
            path=ROOT/name
            assert path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT.resolve())
            for parent in path.parents:
                if parent==ROOT:break
                assert not parent.is_symlink()
            raw=path.read_bytes();assert len(raw)==row['bytes']and _sha256(raw).hexdigest()==row['sha256']
            _raws.append(raw)
        assert _raws[0]==_raws[1]
        assert d['supplemental_public_inputs_sha256'][row['public_path']]==row['sha256']
'''.replace('__BINDINGS__',repr(rows))
adapter=R/'.cache/patch380_final_closeout.py';s=adapter.read_text('utf8')
s=one(s,"    manifest='verification/full-380/execution-attempt'+str(d['actual_validation_attempt'])+'/archive-manifest.json'\n",guard+"    manifest='verification/full-380/execution-attempt'+str(d['actual_validation_attempt'])+'/archive-manifest.json'\n")
modified['../patch380_final_closeout.py']=s

note='''

### 声明前canonical369固定公开原件适配（不增加完整执行attempt）

原声明预检在冻结/activation/full执行之前拒绝canonical369的五条旧公开游戏原件cache键。原终端观察如无完整trace只能忠实保留观察记录，不能重建trace。新增独立canonical_local_public_input_bindings只允许369原manifest明确固定的五条，保留旧local_public_input_bindings原序相等和原selected键。两份已有公共整字节副本复用；另三份由root核原件后保存到verification/full-380/explicit-public-build-inputs/<真实SHA>.json。标准public()仍拒绝所有cache/private；newresolver拒绝其它mode、未知cache路径、来源manifest变更、SHA/bytes不符、软链接或整字节差异。声明、每组件前后、实际review、严格sealer和普通发布守卫均重新核此完整独立绑定。不改变原fixture、旧scope、原30/29、native/Qt、重试和执行策略。
'''
modified['HANDOFF.md']=(B/'HANDOFF.md').read_text('utf8')+note
files={}
for name,text in modified.items():
 if name.endswith('.py'):ast.parse(text)
 target=D/('patch380_final_closeout.py'if name.startswith('../')else name);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf8',newline='\n')
 files[name]={'before':pin(adapter if name.startswith('../')else B/name),'after':pin(target),'candidate':target.relative_to(R).as_posix()}

# Scope-preservation static assertions. No helper or product code executed.
old_common=ast.parse((B/'tools/full380_common.py').read_bytes());new_common=ast.parse((D/'tools/full380_common.py').read_bytes())
for fn in('public','input_bindings','native_source_snapshot','bound','tool_pins'):
 a=next(n for n in old_common.body if isinstance(n,ast.FunctionDef)and n.name==fn);b=next(n for n in new_common.body if isinstance(n,ast.FunctionDef)and n.name==fn)
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),fn
old_seal=(B/'seal_summary380.py').read_text('utf8');new_seal=(D/'seal_summary380.py').read_text('utf8')
assert "data['local_public_input_bindings'] == old['local_public_input_bindings']"in new_seal
for fn in('verify_current30','verify_functional','verify_typed','verify_visual','verify_archive','verify_root_and_ledger','component_argv'):
 a=next(n for n in ast.parse(old_seal).body if isinstance(n,ast.FunctionDef)and n.name==fn);b=next(n for n in ast.parse(new_seal).body if isinstance(n,ast.FunctionDef)and n.name==fn)
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),fn
for name in('tools/activate_full380.py','tools/component_child380.py','tools/run_full380_controller.py','tools/archive_full380.py','tools/execution380.py','tools/run_owned_full380.py','tools/supervisor380.py'):
 assert name not in modified
assert "union = {**data['source_sha256'], **data['supplemental_public_inputs_sha256']}"in new_seal
plan={'kind':'CACHE_ONLY_CANONICAL369_PREFREEZE_REPAIR_PLAN_NOT_APPLIED_NOT_FULL_EXECUTION',
 'at_utc':datetime.now(timezone.utc).isoformat(),'section':380,'existing_unexecuted_capsule':'attempt-1',
 'expected_prepared_READY':pin(B/'PREPARED_READY380.json'),'expected_capsule_READY':pin(B/'attempt-1/CONTROLLER_READY380.json'),'expected_capsule_descriptor':pin(B/'attempt-1/capsule380.json'),
 'source_review':{'path':review_path.relative_to(R).as_posix(),**pin(review_path)},
 'bindings':rows,'new_public_files':[row for row in rows if row['public_path'].startswith('verification/full-380/explicit-public-build-inputs/')],
 'reuse_existing_exact_public_files':[row for row in rows if not row['public_path'].startswith('verification/')],
 'cache_file_replacements':files,
 'mode_bound_only':'p3_369','old_bindings_order_and_full_scope_unchanged':True,'all_original_current30_and29_and_typed_AST_unchanged':True,
 'generic_public_AST_unchanged':True,'old_fixture_activation_controller_argv_budgets_Qt_retry_and_job_behavior_unchanged':True,
 'formal_sources_or_public_copies_written_by_preparer':False,'tests_or_Qt_or_full_started':False,
 'raw_complete_terminal_trace_availability_not_inferred':True}
(D/'plan.json').write_bytes(enc(plan))
print(json.dumps({'plan':(D/'plan.json').relative_to(R).as_posix(),'plan_sha256':pin(D/'plan.json')['sha256'],'candidate_cache_files':list(files),'fixed_bindings':len(rows),'public_copies_root_must_review':len(plan['new_public_files']),'applied':False,'full_execution_started':False},ensure_ascii=False,indent=2))

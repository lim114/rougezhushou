"""Declare complete current350 inputs; no test, Qt construction or suite launch."""
from pathlib import Path
from hashlib import sha256
import ast,json,sys,subprocess
from full350_common import BASE,ROOT,FREEZE,READY_PATH,runner_snapshot,native_source_snapshot,input_bindings,public,sha,write_new,now

old=json.loads((ROOT/'verification/full-335/source-freeze-binding-recheck2.json').read_bytes())
assert not FREEZE.exists()
parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
assert parent=='87b3f79683d0a406ae2d544502323e9239003a70'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
actual=runner_snapshot();assert actual['selectors'][:len(old['selectors'])]==old['selectors'];assert len(actual['selectors'])==569
for name in actual['source_sha256']:
    if name.startswith('tests/test_')and name not in old['source_sha256']:assert'tests.'+Path(name).stem in actual['selectors'],name
native=native_source_snapshot()
assert set(actual['source_sha256'])-set(native)=={'CORE_0.70_VERIFICATION.json'}
assert set(native)-set(actual['source_sha256'])=={'tests/offline_scope_retirement.py'}
scripts=dict(old['p3_scripts'])
for n in range(336,351):
    matches=[p for p in(ROOT/'scripts').glob(f'verify*_window_{n}.py')]
    assert len(matches)==1,(n,matches)
    scripts['p3_'+str(n)]=matches[0].relative_to(ROOT).as_posix()
assert len(scripts)==65

supplemental=set(old['supplemental_public_inputs_sha256']);selected={};options={}
for mode,name in scripts.items():
    source=public(name);raw=source.read_bytes();tree=ast.parse(raw)
    api={'__file__':str(source),'__name__':'_current350_selected_source_api_only'}
    sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
    if any(isinstance(n,ast.FunctionDef)and n.name=='bound_files'for n in tree.body):
        exec(compile(raw,str(source),'exec'),api);mapping=api['bound_files']()
        assert mapping and all(sha(public(k))==(v['sha256']if isinstance(v,dict)else v)for k,v in mapping.items()),name
        selected[mode]=sorted(mapping)
    else:selected[mode]=old['p3_script_selected_paths'][mode]
    supplemental.update(selected[mode]);supplemental.add(name)
    options[mode]={'accepts_visible_ms':b'--visible-ms'in raw,'visible_ms':60000}
options['p3_311']['visible_ms']=300000  # Established full320 same-workflow profile; no claim original120s budget passes.
options['p3_334']['visible_ms']=180000  # Canonical90-entry workflow, all entries retained.

for n in range(336,351):options['p3_'+str(n)]['visible_ms']=120000
options['p3_304']['explicit_current_source_freeze']=True
options['p3_305']['explicit_current_source_freeze']=True

for name in old['supplemental_public_inputs_sha256']:assert public(name).is_file()
bindings=old['local_public_input_bindings'];locals_before=input_bindings(bindings)
extra={name:sha(ROOT/name)for name in old['legacy_external_additional_sha256']}
templates={mode:{name:sha(BASE/('template-'+mode)/name)for name in names}for mode,names in old['template_bundle_sha256'].items()}
assert templates==old['template_bundle_sha256']
refs={}
for label,name in [('necessary','verification/sections/350-necessary-attempt1/process.json'),('native','verification/sections/350-native-attempt1/actual/window.json'),('native_process','verification/sections/350-native-attempt1/process.json')]:
    path=public(name);value=json.loads(path.read_bytes());assert value['passed']is True
    before=value['source_sha256_before'];after=value['source_sha256_after'];assert before==after and all(sha(public(n))==h for n,h in after.items())
    if label=='necessary':assert value['actual_observed_exit']==0 and value['methods_ran']==22
    if label=='native':assert value['unique_checks']>0 and value['qt_exit_code']==0 and value['qpa']=='windows'
    if label=='native_process':assert value['actual_observed_exit']==0
    refs[label]={'path':name,'sha256':sha(path)}
record={'section':350,'actual_validation_attempt':1,'root_declared':True,'declared_at':now(),'parent_commit':parent,
    **actual,'supplemental_public_inputs_sha256':{n:sha(public(n))for n in sorted(supplemental)},
    'legacy_native_source_sha256':native,'legacy_external_additional_sha256':extra,
    'local_public_input_bindings':bindings,'local_public_input_sha256':locals_before,
    'historical_manifest_bindings':old['historical_manifest_bindings'],
    'p3_scripts':scripts,'p3_script_options':options,'p3_script_selected_paths':selected,
    'template_bundle_sha256':templates,'functional_validation':refs,
    'original_typed_auditor_sha256':sha(BASE/'template-legacy/audit_full261_saved_readback.py'),
    'preparation_ready_sha256':sha(READY_PATH),'Linux_WSL_Wine_or_original_private_Windows_verified':False,
    'previous_full_scope_receipt':'verification/full-335/summary.json','previous_results_not_reused_as_current_PASS':True}
assert runner_snapshot()==actual and input_bindings(bindings)==locals_before
write_new(FREEZE,record)
print(json.dumps({'freeze':str(FREEZE),'sha256':sha(FREEZE),'selectors':len(actual['selectors']),'sources':len(actual['source_sha256']),'native_supplements':len(scripts),'supplemental_inputs':len(supplemental),'actual_Qt_or_tests_started':False}))

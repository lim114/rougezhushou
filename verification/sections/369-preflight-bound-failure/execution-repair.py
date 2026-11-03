from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json
R=Path(__file__).resolve().parents[1];p=R/'scripts/verify_current_boss_documents_window_369.py';raw=p.read_bytes();s=raw.decode('utf8')
old='''    for provider in(model,battle,maps,terrain,version,directory,rewards,settlement,settlement.prior,boss_symbols,symbols,phase,cycle,hunt,gold):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])'''
new='''    for provider in(model,battle,maps,terrain,version,directory,rewards,settlement,settlement.prior,boss_symbols,symbols):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    for provider in(phase,cycle,hunt,gold):
        document=json.loads((ROOT/provider.MANIFEST).read_bytes())
        if type(document['runtime_files'])is not dict or type(document['data_file'])is not str:
            raise ValueError('Exact historical runtime manifest schema required: '+provider.MANIFEST)
        names.add(provider.MANIFEST);names.add(document['data_file']);names.update(document['runtime_files'])
        if 'build_authority_files'in document:
            if type(document['build_authority_files'])is not dict:
                raise ValueError('Exact historical build-source map required: '+provider.MANIFEST)
            names.update(document['build_authority_files'])'''
assert s.count(old)==1;s=s.replace(old,new)
a,b=ast.parse(raw),ast.parse(s)
assert [ast.dump(n)for n in a.body if not(isinstance(n,ast.FunctionDef)and n.name=='bound_files')]==[ast.dump(n)for n in b.body if not(isinstance(n,ast.FunctionDef)and n.name=='bound_files')]
out=R/'verification/sections/369-preflight-bound-failure';out.mkdir()
(out/'before-verify_current_boss_documents_window_369.py').write_bytes(raw)
record={'section':369,'kind':'real_wrapper_preflight_failure_not_a_test_failure','observed_at_utc':datetime.now(timezone.utc).isoformat(),'actual_command':['.venv/Scripts/python.exe','-B','-X','utf8','.cache/run369.py','necessary','--attempt','1'],'actual_tool_exit':1,'failure_type':'KeyError','failure_message':'files','location':'scripts/verify_current_boss_documents_window_369.py:20 bound_files','failure_before_retained_child_Popen_created':True,'tests_started':False,'window_started':False,'original_attempt_directory':'verification/sections/369-necessary-attempt1','before_sha256':sha256(raw).hexdigest(),'repair_scope':'Only native harness bound_files: current manifests retain files; four original 309-312 schemas explicitly bind data_file, runtime_files and optional build_authority_files. No product model, parameter, check, timeout or scope removed.'}
p.write_text(s,encoding='utf8',newline='\n');record['after_sha256']=sha256(p.read_bytes()).hexdigest()
(out/'failure-and-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes())
attempt=R/'verification/sections/369-necessary-attempt1';assert attempt.is_dir()and not list(attempt.iterdir())
(attempt/'preflight-failure.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(attempt/'execution-runner.py').write_bytes((R/'.cache/run369.py').read_bytes())
print(json.dumps({'source_guard_schema_repaired_not_yet_tested':True,'original_wrapper_exit1_retained':True,'only_function_changed':'bound_files'}))

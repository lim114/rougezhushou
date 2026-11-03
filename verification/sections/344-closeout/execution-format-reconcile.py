from pathlib import Path
from hashlib import sha256
import ast,json,runpy
root=Path(__file__).resolve().parents[1]
def read(n):return json.loads((root/n).read_bytes())
def save(n,d):(root/n).write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def pin(n):return {'receipt':n,'sha256':sha256((root/n).read_bytes()).hexdigest()}
a=read('verification/sections/344-source-audit.json')
a['previous_native_and_build_bindings']={k:a[k]for k in ['source_build_process','final_native_process']}
a.update(source_build_process='verification/sections/344-source-attempt3/process.json',final_native_process='verification/sections/344-native-attempt3/process.json',format_repair='verification/sections/344-format-repair/repair.json',native_rerun_reasons=['attempt2 after actual terminal fixture-recovery failure','attempt3 after final staged EOL check failure; AST unchanged, rerun for final byte freeze'],launch_observers_timed_out_count=3,final_native_actual_exit=0)
for k in ['source_build_process','local_necessary_process','final_native_process','necessary_source_equivalence']:
    a[k+'_sha256']=sha256((root/a[k]).read_bytes()).hexdigest()
save('verification/sections/344-source-audit.json',a)
n=read('verification/sections/344-necessary-attempt1/process.json')
wname='verification/sections/344-native-attempt3/actual/window.json';pname='verification/sections/344-native-attempt3/process.json'
w=read(wname);p=read(pname);eq=read('verification/sections/344-native-fixture-repair/source-equivalence.json')
assert n['passed']and p['passed']and w['passed']and w['unique_checks']==61
for name,h in n['source_sha256_after'].items():
    actual=sha256((root/name).read_bytes()).hexdigest()
    if name==eq['only_changed_file']:
        assert h==eq['differences'][name]['then']and actual==eq['differences'][name]['now']
    else:assert actual==h,name
for name,h in w['source_sha256_after'].items():assert sha256((root/name).read_bytes()).hexdigest()==h,name
r=read('verification/sections/344.json')
r['source_sha256']=w['source_sha256_after'];r['validated_source_sha256']=w['source_sha256_after']
r['native_windows_validation'].update(**pin(wname),process=pin(pname))
r['necessary_validation']['scope_equivalence']=pin('verification/sections/344-native-fixture-repair/source-equivalence.json')
r['source_audit']=pin('verification/sections/344-source-audit.json');r['root_visual_review']=pin('verification/sections/344-root-visual.json')
r['final_native_fixture_format_repair']=pin('verification/sections/344-format-repair/repair.json')
r['original_project_window_reused_after_fixture_only_formatting']={'product_source_unchanged':True,'actual_window_not_restarted_unnecessarily':True,'scope_equivalence':pin('verification/sections/344-native-fixture-repair/source-equivalence.json')}
save('verification/sections/344.json',r)
tree=ast.parse((root/'.cache/close344.py').read_text('utf8'))
old=next(ast.literal_eval(x.value)for x in tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='validation'for t in x.targets))
new=old.replace('8张最终实际PNG主代理逐张查看。','8张第二轮实际PNG主代理逐张查看；最终第三轮8张完整PNG逐张字节相同，按完整图哈希复用视觉验收。').replace('两个启动观察调用超时，各实际任务分别退出1/0，重跑因已确认失败及修复，不因观察超时。','发布前换行检查随后拦下验收脚本重复回车；保留失败和原字节，归一换行后AST一致，仍按最终字节重跑原生第三轮61项，产品和49项测试不变。三次启动观察均超时，各实际原任务分别退出1/0/0；重跑分别因已确认失败修复和格式变化，不因观察超时。')
for name in ['AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','CLOUD_HANDOFF.md']:
    path=root/name;raw=path.read_bytes();text=raw.decode('utf8')
    old_native=old.replace('\n','\r\n')if b'\r\n'in raw else old
    new_native=new.replace('\n','\r\n')if b'\r\n'in raw else new
    assert text.count(old_native)==1,(name,text.count(old_native))
    path.write_bytes(text.replace(old_native,new_native,1).encode('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json')
cp['latest_section_environment']['native_windows']=new;cp['windows_native_validation']=new
cp['current_section_validation']['native_fixture_format_repaired_and61_rerun']=True
save('DEVELOPMENT_CHECKPOINT.json',cp)
runpy.run_path(str(root/'scripts/update_cloud_index.py'))['update'](root)
s=(root/'.cache/finalize344.py').read_text('utf8').replace('344-index-validation','344-index-validation-attempt2')
(root/'.cache/finalize344_attempt2.py').write_bytes(s.encode('utf8'))
(root/'verification/sections/344-closeout/execution-format-reconcile.py').write_bytes(Path(__file__).read_bytes())
print('Final source, visual, requirements and current validation reconciled')

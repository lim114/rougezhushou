from pathlib import Path
from hashlib import sha256
import json,runpy,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def pin(n):return{'receipt':n,'sha256':sha256((ROOT/n).read_bytes()).hexdigest()}
base='verification/sections/'
n=read(base+'339-necessary-attempt2/process.json');w=read(base+'339-native-attempt2/actual/window.json');p=read(base+'339-native-attempt2/process.json');m=read(base+'339-main-window-final.json');r=read(base+'339.json')
assert n['passed']and n['methods_ran']==45 and w['passed']and w['unique_checks']==47 and w['qt_exit_code']==0 and p['passed']and m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']
for v in(n,w):
 assert v['source_sha256_before']==v['source_sha256_after']
 for name,h in v['source_sha256_after'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
folder=ROOT/(base+'339-format-maintenance')
for name in('339-root-visual.json','339-source-audit.json','339.json'):(folder/('initial-'+name)).write_bytes((ROOT/base/name).read_bytes())
v=read(base+'339-root-visual.json');old={x['name']:x for x in v['final_screenshot_reviews']};reviews=[]
for s in w['screenshots']:
 assert s['sha256']==old[s['name']]['sha256']and sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
 reviews.append({'name':s['name'],'receipt_image':Path(s['path']).relative_to(ROOT).as_posix(),'sha256':s['sha256'],'direct_review_reused_only_because_entire_PNG_bytes_identical':True,'original_direct_review':old[s['name']]['receipt_image']})
v['final_screenshot_reviews']=reviews;v['all9_final_actual_PNGs_byte_identical_to_directly_viewed_first_attempt']=True;(ROOT/base/'339-root-visual.json').write_bytes(enc(v))
a=read(base+'339-source-audit.json');a['first_build_byte_check']=a['build_byte_check'];a['build_byte_check']=pin(base+'339-source-attempt2/process.json');a['format_maintenance']=pin(base+'339-format-maintenance/initial-current_exit.json');a['final_related_tests_rerun']=45;a['final_native_actual_checks_rerun']=47;(ROOT/base/'339-source-audit.json').write_bytes(enc(a))
r['necessary_validation']={**pin(base+'339-necessary-attempt2/process.json'),'methods_run':45,'actual_exit':0};r['native_windows_validation'].update(**pin(base+'339-native-attempt2/actual/window.json'),process=pin(base+'339-native-attempt2/process.json'));r['root_visual_review']=pin(base+'339-root-visual.json');r['source_audit']=pin(base+'339-source-audit.json');r['original_project_window']=pin(base+'339-main-window-final.json');r['source_sha256']=n['source_sha256_after'];r['validated_source_sha256']=w['source_sha256_after'];r['format_maintenance']=pin(base+'339-format-maintenance/initial-current_exit.json');r['initial_runtime_tests_and_native_passed_before_whitespace_gate_failure']=True;r.pop('index_validation',None);(ROOT/base/'339.json').write_bytes(enc(r))
extra='收尾提交检查另发现新模型末尾多余空行，保留原失败与完整原文件压缩原件，仅纠正文档字符串及末尾空行，业务AST未变；最终源码的45项相关检查及47项原生检查已全部实际重跑通过，9张最终PNG与主代理已逐张查看的首轮原图字节完全相同，按字节复用视觉核对。最终测试窗再次正常更新且私人五路径在关闭到启动保持一致。'
old='本机45项相关必要检查首轮全部通过，完整资料构建可重复且字节一致，所选源码前后不变。';new=old+extra
for name in('AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','CLOUD_HANDOFF.md'):
 path=ROOT/name;raw=path.read_bytes();text=raw.decode('utf8');assert text.count(old)==1,name;path.write_bytes(text.replace(old,new,1).encode('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json')
cp['windows_native_validation']=cp['windows_native_validation'].replace(old,new,1);cp['latest_section_environment']['native_windows']=cp['latest_section_environment']['native_windows'].replace(old,new,1);cp['current_section_validation']['format_maintenance_final_checks_rerun']=True;(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
shutil.copyfile(ROOT/'.cache/open_test_window_339_final.py',folder/'execution-main-window-final.py');(folder/'execution-reconcile.py').write_bytes(Path(__file__).read_bytes());runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT);print(json.dumps({'final45_and47_passed':True,'all9_actual_PNGs_byte_identical_to_direct_reviews':True,'final_current_source_guards_checked':True}))

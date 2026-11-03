"""Root closes a genuinely validated section, archives explicit public evidence and publishes."""
import argparse, datetime, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--section',type=int,choices=range(120,126),required=True);p.add_argument('--window-version',type=int,choices=(1,2,3),default=1);p.add_argument('--description',required=True);a=p.parse_args()
n=a.section;B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou')
topics={120:('情景输入保留与严格JSON','manual-scenario-state'),121:('即时技能初动资格','next-attack-ready'),122:('本局保留状态资格','retained-presence'),123:('最后有效攻击节奏','last-accepted-cadence'),124:('阿米娅恢复与眩晕资格','amiya-recovery'),125:('治疗人数预览保留','healing-preview')}
topic,slug=topics[n];gpath=B/f'section{n}-candidate-source-v1.json';g=json.loads(gpath.read_bytes())
def digest(q):return hashlib.sha256(q.read_bytes()).hexdigest()
actual=dict(sorted((q.relative_to(R).as_posix(),digest(q)) for d in ('rouge','tests','scripts') for q in (R/d).rglob('*') if q.is_file() and q.suffix in ('.py','.json') and '__pycache__' not in q.parts))
assert actual==g['source_sha256'] and all(digest(R/q)==s for q,s in g['source_additional_sha256'].items())
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='codex/p2-development'
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==n-1 and cp['next_section']==n
prev=json.loads((B/f'section{n-1}-publication-v1.json').read_bytes());assert head==prev['local_HEAD']==prev['remote_HEAD'] and prev['push_primary_exit']==0 and prev['clean'] is True
window=B/(f'section120-candidate-window-actual-v1' if n==120 else f'section{n}-window-actual-v{a.window_version}');w=json.loads((window/'receipt.json').read_bytes())
saved=B/f'section{n}-saved-actual-v1.json'
if n==122:saved=B/'section122-saved-actual-v1/receipt.json'
visual=B/f'section{n}-visual-actual-v1.json'
receipts=[B/f'section{n}-related-linux-actual-v1.json',B/f'section{n}-related-wine-actual-v1.json',window/'receipt.json',saved,visual]
for q in receipts:
 v=json.loads(q.read_bytes());assert v['passed'] is True and v['workflow_complete'] is True and v.get('source_drift',[])==[],str(q)
vr=json.loads(visual.read_bytes());assert vr.get('Root_actual_pixels_viewed',vr.get('Root_actually_viewed_all4_PNGs')) is True
counts={platform:{k:v[k] for k in ('tests_run','tests_passed','declared_skips','unavailable_records','failures','errors')} for platform in ('linux','wine') for v in [json.loads((B/f'section{n}-related-{platform}-actual-v1.json').read_bytes())]}
complete={'kind':'ROOT_ACTUAL_VALIDATED_SECTION_CLOSURE_BEFORE_PUBLICATION','section':n,'passed':True,'workflow_complete':True,'source_drift':[],'source_count':len(actual),'root_prior_HEAD':head,'description':a.description,'related':counts,'actual_GUI_snapshots':len(w['rows']),'actual_native_records':len(w['records']),'actual_PNGs_viewed':len(w['pngs']),'native_windows_game_chat_verified':False,'publication_still_pending':True,'full_validation_closed':False}
if n%5==0:
 f=B/f'full{n}-aggregate-actual-v1.json';v=json.loads(f.read_bytes());assert v['available_full_regression_closed'] is True and v['passed'] is True and v['source_files']==len(actual)
 assert (B/f'full{n}-aggregate-actual-v1.exit-code').read_bytes()==b'0\n'
 fgpath=B/f'full{n}-root-actual-guard-v1.json';fg=json.loads(fgpath.read_bytes())
 assert fg['section']==n and fg['source_sha256']==g['source_sha256'] and fg['source_additional_sha256']==g['source_additional_sha256']
 matches=[pin for pin in v['actual_receipt_pins'] if pin['path']==fgpath.as_posix()]
 assert matches==[{'path':fgpath.as_posix(),'bytes':fgpath.stat().st_size,'sha256':digest(fgpath)}]
 receipts.append(f);complete['full_validation_closed']=True;complete['full_summary']={k:v[k] for k in ('linux','wine','selected','legacy_gui_checks','legacy_saved_states','wine_environment_capability_skips')}
closure=B/f'section{n}-completion-actual-v1.json'
with closure.open('x') as f:json.dump(complete,f,ensure_ascii=False,indent=2);f.write('\n')
receipts.append(closure)
summary=a.description+' 相关Linux/Wine实际结果分别为'+json.dumps(counts,ensure_ascii=False)+'；真实窗口'+str(len(w['rows']))+'状态、'+str(len(w['records']))+'份原生记录及'+str(len(w['pngs']))+'幅实际查看的有界截图；完整Saved审计通过。'
packets={120:['p2-scenario-state-source-v1','full120-125-gates-source-v1','full120-125-gates-independent-source-v1'],121:['p2-next-attack-ready-source-v1'],122:['section122-retained-presence-source-v1'],123:['p2-last-accepted-cadence-source-v2'],124:['p2-amiya-recovery-eligibility-source-v5'],125:['p2-healing-preview-source-v1','full120-125-gates-source-v1','full120-125-gates-independent-source-v1']}[n]
for q in sorted(B.glob(f'section{n}-*source*')):
 if q.is_dir() and ((q/'MANIFEST.json').exists() or (q/'SOURCE_MANIFEST.json').exists()):packets.append(q.name)
command=['python3',str(B/'root-compact-section-spec-v1.py'),'--section',str(n),'--guard',gpath.name,'--topic',topic,'--slug',slug,'--summary',summary,'--next-action','本批在125节结束，不启动126；'+('完成125节全量、报告、提交推送后停止。' if n==125 else f'依序推进第{n+1}节，完成125节后停止。')]
for d in dict.fromkeys(packets):command+=['--packet',d]
for q in sorted(B.glob(f'section{n}-*actual*')):
 if q.is_dir():command+=['--actual',q.name]
 elif q.is_file():command+=['--file',q.name]
for q in (gpath,B/f'section{n}-original-source-v1.json',B/f'section{n}-root-local-plan-v1.json',B/'root-run-primary-v1.py',B/'root-feature-chain-v1.py',B/'root-feature-saved-chain-v1.py',B/'root-close-section-v1.py'):command+=['--file',q.name]
if n!=120:command+=['--file','root-feature-visual-record-v1.py']
if n==122:command+=['--file','root-section122-window-retry-v2.py']
if n%5==0:
 for q in sorted(B.glob(f'full{n}-*actual*')):
  if q.is_dir():command+=['--actual',q.name]
  elif q.is_file():command+=['--file',q.name]
 for name in ('root-full-chain-v1.py','root-full-aggregate-chain-v1.py'):command+=['--file',name]
 if n==125:command+=['--file','root-full125-prepare-v1.py']
for q in receipts:command+=['--receipt',q.relative_to(B).as_posix()]
for label in ('related-linux','related-wine','saved'):
 q=B/f'section{n}-{label}-actual-v1.exit-code';assert q.read_bytes()==b'0\n';command+=['--exit',q.name]
winexit=B/(f'section120-candidate-window-actual-v1.exit-code' if n==120 else f'section{n}-window-actual-v{a.window_version}.exit-code');assert winexit.read_bytes()==b'0\n';command+=['--exit',winexit.name]
for label in (('original-api','candidate-api') if n in (121,123,124) else ()):
 q=B/f'section{n}-{label}-actual-v1.exit-code';assert q.read_bytes()==b'0\n';command+=['--exit',q.name]
if n==120:
 q=B/'section120-original-window-actual-v2.exit-code';assert q.read_bytes()==b'0\n';command+=['--exit',q.name]
subprocess.run(command,check=True,cwd=R)
spec=B/f'root-section{n}-save-spec-v1.json';subprocess.run(['python3',str(B/'root-section-save-v3.py'),str(spec)],check=True,cwd=R)
if n%5==0:
 path=R/'DEVELOPMENT_CHECKPOINT.json';c=json.loads(path.read_bytes());c['full_validation_due']=False;c['current_section_save']['full_validation_due']=False;c['current_available_full_validation']={'section':n,'available_scope_passed':True,'receipt':f'research/p2-section{n}-{slug}/Root/full{n}-aggregate-actual-v1.json','native_windows_game_chat_verified':False};c['batch_stop_after_section']=125;c['batch_status']='VALIDATED_READY_TO_PUBLISH_AND_STOP' if n==125 else 'CONTINUE121_TO125'
 if n==125:c['next_action']='本批止于125节；126尚未启动，等待新的批次指令。'
 path.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
 verification=R/f'verification/sections/{n:03d}.json';v=json.loads(verification.read_bytes());v['full_validation_due']=False;v['full_available_regression_closed']=True;verification.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 fullfolder=R/f'verification/full-{n}';fullfolder.mkdir(exist_ok=True)
 (fullfolder/'summary.json').write_bytes((B/f'full{n}-aggregate-actual-v1.json').read_bytes())
 subprocess.run(['git','add','--',str(fullfolder.relative_to(R))],check=True,cwd=R)
subprocess.run(['python3',str(B/'root-section-publish-v3.py'),str(spec)],check=True,cwd=R)

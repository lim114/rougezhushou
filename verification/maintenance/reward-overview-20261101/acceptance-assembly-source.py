from pathlib import Path
from hashlib import sha256
import ast,json,re,sys,runpy,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/reward-overview-20261101';D=R/'research/reward-overview-20261101';BASE='84d5400478572c54c09951b5f7700a287779ffa5'
def read(p):return json.loads(p.read_bytes())
def pin(p):
 raw=p.read_bytes();return {'receipt':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def ids(folder):return re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. ok$',(B/folder/'stderr.txt').read_text('utf8'),re.M)
full=ids('related-delivery');current=ids('related-current');assert len(full)==len(set(full))==70 and len(current)==len(set(current))==30 and set(current)<=set(full);reused=sorted(set(full)-set(current));assert len(reused)==40
for name,count in [('related-delivery',70),('related-current',30)]:
 result=read(B/name/'results.json');assert result['passed']and result['tests_run']==count and not(result['failed']or result['errors']or result['skipped']or result['forbidden_external_calls']);assert read(B/name/'process.json')['actual_observed_exit']==0
for name,digest in read(B/'related-current/source-before.json').items():assert sha256((R/name).read_bytes()).hexdigest()==digest,name
prior=read(B/'related-delivery/source-before.json');changed=[p for p,digest in prior.items()if sha256((R/p).read_bytes()).hexdigest()!=digest];assert changed==['rouge/current_reward_view.py'];assert sha256((B/'viewport-source-before-layout-order.py').read_bytes()).hexdigest()==prior['rouge/current_reward_view.py']
def methods(raw):return{c.name+'.'+f.name:f for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)for f in c.body if isinstance(f,ast.FunctionDef)}
old=methods((B/'viewport-source-before-layout-order.py').read_text('utf8'));new=methods((R/'rouge/current_reward_view.py').read_text('utf8'));assert old.keys()==new.keys()
for name in old:
 if name!='CurrentRewardPanel.__init__':assert ast.dump(old[name])==ast.dump(new[name]),name
 else:
  positions=[]
  for fun in(old[name],new[name]):
   indexes=[i for i,n in enumerate(fun.body)if isinstance(n,ast.Assign)and ast.unparse(n)=='layout = QVBoxLayout(body)'];assert len(indexes)==1;positions.append(indexes[0]);del fun.body[indexes[0]]
  assert ast.dump(old[name])==ast.dump(new[name])and positions[0]>positions[1]
old=methods((D/'before-enemy_overview.py').read_text('utf8'))['MechanismDelegate.sizeHint'];new=methods((R/'rouge/wrapped_item_delegate.py').read_text('utf8'))['WrappedItemDelegate.sizeHint'];normalized=ast.parse(ast.unparse(new).replace('self.columns','(5, 6)')).body[0];assert ast.dump(old)==ast.dump(normalized)
def funcs(raw):return{n.name:ast.dump(n)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
a=funcs((D/'before-current_reward_reference.py').read_text('utf8'));b=funcs((R/'rouge/current_reward_reference.py').read_text('utf8'));assert set(b)-set(a)=={'outcome_lines'};assert[k for k in a if a[k]!=b[k]]==['row_text']
for p in ['rouge/collapsible_section.py','licenses/superqt-BSD-3-Clause.txt','licenses/Qt-LGPL-3.0-only.txt','licenses/Qt-GPL-3.0-only.txt','rouge/current_battle_view.py','rouge/current_battle_reference.py','rouge/player_map_reader.py','rouge/current_settlement_modes_view.py','rouge/current_settlement_modes_reference.py','rouge/player_game_binding.py','rouge/run_state.py','rouge/app.py']:
 assert (R/p).read_bytes()==subprocess.check_output(['git','show',BASE+':'+p]),p
oldfile=R/'.cache/reward-overview-selectors-before.py';oldfile.write_bytes((D/'before-verify_full_available.py').read_bytes());before=runpy.run_path(str(oldfile))['maintained_selectors']();after=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']();assert len(before)==744 and len(after)==745 and after[:744]==before
write(B/'selector-prefix.json',{'previous_count':744,'current_count':745,'old_order_preserved':True,'added':list(after[744:]),'not_full_suite_execution':True})
n=read(B/'native-delivery/window.json');assert n['passed']and n['unique_checks']==187 and not n['source_drift']and not any(n['external_operation_attempts'].values());assert read(B/'native-delivery/process.json')['actual_observed_exit']==0
for p,digest in n['source_sha256_after'].items():assert sha256((R/p).read_bytes()).hexdigest()==digest,p
write(B/'accepted-methods.json',{'passed_listed_unit_scope':True,'distinct_accepted_method_count':70,'current_focused30':current,'reused40_unchanged_method_successes':reused,'single_current_full70_run_claimed':False,'previous70_source_current_difference':'Only constructor layout created before setWidget per Qt documented ordering; all other AST statements unchanged. Current30 and native187 validate final layout;40 unchanged successes reused.','original_failed_run':{'tests_run':56,'errors':1,'actual_exit':1,'reason':'New baseline module fixture lacked __file__; new class not executed. Original55 other successes are not counted as a successful full run.'},'final_native':{'unique_named_assertions':187,'not187_distinct_scenarios':True,'receipt':pin(B/'native-delivery/window.json')},'original_models_and_detailed_texts':'All184 pinned stages and1855 reward-source texts matched actual pre-change function; numeric/reward mechanics not changed.','ordered_selectors':745,'whole_program_video_P3_complete':False})
print(json.dumps({'accepted_methods':70,'current_focused':30,'reused':40,'native_unique_assertions':187,'selectors':745,'only_Qt_constructor_statement_order_changed_since70':True}))

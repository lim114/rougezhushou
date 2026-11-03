"""Non-GUI actual calculation probe with the unchanged legacy observer functions."""
from pathlib import Path
from hashlib import sha256
import argparse,ast,functools,json,sys,time
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R),str(R/'scripts')]
p=argparse.ArgumentParser();p.add_argument('--order',choices=['early_app','capture_only'],required=True);a=p.parse_args()
original=R/'.cache/full425-prepared/attempt-3/bound-legacy/window.py';raw=original.read_bytes();tree=ast.parse(raw.decode('utf8'))
names={'_deadline_check100','_replace_binding100','_increment100','_install_narrow_observers100'}
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(functions)==4 and 'rouge.app'not in sys.modules
state={'functools':functools,'time':time,'_deadline100':time.perf_counter()+1200,'_count_enabled100':True,'_restorations100':[],'entry_counts090':{},'profile_case090':None,'profile_trace090':[]}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(original),'exec'),state)
if a.order=='early_app':import rouge.app as app
import rouge.capture as capture
original_enumeration=capture.list_game_windows;calls=[]
def isolated():calls.append(True);return []
capture.list_game_windows=isolated
state['_install_narrow_observers100']()
if a.order=='capture_only':import rouge.app as app
import rouge.damage as damage,rouge.estimate as estimate,rouge.reporting as reporting
matches={'calculate_damage':app.calculate_damage is damage.calculate_damage,'format_estimate':app.format_estimate is estimate.format_estimate,'format_report':app.format_report is reporting.format_report}
scenario={'operator':'mechanist','skill':1,'elite':2,'level':90,'skill_rank':10,'potential':1,'trust':100,'module_id':None,'module_level':0,'enemy_defense':0,'enemy_resistance':0,'relic_ids':[]}
before=dict(state['entry_counts090']);actual=app.calculate_damage(scenario);after=dict(state['entry_counts090']);delta={k:after.get(k,0)-before.get(k,0)for k in sorted(set(before)|set(after))}
from PySide6.QtWidgets import QApplication
out=R/f'verification/sections/425-observer-import-order-{a.order}.json';assert not out.exists()
record={'section':425,'order':a.order,'actual_alias_identity_matches_observers':matches,'actual_same_call_entry_delta':delta,'actual_calculation_returned':True,'result_sha256':sha256(json.dumps(actual,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()).hexdigest(),'unchanged_original_observer_source_sha256':sha256(raw).hexdigest(),'probe_source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'actual_enumeration_alias_is_fixture':app.list_game_windows is isolated,'QApplication_created':QApplication.instance()is not None,'game_operations':0,'chat_requests':0,'private_state_access':False,'counters_or_result_rewritten':False}
assert not record['QApplication_created'];out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
for owner,name,value in reversed(state['_restorations100']):setattr(owner,name,value)
capture.list_game_windows=original_enumeration
print(json.dumps(record,ensure_ascii=False))

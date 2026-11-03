from pathlib import Path
from hashlib import sha256
import json,re,unittest,sys,ast,subprocess,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/battle-overview-sections-20261101';D=R/'research/battle-overview-sections-20261101';BASE='f43b87e6f995358c499c65498d5ee315bd88e92c'
def read(p):return json.loads(p.read_bytes())
def pin(p):return {'receipt':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def lines(folder):return dict(re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. (ok|FAIL|ERROR)$',(folder/'stderr.txt').read_text('utf8'),re.M))
initial=lines(B/'related');final=lines(B/'focused-final');assert len(initial)==85 and len(final)==18 and set(final.values())=={'ok'}
assert {x for x,v in initial.items()if v!='ok'}<=set(final)
reuse={x:v for x,v in initial.items()if x not in final};assert len(reuse)==68 and set(reuse.values())=={'ok'}
def cases(s):
 for c in s:
  if isinstance(c,unittest.TestCase):yield c.id()
  else:yield from cases(c)
ids=list(cases(unittest.TestLoader().loadTestsFromNames(read(B/'related/results.json')['selectors'])));assert len(ids)==len(set(ids))==86 and set(ids)==set(reuse)|set(final)
def methods(s):return {c.name+'.'+f.name:ast.dump(f)for c in ast.parse(s).body if isinstance(c,ast.ClassDef)for f in c.body if isinstance(f,ast.FunctionDef)}
for path in ['tests/test_event_battle_reader_review.py','tests/test_current_event_battles_view_326.py']:
 old=methods((D/('before-'+Path(path).name)).read_text('utf8'));new=methods((R/path).read_text('utf8'))
 retained=[x.split('.',1)[1]for x in reuse if x.startswith(path[:-3].replace('/','.')+'.')]
 assert all(old[k]==new[k]for k in old if k.split('.')[-1]in retained)
for path,row in read(B/'first-suite-inflight-source.json')['source'].items():assert sha256((R/path).read_bytes()).hexdigest()==row['sha256'],path
old=methods((D/'before-current_battle_view.py').read_text('utf8'));new=methods((R/'rouge/current_battle_view.py').read_text('utf8'));assert old.keys()==new.keys();changed=[k for k in old if old[k]!=new[k]];assert changed==['CurrentBattlePanel.__init__','CurrentBattlePanel.refresh_reference','CurrentBattlePanel._sync_enemy_grid'],changed
def funcs(s):return {n.name:ast.dump(n)for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
assert funcs((D/'before-player_map_reader.py').read_text('utf8'))==funcs((R/'rouge/player_map_reader.py').read_text('utf8'))
for path in ['rouge/collapsible_section.py','licenses/superqt-BSD-3-Clause.txt']:
 assert (R/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path])
oldfile=R/'.cache/battle-overview-selectors-before.py';oldfile.write_bytes(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']));oldselectors=runpy.run_path(str(oldfile))['maintained_selectors']();newselectors=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']();assert len(oldselectors)==742 and len(newselectors)==743 and newselectors[:742]==oldselectors
write(B/'selector-prefix.json',{'previous_count':742,'current_count':743,'old_order_preserved':True,'added':list(newselectors[742:]),'not_full_suite_execution':True})
write(B/'accepted-methods.json',{'passed_listed_unit_scope':True,'distinct_current_method_ids':sorted(ids),'accepted_method_count':86,'current_focused_18':sorted(final),'reused_68_unchanged_initial_passes':sorted(reuse),'initial_85_overall_passed':False,'initial_failures':2,'initial_errors':1,'initial_nonpassing_method_ids':[x for x,v in initial.items()if v!='ok'],'initial_process':pin(B/'related/process.json'),'final_process':pin(B/'focused-final/process.json'),'single_fresh_full86_run_claimed':False,'source_boundary':'Initial production source unchanged except shared MapReader QWidget background CSS. Its Python factory functions unchanged. Current focused18 and native99 separately validate final CSS. Initial source snapshot captured while suite running, not before start; retained method sources unchanged.','changed_production_methods':changed,'final_source_color_case_adds_one_current_method':True})
print(json.dumps({'accepted_distinct_methods':len(ids),'reused':len(reuse),'focused_current':len(final),'selectors':len(newselectors),'same_application_source_count':len(list((R/'rouge').rglob('*.py')))},ensure_ascii=False))

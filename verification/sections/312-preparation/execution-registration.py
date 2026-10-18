from pathlib import Path
from hashlib import sha256
import ast,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
name='scripts/verify_full_available.py';old=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT).decode('utf8')
anchor="ADDITIONAL_MODULES += ('tests.test_boss_hunt_reference_311', 'tests.test_boss_hunt_view_311', 'tests.test_boss_hunt_integration_311')"
assert old.count(anchor)==1
modules=tuple('tests.test_gold_boss_'+n+'_312'for n in ('reference','view','integration'))
new=old.replace(anchor,anchor+'\nADDITIONAL_MODULES += '+repr(modules))
(ROOT/name).write_bytes(new.encode('utf8'))
def selectors(s):
 ns={'__file__':str(ROOT/name),'__name__':'registry_for_source_comparison'};exec(compile(s,str(ROOT/name),'exec'),ns);return ns['maintained_selectors']()
before,after=selectors(old),selectors(new)
assert len(before)==484 and len(after)==487 and after[:-3]==before and after[-3:]==list(modules)
def methods(s):
 cls=next(n for n in ast.parse(s).body if isinstance(n,ast.ClassDef)and n.name=='BattlePreviewPanel')
 return{n.name:ast.dump(n,include_attributes=False)for n in cls.body if isinstance(n,ast.FunctionDef)}
prior=methods(subprocess.check_output(['git','show','HEAD:rouge/battle_view.py'],cwd=ROOT).decode('utf8'))
current=methods((ROOT/'rouge/battle_view.py').read_text('utf8'))
preserved=[n for n in prior if n.startswith(('_refresh_enemy_form','open_enemy_form','_refresh_boss_','open_boss_'))]
assert len(preserved)==8 and all(prior[n]==current[n]for n in preserved)
out=ROOT/'verification/sections/312-preparation';report={'before_count':len(before),'after_count':len(after),'original_ordered_prefix_unchanged':True,'new_selectors':modules,'source_sha256':sha256((ROOT/name).read_bytes()).hexdigest(),'previous_four_reader_pairs_AST_unchanged':preserved,'earlier_necessary_attempt1_registry_is_superseded_for_collection_order_only':True,'necessary_tests_will_reexecute_against_final_source':True}
(out/'maintained-registration-first-preparation.json').write_bytes((out/'maintained-registration.json').read_bytes())
(out/'maintained-registration.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
(out/'execution-registration.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(report,ensure_ascii=False))

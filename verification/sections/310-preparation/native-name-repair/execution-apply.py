from pathlib import Path
from hashlib import sha256
import ast,json,shutil,symtable,builtins
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'.cache/p3-310-native-repair';p=ROOT/'scripts/verify_boss_cycle_window_310.py'
old=p.read_bytes();new=(source/'candidate/scripts/verify_boss_cycle_window_310.py').read_bytes()
assert sha256(old).hexdigest()=='1b49430a61b266a052d46c2eb62f9a760d11922485f78a491521972c4b817807'
assert sha256(new).hexdigest()=='f1cf1bfc5d294b719208b4b5fc6edeb7b594537ff461d818b6f37ab2361a2469'
assert old.count(b'keyS')==1 and old.replace(b'keyS',b'KEYS')==new
t=symtable.symtable(new.decode('utf8'),str(p),'exec');defined={s.get_name()for s in t.get_symbols()if s.is_assigned()or s.is_imported()or s.is_namespace()}|set(dir(builtins))|{'__file__','__name__','__doc__','__package__'}
def unknowns(table):
    found=[(table.get_name(),s.get_name())for s in table.get_symbols()if s.is_referenced()and s.is_global()and s.get_name()not in defined]
    for child in table.get_children():found+=unknowns(child)
    return found
assert not unknowns(t)
out=ROOT/'verification/sections/310-preparation/native-name-repair';out.mkdir();(out/'original-before-name-repair.py').write_bytes(old)
for name in('READY.json','static-review.json'):(out/name).write_bytes((source/name).read_bytes())
independent=ROOT/'.cache/p3-310-native-independent-static-review';assert sha256((independent/'HANDOFF.json').read_bytes()).hexdigest()=='7ba894c2566cbd22e299bd513f7bd66da3b8ca3a926017d8bcf54a1c0124a367'
shutil.copytree(independent,out/'independent-static-review')
p.write_bytes(new);(out/'execution-apply.py').write_bytes(Path(__file__).read_bytes())
r={'section':310,'only_replacement':'one Name keyS -> KEYS','application_models_views_data_and_unit_assertions_changed':False,'original_actual_failures':['verification/sections/310-native-attempt1/actual/window.json','verification/sections/310-native-attempt2/actual/window.json'],'source_SHA256_after':sha256(new).hexdigest(),'root_post_fix_undefined_global_names':unknowns(t),'actual_native_pending':True,'all_prior_gate_labels_and_actual_workflow_preserved':True}
(out/'applied.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r))

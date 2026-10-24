from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from rouge import current_boss_documents as model
p=R/'scripts/verify_current_boss_documents_window_369.py';raw=p.read_bytes();s=raw.decode('utf8')
related=model.related_entities(model.reference('ro6_b_5','0'),'0')
assert [(x['key'],x['entity_id'])for x in related]==[('1','enemy_2148_shorbb'),('6','enemy_2149_shorsm')]
old="                    for related_key in('1','2'):";assert s.count(old)==1;s=s.replace(old,"                    for related_key in('1','6'):")
old="""                for name in(provider.MANIFEST,*manifest['files']):
                    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())"""
new="""                if 'files'in manifest:
                    members=set(manifest['files'])
                elif 'runtime_files'in manifest and 'data_file'in manifest:
                    members=set(manifest['runtime_files'])|{manifest['data_file']}|set(manifest.get('build_authority_files',{}))
                else:
                    raise ValueError('Unknown declared source manifest schema: '+provider.MANIFEST)
                for name in sorted({provider.MANIFEST,*members}):
                    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())"""
assert s.count(old)==1;s=s.replace(old,new);ast.parse(s)
out=R/'verification/sections/369-native-reference-repair';out.mkdir()
(out/'before-verify_current_boss_documents_window_369.py').write_bytes(raw)
p.write_text(s,encoding='utf8',newline='\n')
record={'section':369,'actual_failed_native_receipt':'verification/sections/369-native-attempt1/actual/window.json','actual_failed_native_exit':1,'actual_error':'StopIteration locating hardcoded related key2','actual_fixed_current_references':related,'source':'current_boss_documents.reference(ro6_b_5,0) plus exact pinned current level bindings','repair_scope':['native test exact independent entity index6 instead of nonexistent2','native isolated source cloning supports the same actual original manifest schemas already proven in bound_files'],'product_model_or_parameters_changed':False,'original_76_unique_check_scope_removed':False,'native_budget_unchanged_ms':180000,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(p.read_bytes()).hexdigest(),'necessary_rerun_required_for_changed_selected_harness_hash':True,'at_utc':datetime.now(timezone.utc).isoformat()}
(out/'repair-scope.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'exact_reference_harness_fix_applied_not_validated':True,'key1_and_key6_preserved':True,'source_clone_scope_not_reduced':True}))

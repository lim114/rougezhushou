from pathlib import Path
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
import json,sys,ast,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];D=R/'research/battle-document-20261101';B=R/'verification/maintenance/battle-document-20261101'
def functions(raw):return{n.name:ast.dump(n)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
from rouge import current_battle_reference as model
old=ModuleType('rouge._before_document_model');old.__file__=str(R/'rouge/current_battle_reference.py');old.__package__='rouge';exec(compile((D/'before-current_battle_reference.py').read_bytes(),'<prior-model>','exec'),old.__dict__)
a=functions((D/'before-current_battle_reference.py').read_bytes());b=functions((R/'rouge/current_battle_reference.py').read_bytes());assert a.keys()==b.keys()and[k for k in a if a[k]!=b[k]]==['enemy_text']
ref=model.packet();ids=ref['version']['current']['details']['stages'];total=dedup=0
with patch.object(model,'packet',return_value=ref),patch.object(old,'packet',return_value=ref):
 for sid in ids:
  current=model.stage_reference(sid);assert current==old.stage_reference(sid)
  for e in current['enemies']:
   total+=1;part=model.enemy_text(e).split('【介绍与机制】',1)[1].split('【适用提醒】',1)[0]
   if e['description']:assert e['description']in part
   for line in e['abilities']:assert line in part
   if e['description']and e['description']in e['abilities']:dedup+=1
old_full=runpy.run_path(str(D/'before-verify_full_available.py'));old_full['maintained_selectors'].__globals__['ROOT']=R;new_full=runpy.run_path(str(R/'scripts/verify_full_available.py'));a=old_full['maintained_selectors']();b=new_full['maintained_selectors']();assert b[:-2]==a and b[-2:]==['tests.test_battle_document_review','tests.test_interpret_lookup_review']
raw=json.loads((B/'public-pipeline/results.json').read_bytes());assert raw['passed']and len(raw['rows'])==6 and all(x['all_interpreted_facts_equal']for x in raw['rows']);times=[{'second':x['second'],'page_before':x['readers']['before']['page'],'page_after':x['readers']['after']['page'],'before_ms':x['readers']['before']['total_ms'],'after_ms':x['readers']['after']['total_ms'],'visible_labels_before_ms':x['readers']['before']['stages_ms']['visible_labels'],'visible_labels_after_ms':x['readers']['after']['stages_ms']['visible_labels']}for x in raw['rows']]
value={'fixed_stages':len(ids),'exact_enemy_references':total,'intro_also_present_in_abilities':dedup,'all_stage_models_equal_prior':True,'all_distinct_mechanism_paragraphs_preserved':True,'only_model_function_changed':'enemy_text: omit identical intro already present in abilities, combine wholly missing explanation. Do not collapse separate ability entries or alter model array/counts.','old_selectors':len(a),'current_selectors':len(b),'previous_selector_prefix_unchanged':True,'pipeline_pairs':times,'all_six_pipeline_facts_equal':True,'pipeline_inputs':'public reference video desktop composites, not current game/client accuracy','stable_end_to_end_speedup_claimed':False,'current_UI_or_game_accuracy_proven_by_pipeline':False}
(B/'reference-audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(value,ensure_ascii=False))

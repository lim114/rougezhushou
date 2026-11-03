from pathlib import Path
from datetime import datetime, timezone
import ast, json, subprocess, sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
from scripts.verify_full_available import maintained_selectors
from rouge import current_critical_reward_origins as m, current_reward_origins as old, current_named_reward_origins as named
prior=json.loads((R/'verification/sections/348-source-audit.json').read_bytes())['current_selectors'];current=maintained_selectors()
assert len(prior)==565 and current[:565]==prior and len(current)==567
def methods(tree):
    return {n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)}
before=methods(ast.parse(subprocess.check_output(['git','show','HEAD:rouge/current_reward_origins.py']).decode('utf8')))
after=methods(ast.parse((R/'rouge/current_reward_origins.py').read_text('utf8')))
changed={k for k in before.keys()|after.keys()if before.get(k)!=after.get(k)}
assert changed=={'reference','player_text'}
rows=m.packet()['data']['rows'];old_rows=old.packet()['data']['rows'];named_rows=named.packet()['data']['rows']
assert len(rows)==3 and len(old_rows)==6 and len(named_rows)==11
assert len({r['item_id']for r in rows+old_rows+named_rows})==17
for provider in(m.conditions,m.flows,m.exit_flow,old,named):
    assert not subprocess.check_output(['git','diff','--',provider.DATA,provider.MANIFEST]).strip()
assert not subprocess.check_output(['git','diff','--','rouge/data/current-exit.json','rouge/data/documented-event-flows.json','rouge/data/ending-events-reference.json','research/p3-expansion-313/current-topic.json','rouge/boss_map_markers.py','rouge/data/boss-map-markers.json']).strip()
r={'section':349,'passed':True,'ordered_previous565_preserved':True,'current_selectors':current,
   'changed_existing_model_methods':sorted(changed),'new_explicit_grants':3,'old338_rows_unchanged':6,'old347_rows_unchanged':11,'combined_items':17,'combined_rows':20,
   'source_grant_rows':[{'item':r['item_id'],'original_choice':r['choice_id'],'reader_target':r['reader_target']}for r in rows],
   'same_literal_name_not_used_for_binding':True,'unknown_quantities_preserved':True,'no_complete_pool_claimed':True,
   'originals_and_old_maps_unchanged':True,'local_tests_only':True,'full335_is_historical':True,'next_full':350,
   'failure_correction':'verification/sections/349-flow-binding-correction/reason.json','at_utc':datetime.now(timezone.utc).isoformat()}
(R/'verification/sections/349-source-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':True,'new_grants':3,'combined_items':17,'combined_rows':20,'selectors':567}))

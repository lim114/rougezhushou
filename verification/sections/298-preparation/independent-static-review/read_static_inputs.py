"""Read JSON and AST only; no product imports or tests/Qt execution."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
data=json.loads((ROOT/'rouge/data/event-node-requirements.json').read_bytes())
catalog=json.loads((ROOT/'rouge/data/node-catalog.json').read_bytes())
manifest=json.loads((ROOT/'research/p3-event-node-requirements-298/source-manifest.json').read_bytes())
files=['rouge/event_node_requirements.py','rouge/data/event-node-requirements.json',
 'rouge/node_catalog.py','rouge/event_planning.py','rouge/node_catalog_view.py','rouge/player_node_information.py',
 'tests/test_event_node_requirements_298.py','research/p3-event-node-requirements-298/source-manifest.json']
pins={name:{'sha256':sha256((ROOT/name).read_bytes()).hexdigest(),'bytes':(ROOT/name).stat().st_size}for name in files}
bound={}
for name,pin in manifest['files'].items():
 raw=(ROOT/name).read_bytes();bound[name]={'sha_matches':sha256(raw).hexdigest()==pin['sha256'],'bytes_match':len(raw)==pin['bytes']}
rows=[]
for identity,reference in data['events'].items():
 event=next(e for e in catalog['events']if e['id']==identity)
 rows.append({'id':identity,'title':event['title'],'floors':event['floors'],'natural':event['natural'],
  'node_types':event['node_types'],'expected_full_event_equals_catalog':data['expected_events'][identity]==event,
  'excluded_main_floors':reference['documented_excluded_main_floors'],
  'technology':reference['technology_enabling_reference']})
other_floors=[{'id':e['id'],'title':e['title'],'floors':e['floors'],'natural':e['natural']}
 for e in catalog['events']if e['floors']and e['id']not in data['events']]
result={'kind':'SECTION298_STATIC_INPUT_REVIEW_NOT_PRODUCT_EXECUTION','six_target_catalog_rows':rows,
 'other_catalog_rows_with_floor_filters':other_floors,'manifest_members':bound,'source_pins':pins,
 'product_imported_or_executed':False,'tests_or_Qt_executed':False,'live_modified':False}
(HERE/'static-inputs.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'six':[{k:v for k,v in row.items()if k!='technology'}for row in rows],
 'other_floors':other_floors,'manifest_all_members_match':all(all(v.values())for v in bound.values())},ensure_ascii=False,indent=2))

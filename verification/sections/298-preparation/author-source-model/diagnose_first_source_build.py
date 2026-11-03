"""Read exact DOM attributes behind the first source-build rejection."""
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('candidate_builder',HERE/'candidate/scripts/build_event_node_requirements_298.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
catalog=json.loads((ROOT/b.CATALOG).read_bytes());out=[]
for _,(_,_,events,_) in enumerate(b.RULES):
    for event_id in events:
        event=next(e for e in catalog['events'] if e['id']==event_id)
        for name,(path,_) in b.SOURCES.items():
            if not name.startswith('events-'):continue
            doc=b._Document((ROOT/path).read_text(encoding='utf8'))
            for group in (n for n in doc.nodes if b._class(n,'IS-event-data')):
                scenes=[n for n in b._children(group) if b._class(n,'scene')]
                if scenes and scenes[0].attrs.get('data-index')==event['scenes'][0]['attributes']['data-index']:
                    out.append({'event':event_id,'node_type':event['node_types'],'catalog_scene_count':len(event['scenes']),
                        'catalog_scene_attributes':event['scenes'][0]['attributes'],'HTML':path,
                        'actual_scene_count':len(scenes),'actual_scene_attributes':scenes[0].attrs})
target=HERE/'first-source-build-diagnosis.json';target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))

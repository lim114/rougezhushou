"""Reproduce literal destination references from fully audited selected source rows."""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
FIELDS=('title','description','lockedCoverDesc','nextSceneId','type','isHiddenChoice')
SCENE_FIELDS=('title','description','background')


def fingerprint(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
        separators=(',',':')).encode('utf8')).hexdigest()


def build(root=ROOT):
    path=root/'research/p3-original-destinations'
    selected=json.loads((path/'selected-original.json').read_text(encoding='utf8'))
    original=json.loads((root/'rouge/data/node-events.json').read_text(encoding='utf8'))
    catalog=json.loads((root/'rouge/data/node-catalog.json').read_text(encoding='utf8'))
    assert selected['source']==original['source']['game_data']
    assert {k:{f:r.get(f) for f in FIELDS} for k,r in selected['choices'].items()}==original['choices']
    assert {k:{f:r.get(f) for f in SCENE_FIELDS} for k,r in selected['choiceScenes'].items()}==original['scenes']
    rows={};matched=0;unresolved=[]
    for choice_id,choice in original['choices'].items():
        target=choice['nextSceneId'];bindings=[]
        if target:
            if target not in original['scenes']:unresolved.append(target)
            assert target in original['scenes'],('missing literal scene',choice_id,target)
            for event in catalog['events']:
                for scene in event['scenes']:
                    if target in scene['game_scene_ids']:
                        bindings.append({'event_id':event['id'],'scene_key':scene['key'],
                            'scene_record_sha256':fingerprint(scene)})
            matched+=bool(bindings)
        rows[choice_id]={'next_scene_id':target,
            'original_record_sha256':fingerprint(choice),
            'destination_record_sha256':fingerprint(original['scenes'][target]) if target else None,
            'catalog_references':bindings}
    data={'schema_version':1,'sources':{k:catalog['sources'][k] for k in
        ('original_game_data','cached_community_catalog')},
        'runtime_source_sha256':{name:sha256((root/'rouge/data'/name).read_bytes()).hexdigest()
            for name in ('node-events.json','node-catalog.json','event-planning-reference.json')},
        'coverage':{'original_choice_count':len(rows),
            'explicit_destination_count':sum(bool(r['next_scene_id']) for r in rows.values()),
            'destination_with_catalog_reference_count':matched,
            'source_scene_relation_verified':False,'actual_game_execution_verified':False},
        'choices':rows}
    targetpath=root/'rouge/data/original-destinations.json'
    targetpath.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(data['coverage'],ensure_ascii=False))
    return data


if __name__=='__main__':build(Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT)

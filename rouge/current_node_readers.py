"""Source-checked links from the fixed node catalogue to current event readers."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import importlib,json
from . import node_catalog,expansion_reference
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-node-readers-332';DATA='rouge/data/current-node-readers.json';LEGACY='rouge/data/node-catalog.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='348ccd495b3a80e987a70c79f4ab24c54651948b61343305b57372c829e13e35'
PROVIDERS={'rest':'current_rest_travel','shop':'current_unattended_shop','resources':'current_resource_events','lake':'current_lake','encounters':'current_encounters','sand':'current_sand_reference','ritual':'current_ritual_reference','box':'box_event_reference'}
NOTICE='当前固定版本事件资料。请核对实际游戏版本及选项；不代表本局已出现、已选择、已领取或已生效。'

def same(a,b):
    if type(a)is not type(b):return False
    if type(b)is dict:return a.keys()==b.keys()and all(type(k)is str and same(a[k],b[k])for k in a)
    if type(b)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    if type(b)is tuple:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,LEGACY,PACK+'/source-ledger.json'}
        if m['schema']!='current_node_readers_332_manifest_v1'or m['game_commit']!=expansion_reference.NEW_COMMIT or set(m['files'])!=expected:return None
        values={}
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in p.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            content=p.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            values[name]=content
        data=json.loads(values[DATA])
        if data['schema']!='current_node_readers_332_v1'or set(data['current_sources'])!=set(PROVIDERS):return None
        return {'data':data,'source_identity':MANIFEST_SHA256,'actual_same_version':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def provider_reference(reader,event_id):
    if reader not in PROVIDERS:return None
    return importlib.import_module('.'+PROVIDERS[reader],__package__).reference(event_id)

def matches_current(row,reference):
    if reference is None:return False
    identity=json.loads(json.dumps(reference['source_identity']))
    scenes={k:v for k,v in reference['data']['originals']['scenes'].items()if v['title']==row['title']}
    return same(identity,row['current_source_identity'])and same(reference['event'],row['current_event'])and same(scenes,row['current_original_scenes'])

def binding_for(record):
    if type(record)is not dict or type(record.get('id'))is not str or not record['id'].startswith('community_group_'):return None
    if record['id']=='community_group_011':
        from .current_memory_tree import catalogue_binding
        return catalogue_binding(record)
    if record['id']=='community_group_020':
        from .current_lone_dog import catalogue_binding
        return catalogue_binding(record)
    if record['id']=='community_group_017':
        from .current_cave import catalogue_binding
        return catalogue_binding(record)
    if record['id']in('community_group_007','community_group_009'):
        from .current_vine_events import catalogue_binding
        return catalogue_binding(record)
    try:
        p=packet()
        if p is None:return None
        row=p['data']['bindings'].get(record['id'])
        if row is None or any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
        if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
        if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
        reference=provider_reference(row['reader'],row['current_event_id'])
        if not matches_current(row,reference):return None
        return {**deepcopy(row),'source_identity':(p['source_identity'],deepcopy(row['current_source_identity'])),'reference_only':True,'actual_node_version_confirmed':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def recheck(binding):
    if type(binding)is not dict or type(binding.get('expected_summary'))is not dict:return None
    fresh=binding_for(binding['expected_summary']);return fresh if same(fresh,binding)else None

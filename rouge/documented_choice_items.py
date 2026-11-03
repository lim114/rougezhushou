"""Documented named-item reading, separate from typed grant and actual state."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_021'
SCENE=EVENT+':scene:0'
CHOICE=SCENE+':choice:0'
ITEM='rogue_6_relic_final_1'
DATA='rouge/data/documented-choice-items.json'
MANIFEST='research/p3-documented-choice-items-295/source-manifest.json'
MANIFEST_SHA256='e98f48e0629307f9fdbc98c8e6cb8ca4b6ffbe93e3939c3cf4d489ef476853e9'
_CACHE={}


def _same_json(value,expected):
    if type(value) is not type(expected):return False
    if type(expected) is dict:
        return (value.keys()==expected.keys() and all(type(key) is str for key in value)
                and all(_same_json(value[key],expected[key]) for key in expected))
    if type(expected) is list:
        return len(value)==len(expected) and all(_same_json(a,b) for a,b in zip(value,expected))
    return value==expected


def _valid_schema(data):
    if (type(data) is not dict or type(data.get('schema_version')) is not int or data['schema_version']!=1
            or data.get('event_id')!=EVENT or data.get('scope')!='documented_named_item_not_grant'
            or data.get('current_server_verified') is not False or data.get('inventory_updated') is not False
            or data.get('source_scene_link_verified') is not False
            or any(data.get(key) is not None for key in ('actual_reward','actual_quantity','actual_selectable'))):return False
    ref=data['reference'];item=data['item'];event=data['expected_event']
    if (event['id']!=EVENT or event['scenes'][0]['key']!=SCENE
            or event['scenes'][0]['choices'][0]['key']!=CHOICE
            or event['scenes'][0]['choices'][0]['game_choice_ids']!=[]
            or ref['reference_id']!=CHOICE+':documented-item:'+ITEM
            or (ref['event_id'],ref['scene_key'],ref['choice_key'],ref['item_id'])!=(EVENT,SCENE,CHOICE,ITEM)
            or ref['reference_kind']!='documented_named_item' or ref['item_type']!='RELIC'
            or item['id']!=ITEM or item['type']!='RELIC' or item['iconId']!=ITEM
            or ref['name']!=item['name'] or ref['icon_reference']['item_id']!=ITEM
            or ref['icon_reference']['icon_id']!=ITEM
            or ref['source_scene_link_verified'] is not False or ref['original_choice_entry_bound'] is not False
            or ref['original_item_pointer_present'] is not False
            or any(ref[key] is not None for key in ('quantity_reference','actual_reward','actual_selectable'))):return False
    return (ref['choice_title']==event['scenes'][0]['choices'][0]['title']
        and ref['choice_description']==event['scenes'][0]['choices'][0]['description']
        and ref['icon_reference']['file']=='rouge/data/relic-icons/'+ITEM+'.png')


def _validated_packet():
    """Rehash all bound bytes every time; only unchanged parsing is cached."""
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);blobs={}
        for relative,expected in manifest['files'].items():
            path=ROOT/relative
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():return None
            blob=path.read_bytes()
            if len(blob)!=expected['bytes'] or hashlib.sha256(blob).hexdigest()!=expected['sha256']:return None
            blobs[relative]=blob
        payload=blobs[DATA];key=(MANIFEST_SHA256,hashlib.sha256(payload).hexdigest())
        if key not in _CACHE:
            data=json.loads(payload)
            if not _valid_schema(data):return None
            _CACHE.clear();_CACHE[key]=data
        data=_CACHE[key]
        current=json.loads(blobs['rouge/data/node-catalog.json'])
        event=next((row for row in current['events'] if row.get('id')==EVENT),None)
        if not _same_json(event,data['expected_event']):return None
        return data
    except (OSError,ValueError,KeyError,TypeError,AttributeError,IndexError):return None


def source_data():
    """Return an isolated validated source copy, without a data override API."""
    data=_validated_packet()
    return deepcopy(data) if data is not None else None


def _unknown(kind):
    return {'status':'unknown','reference_kind':kind,'event_id':EVENT,'source_valid':False,
        'items':[],'sources':None,'source_reference':None,
        'quantity_reference':None,'actual_reward':None,'actual_quantity':None,'actual_selectable':None,
        'source_scene_link_verified':False,'current_server_verified':False,'inventory_updated':False,
        'notice':'物品资料暂时无法核对；旧条目与图标已清除，保留事件原文，领取与资格仍未知。'}


def event_item_references(event_id):
    """One exact documented item; unrelated IDs never scan the source packet."""
    if type(event_id) is not str or event_id!=EVENT:return None
    data=_validated_packet();result=_unknown('documented_named_items')
    if data is None:return result
    result.update(status='documented_reference',source_valid=True,items=[deepcopy(data['reference'])],
        sources=deepcopy(data['sources']),source_reference=deepcopy(data['source_reference']),notice=data['notice'])
    return result


def item_details(event_id,scene_key,choice_key,item_id):
    """Freshly validate all four IDs before returning full item reading details."""
    if type(event_id) is not str or event_id!=EVENT:return None
    if (type(scene_key) is not str or type(choice_key) is not str or type(item_id) is not str
            or (scene_key,choice_key,item_id)!=(SCENE,CHOICE,ITEM)):
        raise ValueError('请选择当前完整选项明确列出的物品资料，不能借用其它选项或相似名称。')
    data=_validated_packet();result=_unknown('documented_named_item_details')
    result.update(scene_key=scene_key,choice_key=choice_key,item_id=item_id,item=None,reference=None,icon_reference=None)
    if data is None:return result
    result.update(status='documented_reference',source_valid=True,item=deepcopy(data['item']),
        reference=deepcopy(data['reference']),icon_reference=deepcopy(data['reference']['icon_reference']),
        sources=deepcopy(data['sources']),source_reference=deepcopy(data['source_reference']),
        notice=data['notice'],unlock_notice=data['unlock_notice'])
    return result

"""Exact one-hop future-scene cards; never eligibility, actual rewards or pools."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_023'
DATA='rouge/data/resting-corner-results.json'
MANIFEST='research/p3-resting-results-293/source-manifest.json'
MANIFEST_SHA256='3db8aee2815e898211bc902d0314e0d58e5e1fd5c585cd265fde280b4d2b5476'
_CHOICES=tuple(EVENT+f':scene:{scene}:choice:{choice}' for scene,choice in ((1,0),(6,0),(9,1),(11,0)))
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
            or data.get('event_id')!=EVENT or data.get('full_actual_pool_known') is not False
            or data.get('current_server_verified') is not False or data.get('actual_result') is not None):return False
    cards=data['cards'];scenes=data['scenes']
    if type(cards) is not list or len(cards)!=4 or type(scenes) is not dict:return False
    if tuple(card['choice_key'] for card in cards)!=_CHOICES:return False
    all_branch_ids=[]
    for card,count,listed in zip(cards,(3,2,2,2),(3,2,1,3)):
        if (card['reference_id']!=card['choice_key'] or card['event_id']!=EVENT
                or type(card['documented_count']) is not int or card['documented_count']!=count
                or type(card['listed_branch_count']) is not int or card['listed_branch_count']!=listed
                or card['count_matches'] is not (count==listed) or len(card['branches'])!=listed
                or card['full_actual_pool_known'] is not False or card['source_scene_link_verified'] is not False
                or any(card[key] is not None for key in ('actual_selected_branch','actual_reward','actual_selectable'))):return False
        for index,branch in enumerate(card['branches']):
            if (branch['branch_id']!=card['choice_key']+':sub:'+str(index)
                    or branch['target_scene_key'] not in scenes
                    or branch['actual_transition'] is not None or branch['actual_reward'] is not None
                    or type(branch['future_buttons']) is not list or len(branch['future_buttons'])!=1):return False
            all_branch_ids.append(branch['branch_id'])
            button=branch['future_buttons'][0]
            if (type(button['quantity_reference']) is not int or button['quantity_reference']<=0
                    or button['actual_granted'] is not None or button['item_pool'] is not None
                    or button['original_entry_relation_verified'] is not False):return False
    return len(all_branch_ids)==len(set(all_branch_ids))==9


def _validated_packet():
    """Hash every pinned public file on every call; only parsing may be reused."""
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
        raw_data=blobs[DATA];key=(MANIFEST_SHA256,hashlib.sha256(raw_data).hexdigest())
        if key not in _CACHE:
            data=json.loads(raw_data)
            if not _valid_schema(data):return None
            _CACHE.clear();_CACHE[key]=data
        data=_CACHE[key]
        # Read the current file bytes rather than a mutable/cached catalog object.
        current=json.loads(blobs['rouge/data/node-catalog.json'])
        event=next((row for row in current['events'] if row.get('id')==EVENT),None)
        if not _same_json(event,data['expected_event']):return None
        return data
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None


def source_data():
    """Independent defensive source snapshot; no public override/evaluator hook."""
    data=_validated_packet()
    return deepcopy(data) if data is not None else None


def _unknown(kind):
    return {'status':'unknown','reference_kind':kind,'event_id':EVENT,'source_valid':False,
        'sources':None,'notice':'这组后续资料暂时无法核对；保留原文，暂不提供旧的结果或场景入口。',
        'full_actual_pool_known':False,'current_server_verified':False,
        'actual_transition':None,'actual_selected_branch':None,'actual_reward':None,'actual_selectable':None}


def resting_result_cards(event_id):
    """Four precise reading references. Unrelated event IDs do not read sources."""
    if type(event_id) is not str or event_id!=EVENT:return None
    data=_validated_packet();result=_unknown('resting_corner_future_result_cards')
    result['cards']=[]
    if data is None:return result
    result.update(status='documented_reference',source_valid=True,cards=deepcopy(data['cards']),
        sources=deepcopy(data['sources']),notice=data['notice'])
    return result


def resting_result_scene(event_id,choice_key,branch_id):
    """Revalidate before reading one declared local scene; no guessed destination."""
    if type(event_id) is not str or event_id!=EVENT:return None
    if type(choice_key) is not str or choice_key not in _CHOICES:
        raise ValueError('请选择这组资料中明确列出的四条选择之一。')
    if type(branch_id) is not str:raise ValueError('后续资料引用需要完整文字标识。')
    data=_validated_packet();result=_unknown('resting_corner_future_scene_reading')
    result.update(choice_key=choice_key,branch_id=branch_id,scene=None)
    if data is None:return result
    card=next(card for card in data['cards'] if card['choice_key']==choice_key)
    branch=next((row for row in card['branches'] if row['branch_id']==branch_id),None)
    if branch is None:raise ValueError('这条后续不属于正在查阅的选择，不能借用其它选项。')
    scene=data['scenes'][branch['target_scene_key']]
    result.update(status='documented_reference',source_valid=True,scene=deepcopy(scene),
        branch_label=branch['label'],future_buttons=deepcopy(branch['future_buttons']),
        sources=deepcopy(data['sources']),notice='这里只打开该选择明确列出的社区场景原文；不表示实际进入、按钮可选或已经领取。')
    return result

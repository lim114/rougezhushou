"""Four fixed recruitment results, separate from eligibility and actual grants."""
from copy import deepcopy
from .choice_annotations import choice_document_payload, same_choice_json
import json
from pathlib import Path
from . import node_catalog as catalog

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_018'
SCENE=EVENT+':scene:0'
CHOICE=SCENE+':choice:1'
DATA='rouge/data/choice-recruitment-results.json'
MANIFEST = 'research/runtime-reference-loaders-20261031/recruitment/source-manifest.json'
MANIFEST_SHA256 = 'c50017cce26f0800a642b6a875a5a60213a4eb57ad5c0b74fd0453774b25b41a'
_CACHE={}


def _validated_packet():
    try:
        payload = choice_document_payload(ROOT, MANIFEST, MANIFEST_SHA256, DATA)
        if payload is None:return None
        if MANIFEST_SHA256 in _CACHE:
            return _CACHE[MANIFEST_SHA256]
        data = json.loads(payload)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if (data['schema_version']!=1 or data['event_id']!=EVENT or data['scene_key']!=SCENE
            or data['choice_key']!=CHOICE or len(data['variants'])!=4
            or data['original_entry_scene_verified'] is not False
            or data['full_recruitment_pool_known'] is not False
            or data['actual_result_variant'] is not None):return None
    _CACHE.clear()
    _CACHE[MANIFEST_SHA256] = data
    return data


def source_data():
    """Return a defensive copy only after fresh verification of all public files."""
    data=_validated_packet()
    return deepcopy(data) if data is not None else None


def choice_reference(event_id,choice,*,scene_key=None):
    """Return one exact result annotation; unrelated choices do not scan sources.

    The fixed full choice key locates its scene when ``scene_key`` is omitted.
    Only ``annotation_role == 'selection_result'`` permits the caller to replace
    its unparsed annotation warning. Unknown results retain that warning/text.
    """
    return _choice_reference(event_id, choice, scene_key)


def _choice_reference(event_id, choice, scene_key, *, prepared=None):
    if (type(event_id) is not str or event_id!=EVENT or type(choice) is not dict
            or type(choice.get('key')) is not str or choice['key']!=CHOICE
            or scene_key is not None and (type(scene_key) is not str or scene_key!=SCENE)):
        return None
    result={'status':'unknown','reference_kind':'documented_recruitment_result_variants',
        'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,'annotation_role':None,'annotation_text':None,
        'variants':[],'variants_are_alternatives':True,'hope_gain_reference':None,
        'recruit_count_reference':None,'rarity_ceiling_reference':None,'upgrade_reference_text':None,
        'source':None,'source_reference':None,'source_valid':False,'reason_codes':[],
        'original_entry_scene_verified':False,'source_scene_link_verified':False,
        'full_recruitment_pool_known':False,'current_server_verified':False,
        'actual_selectable':None,'actual_result_variant':None,'actual_recruited_operator':None,
        'actual_hope_gain':None,'actual_cultivation':None,'actual_granted':None,'recruitment_cost':None}
    data=_validated_packet()
    if data is None:
        result.update(notice='招募结果的补充来源未通过核对；保留原说明，职业结果与实际招募仍未知。',
                      reason_codes=['fixed_source_unverified'])
        return result
    result['source_valid']=True
    result['source']=deepcopy(data['source'])
    if prepared is None:
        try:
            event = catalog._event(event_id)
            scene = catalog._event_scene(event, SCENE)
        except catalog.NodeQueryError:
            event = scene = None
    else:
        event, scene = prepared
    if (not same_choice_json(data['expected_event'], event) or not same_choice_json(data['expected_scene'], scene)
            or not same_choice_json(data['expected_choice'], choice)):
        result.update(notice='招募结果资料与当前完整事件、场景或选项未能核对；保留原说明。',
                      reason_codes=['catalog_content_mismatch'])
        return result
    result.update(status='documented_reference',annotation_role='selection_result',
        annotation_text=data['annotation_text'],variants=deepcopy(data['variants']),
        hope_gain_reference=2,recruit_count_reference=1,rarity_ceiling_reference=5,upgrade_reference_text='直升',
        source_reference=deepcopy(data['source_reference']),
        notice='这是选择后的四种职业组合参考，不是出现门槛；每次参考为2希望、招募1名5星及以下直升干员，费用和实际结果仍未知。')
    return result

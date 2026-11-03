"""CACHE CANDIDATE: a documented one-way result, never actual run completion."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_019'
SCENE=EVENT+':scene:1'
CHOICE=SCENE+':choice:0'
DATA='rouge/data/peace-guardian-results.json'
MANIFEST = 'research/runtime-reference-loaders-20261031/peace-guardian/source-manifest.json'
MANIFEST_SHA256 = 'ce6bafd319577204481b485aaace6c8440d61b02c4f836242e0b36aa47df0239'
_CACHE={}


def _validated_packet():
    try:
        manifest_raw=(ROOT/MANIFEST).read_bytes()
        if hashlib.sha256(manifest_raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(manifest_raw)
        blobs={}
        for relative,expected in manifest['files'].items():
            path=ROOT/relative
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():return None
            raw=path.read_bytes()
            if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:return None
            blobs[relative]=raw
        payload=blobs[DATA]
        key=(MANIFEST_SHA256,hashlib.sha256(payload).hexdigest())
        if key not in _CACHE:
            data=json.loads(payload)
            if (data['schema_version']!=1 or data['event_id']!=EVENT or data['scene_key']!=SCENE
                    or data['choice_key']!=CHOICE or data['source_scene_link_verified'] is not False
                    or data['complete_movement_result_known'] is not False
                    or data['actual_current_floor_completion'] is not None
                    or data['actual_target_node_id'] is not None or data['actual_moved'] is not None):return None
            _CACHE.clear()
            _CACHE[key]=data
        return _CACHE[key]
    except (OSError,ValueError,KeyError,TypeError):return None


def source_data():
    data=_validated_packet()
    return deepcopy(data) if data is not None else None


def _same_json(value,expected):
    if type(value) is not type(expected):return False
    if type(expected) is dict:
        return (value.keys()==expected.keys() and all(type(k) is str for k in value)
                and all(_same_json(value[k],expected[k]) for k in expected))
    if type(expected) is list:
        return len(value)==len(expected) and all(_same_json(v,e) for v,e in zip(value,expected))
    return value==expected


def choice_result_reference(event,scene,choice):
    """Explain one MOVE choice; no evaluator, declarations, map or inverse rule.

    A valid annotation_role permits a consumer to classify just this exact text
    as a result reference. It does not set completion, choose a target or prove
    that the condition holds. Non-target input does not read source files.
    """
    if (type(event) is not dict or type(event.get('id')) is not str or event['id']!=EVENT
            or type(scene) is not dict or type(scene.get('key')) is not str or scene['key']!=SCENE
            or type(choice) is not dict or type(choice.get('key')) is not str or choice['key']!=CHOICE):
        return None
    result={'status':'unknown','reference_kind':'documented_current_floor_resident_movement_exception',
        'event_id':EVENT,'scene_key':SCENE,'choice_key':CHOICE,'annotation_role':None,
        'base_action_reference':None,'completion_exception_reference':None,'related_option_reference':None,
        'source':None,'source_reference':None,'source_valid':False,'reason_codes':[],
        'source_scene_link_verified':False,'complete_movement_result_known':False,
        'actual_current_floor_completion':None,'actual_target_node_id':None,'actual_moved':None,
        'actual_battle_triggered':None,'actual_position_after':None}
    data=_validated_packet()
    if data is None:
        result.update(reason_codes=['fixed_source_unverified'],
            notice='移动例外的补充来源未通过核对；保留原文，完成状态、目的地与实际移动仍未知。')
        return result
    result['source_valid']=True
    result['source']=deepcopy(data['source'])
    if (not _same_json(event,data['expected_event']) or not _same_json(scene,data['expected_scene'])
            or not _same_json(choice,data['expected_choice'])):
        result.update(reason_codes=['catalog_content_mismatch'],
            notice='移动结果资料与完整事件、场景或选项未能核对；保留原说明。')
        return result
    result.update(status='documented_reference',annotation_role='selection_result',
        base_action_reference=deepcopy(data['base_action_reference']),
        completion_exception_reference=deepcopy(data['completion_exception_reference']),
        related_option_reference=deepcopy(data['related_option_reference']),
        source_reference=deepcopy(data['source_reference']),
        notice='资料只说明：若已完成当前层据点作战，则此选项不会移动；本层完成状态未知，未完成不证明一定移动。')
    return result

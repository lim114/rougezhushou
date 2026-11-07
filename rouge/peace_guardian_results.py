"""CACHE CANDIDATE: a documented one-way result, never actual run completion."""
from copy import deepcopy
from .choice_annotations import choice_document_files, same_choice_json
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
        files = choice_document_files(ROOT, MANIFEST, MANIFEST_SHA256, (DATA,))
        if files is None:return None
        if MANIFEST_SHA256 in _CACHE:
            return _CACHE[MANIFEST_SHA256]
        data = json.loads(files[DATA])
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if (data['schema_version']!=1 or data['event_id']!=EVENT or data['scene_key']!=SCENE
            or data['choice_key']!=CHOICE or data['source_scene_link_verified'] is not False
            or data['complete_movement_result_known'] is not False
            or data['actual_current_floor_completion'] is not None
            or data['actual_target_node_id'] is not None or data['actual_moved'] is not None):return None
    _CACHE.clear()
    _CACHE[MANIFEST_SHA256] = data
    return data


def source_data():
    data=_validated_packet()
    return deepcopy(data) if data is not None else None


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
    if (not same_choice_json(data['expected_event'], event) or not same_choice_json(data['expected_scene'], scene)
            or not same_choice_json(data['expected_choice'], choice)):
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

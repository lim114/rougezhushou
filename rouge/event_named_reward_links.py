"""Strict supplemental document links; never a grant or source-scene script."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'community_group_007'
DATA = 'rouge/data/event-named-reward-links.json'
MANIFEST = 'research/p3-event-named-rewards-289/source-manifest.json'
MANIFEST_SHA256 = 'c1b6ac0ae75261ec5cc56d75334c951145b192259124d0878b97390d254ec8ee'
_CACHE = {}


def _validated_packet():
    """Check every byte on each applicable call; only unchanged JSON is reused."""
    try:
        manifest_raw = (ROOT/MANIFEST).read_bytes()
        if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(manifest_raw)
        blobs = {}
        for relative, expected in manifest['files'].items():
            path = ROOT/relative
            if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():
                return None
            raw = path.read_bytes()
            if len(raw) != expected['bytes'] or hashlib.sha256(raw).hexdigest() != expected['sha256']:
                return None
            blobs[relative] = raw
        payload = blobs[DATA]
        key = (MANIFEST_SHA256,hashlib.sha256(payload).hexdigest())
        if key not in _CACHE:
            data = json.loads(payload)
            if (data['schema_version'] != 1 or data['event_id'] != TARGET
                    or len(data['links']) != 2 or data['source_scene_link_verified'] is not False
                    or data['actual_reward'] is not None or data['full_reward_pool_known'] is not False):
                return None
            _CACHE.clear()
            _CACHE[key] = data
        return _CACHE[key]
    except (OSError,ValueError,KeyError,TypeError):
        return None


def source_data():
    """Return an isolated source packet after a fresh byte check."""
    data = _validated_packet()
    return deepcopy(data) if data is not None else None


def _same_json(value, expected):
    """JSON equality must not equate true/1, subclass objects or changed fields."""
    if type(value) is not type(expected):
        return False
    if type(expected) is dict:
        return (value.keys() == expected.keys() and all(type(key) is str for key in value)
                and all(_same_json(value[key],expected[key]) for key in expected))
    if type(expected) is list:
        return len(value) == len(expected) and all(_same_json(v,e) for v,e in zip(value,expected))
    return value == expected


def event_named_reward_links(event, existing_rewards):
    """Link exactly two known catalog choices to already existing reward records.

    ``existing_rewards`` is the existing ``event_rewards`` mapping. A complete
    document-content match does not fill catalog ``game_choice_ids``, establish
    source-scene reachability, select a choice, or change inventory/resources.
    """
    result = {'status':'not_applicable','links':{},'source':None,'source_valid':None,
              'notice':'此事件不适用该补充资料；现有奖励参考不受影响。','reason_codes':[]}
    if type(event) is not dict or type(event.get('id')) is not str or event['id'] != TARGET:
        return result
    data = _validated_packet()
    result['status'] = 'unknown'
    result['source_valid'] = data is not None
    if data is None:
        result.update(notice='具名奖励的补充来源未通过核对；奖励关联未知，原有资料仍保留。',
                      reason_codes=['fixed_source_unverified'])
        return result
    result['source'] = deepcopy(data['sources'])
    if not _same_json(event,data['expected_event']):
        result.update(notice='补充资料与当前事件内容未能核对；不按相似名称关联奖励。',
                      reason_codes=['catalog_event_content_mismatch'])
        return result
    if (type(existing_rewards) is not dict or any(
            cid not in existing_rewards or not _same_json(existing_rewards[cid],expected)
            for cid,expected in data['expected_existing_rewards'].items())):
        result.update(notice='补充资料与既有奖励记录未能核对；具名奖励关联未知。',
                      reason_codes=['existing_reward_content_mismatch'])
        return result
    for key, reference in data['links'].items():
        cid = reference['original_choice_id']
        result['links'][key] = {**deepcopy(reference),
            'reward_reference':deepcopy(existing_rewards[cid]),
            'reference_kind':'full_literal_document_corroboration',
            'content_link_verified':True,'source_scene_link_verified':False,
            'actual_claim_eligible':None,'actual_reward':None,
            'full_reward_pool_known':False,'probability':None}
    result.update(status='documented_reference',
                  notice='两条选项的完整资料与原有笼控器记录相符；数量、实际领取和原生入口关系仍未知。')
    return result

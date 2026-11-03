"""Read-only documented entry configuration, never run eligibility or floors.

Only the exact fixed ro6_t_12 identity is covered. Every call verifies source
bytes anew; parsed copies may be reused only after that verification succeeds.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath

STAGE_ID = 'ro6_t_12'
ROOT = Path(__file__).resolve().parents[1]
DATA = 'rouge/data/stage-entry-configuration-reference.json'
MANIFEST = 'research/p3-stage-entry-configuration-296/manifest.json'
DATA_SHA256 = 'd30165125724bad4d520bd84506666f7c4eba151080a4b231bda8721d8761bcf'
MANIFEST_SHA256 = '47b272989530c116163c59e683dca7cf77a6798f2eb1180b4d112ad350c01976'
_parsed_packet = None


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _source_path(relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative:
        raise ValueError('Invalid source path.')
    return ROOT.joinpath(*rel.parts)


def _verified_packet():
    global _parsed_packet
    try:
        raw_manifest = _source_path(MANIFEST).read_bytes()
        if _sha(raw_manifest) != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw_manifest)
        if manifest.get('schema') != 'stage_entry_configuration_source_manifest_v1':
            return None
        if manifest.get('data_file') != DATA or manifest.get('data_sha256') != DATA_SHA256:
            return None
        for relative, pin in manifest['files'].items():
            raw = _source_path(relative).read_bytes()
            if len(raw) != pin['bytes'] or _sha(raw) != pin['sha256']:
                return None
        raw_data = _source_path(DATA).read_bytes()
        if _sha(raw_data) != DATA_SHA256:
            return None
        if _parsed_packet is None:
            packet = json.loads(raw_data)
            if packet['schema'] != 'stage_entry_configuration_reference_v1' or packet['stage']['id'] != STAGE_ID:
                return None
            _parsed_packet = packet
        return deepcopy(_parsed_packet)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError):
        return None


def source_data():
    """Return a fresh-verified independent copy, or None when a source fails."""
    return _verified_packet()


def stage_entry_reference(stage_id):
    """List fixed documentary configuration only, with no current-state inputs.

    Other stage IDs, aliases, booleans and non-string values return immediately
    without reading source files. A failed target never returns cached content.
    """
    if type(stage_id) is not str or stage_id != STAGE_ID:
        return None
    packet = _verified_packet()
    if packet is None:
        return {'status': 'source_unavailable', 'reference_kind': 'documented_stage_entry_configuration',
                'stage_id': STAGE_ID, 'stage_name': '无效验尸', 'rows': [],
                'source': None, 'marker': None, 'not_hold_item': None, 'beacon_item': None,
                'community_reference': None, 'upstream_reference': None,
                'notice': '资料文件发生变化或无法读取，暂不显示这份进入条件说明，请先重新核对来源。',
                'actual_eligibility': None, 'actual_node': None, 'actual_entry': None,
                'actual_reward': None, 'actual_count': None, 'complete_stage_floor_pool': None,
                'current_inventory_used': False, 'floor_eligibility_evaluated': False}
    return {'status': 'documented_reference', 'reference_kind': packet['reference_kind'],
            'stage_id': STAGE_ID, 'stage_name': packet['stage']['name'],
            'stage': packet['stage'], 'rows': packet['rows'], 'source': packet['source'],
            'marker': packet['marker'], 'not_hold_item': packet['not_hold_item'],
            'beacon_item': packet['beacon_item'], 'community_reference': packet['community_reference'],
            'upstream_reference': packet['upstream_reference'], 'notice': packet['player_notice'],
            'unknowns': packet['unknowns'],
            'actual_eligibility': None, 'actual_node': None, 'actual_entry': None,
            'actual_reward': None, 'actual_count': None, 'complete_stage_floor_pool': None,
            'current_inventory_used': False, 'floor_eligibility_evaluated': False}

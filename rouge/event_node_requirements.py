"""Five explicit natural-main-floor restrictions, separate from actual entry.

No catalog import or mutation. Fresh file guards and cached object integrity
follow the independent source-reference pattern used by sections 295–297.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
DATA='rouge/data/event-node-requirements.json'
MANIFEST='research/p3-event-node-requirements-298/source-manifest.json'
DATA_SHA256='f11c6d83a048ffdea14cbccdd1506ff02c3ef35a1cf94f107e30845b2d1deab3'
MANIFEST_SHA256='38638685b5b5084cbd3e81ff1c288a6d89c97c67cdc34fa72299a7997aa621ed'
EVENT_RULES={
    'community_group_024':('先行一步',(1,5,6)),
    'community_group_025':('失与得',(1,6)),
    'community_group_027':('误入奇境',(1,2,6)),
    'community_group_028':('狭路相逢',(1,2,6)),
    'community_group_029':('狭路相逢',(1,2,6)),
    'community_group_037':('安全的角落',(1,))}
_parsed_packet=None


def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def _same_json(value,expected):
    if type(value) is not type(expected):return False
    if type(expected) is dict:
        return value.keys()==expected.keys() and all(type(k) is str and _same_json(value[k],expected[k]) for k in value)
    if type(expected) is list:return len(value)==len(expected) and all(_same_json(a,b) for a,b in zip(value,expected))
    return value==expected


def _source_path(relative):
    if type(relative) is not str:raise ValueError('Source path must be text.')
    path=PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative:raise ValueError('Invalid source path.')
    result=ROOT.joinpath(*path.parts)
    if not result.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Source escaped root.')
    return result


def _valid_schema(packet,current):
    if (type(packet) is not dict or packet.get('schema')!='event_node_requirements_v1'
        or packet.get('current_server_verified') is not False or packet.get('actual_server_eligible') is not None
        or packet.get('inventory_updated') is not False or packet.get('original_entry_restored') is not False
        or packet.get('probability') is not None or set(packet['expected_events'])!=set(EVENT_RULES)
        or set(packet['events'])!=set(EVENT_RULES)):return False
    for identity,(node_type,excluded) in EVENT_RULES.items():
        expected=packet['expected_events'][identity]
        actual=next((e for e in current['events'] if e.get('id')==identity),None)
        if not _same_json(expected,actual):return False
        row=packet['events'][identity]
        if (row['event_id']!=identity or row['node_type']!=node_type or expected['node_types']!=[node_type]
                or not _same_json(row['documented_excluded_main_floors'],list(excluded))):return False
        tech=row['technology_enabling_reference']
        if tech is not None and (tech['role']!='known_enabling_path_only'
                or tech['necessary_negative_gate_proven'] is not False
                or tech['inactive_hard_exclusion_supported'] is not False
                or tech['actual_account_active'] is not None):return False
    return True


def _verified_packet():
    global _parsed_packet
    try:
        raw_manifest=_source_path(MANIFEST).read_bytes()
        if _sha(raw_manifest)!=MANIFEST_SHA256:return None
        manifest=json.loads(raw_manifest)
        if (manifest.get('schema')!='event_node_requirements_source_manifest_v1'
            or manifest.get('data_file')!=DATA or manifest.get('data_sha256')!=DATA_SHA256
            or manifest.get('runtime_reads_primary_table') is not False):return None
        blobs={}
        for relative,pin in manifest['files'].items():
            raw=_source_path(relative).read_bytes()
            if type(pin['bytes']) is not int or len(raw)!=pin['bytes'] or _sha(raw)!=pin['sha256']:return None
            blobs[relative]=raw
        if _sha(blobs[DATA])!=DATA_SHA256:return None
        current=json.loads(blobs['rouge/data/node-catalog.json'])
        key=(DATA_SHA256,MANIFEST_SHA256)
        if _parsed_packet is None or _parsed_packet[0]!=key:
            packet=json.loads(blobs[DATA])
            if not _valid_schema(packet,current):return None
            _parsed_packet=(key,_sha(_canonical(packet)),packet)
        elif _sha(_canonical(_parsed_packet[2]))!=_parsed_packet[1]:return None
        if not _valid_schema(_parsed_packet[2],current):return None
        return deepcopy(_parsed_packet[2])
    except (OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,UnicodeError):return None


def source_data():
    """Complete freshly verified independent source copy, or None."""
    return _verified_packet()


def _context(floor,entry_mode,special_region,historical):
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):
        raise ValueError('主层必须为1–6的整数或未知，布尔值不是层数。')
    if type(entry_mode) is not str or entry_mode not in ('unknown','natural','content','processed_item','history'):
        raise ValueError('入口范围必须为unknown/natural/content/processed_item/history。')
    if type(special_region) is not bool or type(historical) is not bool:raise ValueError('特殊区域与历史标记必须为布尔值。')
    return {'floor':floor,'entry_mode':entry_mode,'special_region':special_region,'historical':historical}


def event_requirements(event_id,*,floor=None,entry_mode='unknown',special_region=False,historical=False):
    """Documented negative floor constraint; all actual entry remains unknown.

    Only natural, non-special, nonhistorical main-floor contexts are evaluated.
    Other contexts still receive source references without applying exclusions.
    An allowed floor is not an overall eligibility or occurrence guarantee.
    """
    if type(event_id) is not str or event_id not in EVENT_RULES:return None
    context=_context(floor,entry_mode,special_region,historical)
    applicable=entry_mode=='natural' and floor is not None and not special_region and not historical
    packet=_verified_packet()
    if packet is None:
        return {'status':'source_unavailable','source_valid':False,'event_id':event_id,'node_type':None,
            'reference_kind':'documented_natural_main_floor_requirements','source':None,'source_reference':None,
            'expected_event':None,'documented_excluded_main_floors':[],'documented_floor_match':None,
            'context':context,'context_applicable':applicable,'check':None,'technology_enabling_reference':None,
            'actual_server_eligible':None,'actual_node':None,'probability':None,'inventory_updated':False,
            'qualification_status_reference':'unknown',
            'notice':'节点主层资料暂时无法核对；不沿用旧禁区排除事件，保留原文和资格未知。'}
    reference=packet['events'][event_id]
    match=None if not applicable or floor is None else floor not in reference['documented_excluded_main_floors']
    check={'key':'documented_node_natural_main_floor','kind':'source_node_floor_requirement',
        'matches':match,'source_text':reference['source_text'],'context_applicable':applicable,
        'documented_excluded_main_floors':reference['documented_excluded_main_floors'],
        'source_revision':packet['source']['main']['revision'],'actual_server_eligible':None}
    return {'status':'documented_reference','source_valid':True,
        'reference_kind':'documented_natural_main_floor_requirements','event_id':event_id,
        'event_name':reference['event_name'],'node_type':reference['node_type'],
        'expected_event':packet['expected_events'][event_id],'source':packet['source'],
        'source_reference':reference,
        'documented_excluded_main_floors':reference['documented_excluded_main_floors'],
        'documented_floor_match':match,'context':context,'context_applicable':applicable,'check':check,
        'technology_enabling_reference':reference['technology_enabling_reference'],
        'qualification_status_reference':'excluded' if match is False else 'unknown',
        'actual_server_eligible':None,'actual_node':None,'probability':None,'inventory_updated':False,
        'current_server_verified':False,'original_entry_restored':False,'notice':packet['notice'],'limits':packet['limits']}

"""Manual exact-choice item references; never a grant, eligibility or run update."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
DATA='rouge/data/named-reward-items.json'
MANIFEST='research/p3-named-reward-items-301/source-manifest.json'
SELECTED_AUTHORITY='research/p3-named-reward-items-301/selected-authority-records.json'
DATA_SHA256='437684110f9e1190e1e7b681ef14f9d20ceb17e45e814a769244cca1a072353c'
MANIFEST_SHA256='a7501b82da0c9e3fa75809656f371f20a43c196eeef2cd37cfd388c16f185374'
EVENT_IDS=tuple('community_group_'+n for n in('005','006','007','008','010','011','019','020','022','025'))
CHOICE_KEYS={
 'community_group_005':tuple('community_group_005:scene:0:choice:'+str(i)for i in range(3)),
 'community_group_006':tuple('community_group_006:scene:0:choice:'+str(i)for i in range(2)),
 'community_group_007':tuple('community_group_007:scene:0:choice:'+str(i)for i in range(2)),
 'community_group_008':('community_group_008:scene:0:choice:0',),
 'community_group_010':('community_group_010:scene:17:choice:0',),
 'community_group_011':tuple('community_group_011:scene:0:choice:'+str(i)for i in range(3)),
 'community_group_019':('community_group_019:scene:0:choice:0',),
 'community_group_020':('community_group_020:scene:0:choice:0',),
 'community_group_022':('community_group_022:scene:0:choice:0',),
 'community_group_025':('community_group_025:scene:9:choice:0',)}
ACTUAL_FIELDS=('actual_reward','actual_quantity','actual_claimed','actual_held','actual_effect','actual_eligible')
_parsed_packet=None


def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')


def _same_json(value,expected):
    if type(value)is not type(expected):return False
    if type(expected)is dict:
        return value.keys()==expected.keys()and all(type(k)is str and _same_json(value[k],expected[k])for k in value)
    if type(expected)is list:return len(value)==len(expected)and all(_same_json(a,b)for a,b in zip(value,expected))
    return value==expected


def _source_path(relative):
    if type(relative)is not str:raise ValueError('Source path must be text.')
    path=PurePosixPath(relative)
    if path.is_absolute()or'..'in path.parts or'\\'in relative or':'in relative:raise ValueError('Invalid public source path.')
    result=ROOT.joinpath(*path.parts)
    if not result.resolve().is_relative_to(ROOT.resolve())or not result.is_file()or result.is_symlink():
        raise ValueError('Regular public source inside root required.')
    return result


def _valid_packet(packet,authority,current_catalog,current_rewards):
    if packet['schema']!='named_reward_items_v1'or authority['schema']!='named_reward_selected_authority_v1':return False
    if not all(_same_json(packet[k],authority[k])for k in('expected_events','expected_original_rewards','expected_reward_queries','icons','source')):return False
    if not _same_json(packet['items'],authority['complete_items'])or not _same_json(packet['relics'],authority['complete_relics']):return False
    if set(packet['expected_events'])!=set(EVENT_IDS)or len(packet['choices'])!=16 or len(packet['items'])!=13 or len(packet['relics'])!=12:return False
    if len(packet['expected_original_rewards'])!=17 or not _same_json(packet['expected_original_rewards'],current_rewards['event_rewards']):return False
    current_events={e['id']:e for e in current_catalog['events']if e['id']in EVENT_IDS}
    if not _same_json(packet['expected_events'],current_events):return False
    if packet['inventory_updated']is not False or packet['current_server_verified']is not False or packet['original_entry_restored']is not False:return False
    keys={(r['event_id'],r['scene_key'],r['choice_key'])for r in packet['choices']}
    expected={(event,key.rsplit(':choice:',1)[0],key)for event,choices in CHOICE_KEYS.items()for key in choices}
    if keys!=expected or len(keys)!=16:return False
    for row in packet['choices']:
        if row['reference_id']!=row['choice_key']or row['quantity_reference']is not None:return False
        if any(row[k]is not None for k in ACTUAL_FIELDS):return False
        item=packet['items'][row['item_id']]
        if row['item_kind']!=item['type']or row['item_kind']not in('RELIC','SCRAP'):return False
        if row['original_choice_id']=='choice_ro6_rest_4':return False
        if not _same_json(row['original_choice'],authority['complete_original_choices'][row['original_choice_id']]):return False
        event=packet['expected_events'][row['event_id']]
        scene=next(s for s in event['scenes']if s['key']==row['scene_key'])
        choice=next(c for c in scene['choices']if c['key']==row['choice_key'])
        if not _same_json(row['catalog_choice'],choice):return False
    return True


def _verified_packet(event_id):
    global _parsed_packet
    try:
        raw_manifest=_source_path(MANIFEST).read_bytes()
        if _sha(raw_manifest)!=MANIFEST_SHA256:return None
        manifest=json.loads(raw_manifest)
        if(manifest['schema']!='named_reward_items_source_manifest_v1'or manifest['data_file']!=DATA
            or manifest['data_sha256']!=DATA_SHA256 or manifest['selected_authority_file']!=SELECTED_AUTHORITY
            or manifest['runtime_reads_complete_primary_table']is not False
            or manifest['runtime_verifies_complete_build_original_bytes']is not False
            or manifest['all_package_runtime_members_required_for_each_target_query']is not True):return None
        selected={}
        for name,pin in manifest['runtime_files'].items():
            if not _same_json(pin,manifest['files'][name]):return None
            raw=_source_path(name).read_bytes()
            if type(pin['bytes'])is not int or len(raw)!=pin['bytes']or _sha(raw)!=pin['sha256']:return None
            if name in(DATA,SELECTED_AUTHORITY,'rouge/data/node-catalog.json','rouge/data/node-reward-reference.json'):selected[name]=raw
        if _sha(selected[DATA])!=DATA_SHA256:return None
        authority=json.loads(selected[SELECTED_AUTHORITY]);catalog=json.loads(selected['rouge/data/node-catalog.json'])
        reward_data=json.loads(selected['rouge/data/node-reward-reference.json'])
        key=(DATA_SHA256,MANIFEST_SHA256)
        if _parsed_packet is None or _parsed_packet[0]!=key:
            packet=json.loads(selected[DATA])
            if not _valid_packet(packet,authority,catalog,reward_data):return None
            _parsed_packet=(key,_sha(_canonical(packet)),packet)
        elif _sha(_canonical(_parsed_packet[2]))!=_parsed_packet[1]:return None
        packet=_parsed_packet[2]
        if not _valid_packet(packet,authority,catalog,reward_data):return None
        from . import node_catalog,node_rewards
        if not _same_json(node_catalog._event(event_id),packet['expected_events'][event_id]):return None
        if not _same_json(node_rewards._reference()['event_rewards'],packet['expected_original_rewards']):return None
        if not _same_json(node_catalog.event_reward_options(event_id),packet['expected_reward_queries'][event_id]):return None
        return deepcopy(packet)
    except(OSError,ValueError,TypeError,KeyError,AttributeError,IndexError,UnicodeError,StopIteration,RecursionError):return None


def _common(event_id):
    return{'event_id':event_id,**{k:None for k in ACTUAL_FIELDS},'inventory_updated':False}


def _reference_source(packet,event_id):
    return{'expected_event':packet['expected_events'][event_id],
        'expected_reward_query':packet['expected_reward_queries'][event_id],
        'original_typed_count':17,'full_reward_pool_known':False,'actual_server_verified':False}


def event_reference(event_id):
    """Exact current catalog choice references; no title or first-record fallback."""
    if type(event_id)is not str or event_id not in EVENT_IDS:return None
    packet=_verified_packet(event_id)
    if packet is None:
        return{**_common(event_id),'target':True,'status':'source_unavailable','source_valid':False,
            'event_title':None,'scope_key':None,'choices':[],'source':None,'source_reference':None,
            'notice':'物品资料或图标暂时无法核对，已清除旧资料；本局领取与生效仍未知。','unknowns':['本局资格、数量、领取、持有与生效']}
    return{**_common(event_id),'target':True,'status':'documented_reference','source_valid':True,
        'event_title':packet['expected_events'][event_id]['title'],
        'scope_key':event_id+':'+DATA_SHA256+':'+MANIFEST_SHA256,
        'choices':[r for r in packet['choices']if r['event_id']==event_id],
        'source':packet['source'],'source_reference':_reference_source(packet,event_id),
        'notice':packet['notice'],'unknowns':packet['unknowns']}


def item_details(event_id,scene_key,choice_key):
    """Manual exact unique tuple details; selecting it does not select a game choice."""
    if(type(event_id)is not str or event_id not in CHOICE_KEYS or type(scene_key)is not str or type(choice_key)is not str
        or choice_key not in CHOICE_KEYS[event_id]or scene_key!=choice_key.rsplit(':choice:',1)[0]):return None
    packet=_verified_packet(event_id)
    if packet is None:
        return{**_common(event_id),'status':'source_unavailable','source_valid':False,'reference':None,
            'item':None,'relic':None,'icon_reference':None,'unlock_notice':None,'source':None,'source_reference':None,
            'notice':'物品资料或图标暂时无法核对，已清除旧资料。'}
    matches=[r for r in packet['choices']if(r['event_id'],r['scene_key'],r['choice_key'])==(event_id,scene_key,choice_key)]
    if len(matches)!=1:return None
    row=matches[0];item_id=row['item_id']
    return{**_common(event_id),'status':'documented_reference','source_valid':True,'reference':row,
        'item':packet['items'][item_id],'relic':packet['relics'].get(item_id),
        'icon_reference':packet['icons'][item_id],'unlock_notice':packet['unlock_notice'],
        'source':packet['source'],'source_reference':_reference_source(packet,event_id),'notice':packet['notice']}

"""Local map reference queries; historical frequencies are never conditional odds."""
from functools import lru_cache
from pathlib import Path
import json
from . import public_node_statistics as statistics

@lru_cache(maxsize=1)
def public_counts():return statistics.load()

@lru_cache(maxsize=1)
def default_frequencies():
    try:return statistics.FrequencyIndex(public_counts())
    except(ValueError,KeyError,TypeError,OSError):return statistics.FrequencyIndex()

def historical_rows(zone_id,distance,frequencies=None):
    floor={'zone_1':'0','zone_2':'1','zone_3':'2','zone_4':'3','zone_5':'4'}.get(zone_id)
    if floor is None or type(distance)is not int or distance<0:return ()
    try:return tuple((default_frequencies()if frequencies is None else frequencies).rows(floor,distance))
    except(ValueError,KeyError,TypeError,OSError):return ()

def candidate_types(node):
    observed=node.get('observed_type')
    if observed and not observed.startswith(('未知','类型未确认')):return (observed,)
    if node.get('template_type'):return (node['template_type'],)
    return tuple(dict.fromkeys((node.get('prediction')or{}).get('candidates')or()))

def type_match(node,kind):
    observed=node.get('observed_type')
    if observed and not observed.startswith(('未知','类型未确认')):
        if observed==kind:return 'observed'
        return 'history'if observed=='林间空地'and node.get('remembered_type')==kind else 'excluded'
    if node.get('template_type'):return 'template'if node['template_type']==kind else'excluded'
    candidates=candidate_types(node)
    if candidates:return 'candidate'if kind in candidates else'excluded'
    return 'unconfirmed'

def historical_frequency(graph,node,kind,frequencies=None):
    return next((dict(r)for r in historical_rows(graph.get('zone_id'),node.get('distance'),frequencies)if r['name']==kind),None)

def overlay_rows(graph,kind,frequencies=None):
    result={}
    for node in(graph or{}).get('nodes',[]):
        match=type_match(node,kind)
        # Do not put an uncertain historical rate on revealed, passed or fixed nodes.
        frequency=historical_frequency(graph,node,kind,frequencies)if match=='candidate'else None
        result[node['id']]={'match':match,'frequency':frequency}
    return result

@lru_cache(maxsize=1)
def event_art_manifest():
    return json.loads((Path(__file__).with_name('data')/'map-event-art/sources.json').read_text('utf8'))

def event_picture(event_id):
    from .node_catalog import _event
    try:event=_event(event_id)
    except(ValueError,TypeError):return None
    ids={value.split(':')[-1]for scene in event['scenes']for value in scene['game_scene_ids']}
    manifest=event_art_manifest();keys=set()
    for prefix,key in manifest['event_images'].items():
        prefix=prefix.split(':')[-1]
        if any(identity==prefix or identity.startswith(prefix+'_')for identity in ids):keys.add(key)
    if len(keys)!=1:return None
    key=keys.pop();source=manifest['sources'].get(key)
    if not source:return None
    path=Path(__file__).resolve().parents[1]/source['file']
    return path if path.is_file()else None

def node_dossier(graph,node_id,config):
    from . import node_catalog
    from .node_catalog_view import map_conditions
    from .player_map import dossier_graph
    node=next((n for n in(graph or{}).get('nodes',[])if n['id']==node_id),None)
    if node is None:return None
    if not candidate_types(node):
        history=node_catalog.node_history(graph,node_id)
        if not any(history.values()):return None
        return {'rows':[],'battle_rows':[],'function_rows':[],**history}
    return node_catalog.node_dossier(dossier_graph(graph),node_id,**map_conditions(graph,config))

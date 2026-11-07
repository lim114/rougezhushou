"""Use explicit held counters only where the pinned layer rune fixes the meaning."""
from copy import deepcopy
from functools import lru_cache
import math

from .relics import mechanics
from .record_flags import active_record

# Each own-item layer is the same value consumed by its existing numerical
# rule. These bindings do not identify a random recipient, count battles, or
# reconstruct an acquisition/loss history.
COUNTER_BINDINGS = {
    'rogue_6_relic_legacy_103': ('altar_stacks','layer_after_battle_data',10),
    'rogue_6_relic_legacy_136': ('mercenary_stacks','layer_after_perfect_battle',10),
    'rogue_6_relic_cargo_11': ('fire_rod_stacks','layer_pass_stage',99),
    'rogue_6_relic_fight_30': ('probe_stacks','layer_zone_end_battle',99),
    'rogue_6_relic_artifact_7': ('grudge_stacks','layer_after_battle_data',999),
}
HUD_RESOURCE_LABELS = {'life':'目标生命','shield':'护盾','command':'指挥等级',
    'hope':'希望','action':'行动力','valuation':'总估价'}
RESOURCE_CAPACITY_LABELS = {'life':'上限','hope':'上限','parts_count':'容量'}
RESOURCE_LABELS = {**HUD_RESOURCE_LABELS,'gold':'源石锭','parts_count':'零件数',
    'altar_stacks':'圆石祭坛层数','mercenary_stacks':'佣兵饰物层数',
    'fire_rod_stacks':'厄运火杆层数','probe_stacks':'探测先锋层数',
    'grudge_stacks':'仇名录层数'}


@lru_cache(maxsize=1)
def _verified_bindings():
    result={}
    relics=mechanics()['relics']
    for rid,(condition,rune,maximum) in COUNTER_BINDINGS.items():
        item=relics[rid]
        layers=[b for b in item['raw_buffs'] if b['key']==rune]
        if len(layers)!=1:continue
        board={b['key']:b['valueStr'] if b.get('valueStr') is not None else b['value']
               for b in layers[0]['blackboard']}
        if board.get('max')!=maximum:continue
        if rune=='layer_after_battle_data' and board.get('src')!=rid:continue
        if not any(e.get('condition')==condition and e.get('maximum')==maximum
                   for e in item['effects']):continue
        result[rid]={'condition':condition,'maximum':maximum,'name':item['name'],
                     'rune':rune,'mechanism_source':item['source']}
    return result


def _counter_record(rid, proof, binding):
    value=proof.get('value')
    if (type(value) is not int or not 0<=value<=binding['maximum']
            or proof.get('title')!=binding['name']
            or not proof.get('source','').startswith('held_full_name_usage_and_')):
        return None
    return {'value':value,'relic_id':rid,'source':'held_card_counter','counter_evidence':proof,
            'counter_rune':binding['rune'],'mechanism_source':binding['mechanism_source']}


def counter_resources(counters):
    """Map a unique complete held-card proof; missing/contradicting reads give none."""
    unique={}
    for proof in counters:
        rid=proof.get('id')
        unique[rid]=None if rid in unique else proof
    result={}
    for rid,proof in unique.items():
        binding=_verified_bindings().get(rid)
        if proof is not None and binding:
            record=_counter_record(rid,proof,binding)
            if record is not None:
                record['counter_evidence']=deepcopy(proof)
                result[binding['condition']]=record
    return result


def valid_counter_resource(key,record):
    """Keep persistence restricted to the same validated source contract."""
    if not isinstance(record,dict) or record.get('source')!='held_card_counter':return False
    proof=record.get('counter_evidence')
    if not isinstance(proof,dict):return False
    rid=proof.get('id')
    if not isinstance(rid,str) or not isinstance(proof.get('source',''),str):return False
    binding=_verified_bindings().get(rid)
    return bool(binding and binding['condition']==key and _counter_record(rid,proof,binding)==record)


def _valid_time(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


def reusable_resources(state):
    """Return last-confirmed resources valid for this possession, without edits.

    A missing frame is not a loss. A confirmed loss, however, ends the scope
    of its old held-card evidence. The actual reacquisition/reset mechanism is
    unproved, so neither zero nor the previous count is a safe replacement.
    Deriving this view from existing history also protects pre-0.64 save files.
    """
    losses={};qualification_cutoffs={}
    for event in state.get('history',[]):
        kind=event.get('kind')
        if kind in ('relic_no_longer_held','relic_variant_corrected'):
            rid=event.get('id' if kind=='relic_no_longer_held' else 'previous_id')
            if not rid:continue
            cutoffs=losses
        elif (kind=='state_flag_reconfirmed' and event.get('record_kind')=='relic'
                and event.get('field')=='held' and type(event.get('value')) is bool
                and isinstance(event.get('id'),str)):
            rid=event['id']
            cutoffs=qualification_cutoffs
        else:continue
        at=event.get('at')
        if _valid_time(at):
            cutoffs[rid]=max(cutoffs.get(rid,float('-inf')),at)
    result={}
    for key,record in state.get('resources',{}).items():
        if key in ('gold','parts_count'):
            result[key]=deepcopy(record);continue
        if not isinstance(record,dict):continue
        source={k:v for k,v in record.items() if k!='captured_at'}
        if not valid_counter_resource(key,source):continue
        rid=record['relic_id'];at=record.get('captured_at')
        if (not _valid_time(at)
                or at<state['started_at'] or at>(state.get('last_read') or at)
                or rid not in state.get('relics',{})
                or not active_record(state['relics'][rid],'held')
                or losses.get(rid,float('-inf'))>=at
                or qualification_cutoffs.get(rid,float('-inf'))>at):continue
        result[key]=deepcopy(record)
    return result

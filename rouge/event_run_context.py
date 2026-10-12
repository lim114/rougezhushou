"""Read-only last-confirmed event conditions; presence is never a quantity.

Do not infer encountered/entered/visited events from preview titles, or create
pre-entry possession snapshots from the current run's retained inventory.
"""
from copy import deepcopy
import math
from .catalog import catalog, tactical_tools


def _time(value):
    return type(value) in (int,float) and math.isfinite(value)


def observed_event_context(run):
    state=run.state
    resources=run.calculation_resources()
    gold=(resources.get('gold') or {}).get('value')
    result={'item_presence':{},'inventory_complete':False,
            'condition_sources':{},'reference_context_scope':'same_run_last_confirmed_read_only'}
    if type(gold) is int and gold>=0:
        result['gold']=gold
        result['condition_sources']['gold']={'scope':'last_confirmed_resource',
            'captured_at':(resources.get('gold') or {}).get('captured_at')}
    start=state.get('started_at');last=state.get('last_read')
    if not _time(start) or not _time(last) or last<start:return result
    allowed=set(catalog()['relics'])|set(tactical_tools())
    sources={};conflicts=set();unqualified=False
    for group in ('relics','tactical_tools'):
        records=state.get(group,{})
        if not isinstance(records,dict):unqualified=True;continue
        for identity,record in records.items():
            if identity not in allowed or not isinstance(record,dict):unqualified=True;continue
            held=record.get('held');at=record.get('captured_at');source=record.get('source')
            if (type(held) is not bool or not _time(at) or not start<=at<=last
                    or not isinstance(source,str) or not source.strip()):unqualified=True;continue
            if identity in result['item_presence'] and result['item_presence'][identity] is not held:
                conflicts.add(identity);continue
            result['item_presence'][identity]=held
            sources[identity]={'scope':'last_confirmed_held_flag','captured_at':at,'source':source}
    for identity in conflicts:result['item_presence'].pop(identity,None);sources.pop(identity,None)
    status=run.inventory_status()
    expected=status.get('recognized',0)+status.get('recognized_tools',0)
    result['inventory_complete']=bool(status.get('complete') is True and not conflicts and not unqualified
        and sum(v is True for v in result['item_presence'].values())==expected)
    result['condition_sources']['item_presence']=sources
    result['condition_sources']['inventory_complete']={
        'scope':'last_confirmed_inventory_status','confirmed_at':status.get('confirmed_at')}
    return deepcopy(result)

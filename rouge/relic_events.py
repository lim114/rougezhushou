"""Apply supported effects to ordered damage events, never to aggregate DPS."""
DAMAGE={'physical','magic','true','elemental','weakness'}

def ammunition_rounds(maximum,cost,scenario,*,minimum_interval=None):
    """Supported count reference; a periodic refill cannot revive empty ammo."""
    import math
    if (isinstance(maximum,bool) or not isinstance(maximum,(int,float)) or
            not math.isfinite(maximum) or not float(maximum).is_integer() or not 0<maximum<=10000):
        raise ValueError('弹药最大值需要为已核验范围内的正整数。')
    if isinstance(cost,bool) or not isinstance(cost,int) or cost<=0:
        raise ValueError('单次耗弹需要为正整数。')
    maximum=int(maximum)
    rules=[r for r in scenario.get('_relic_rules',[]) if r['kind']=='ammo_refill']
    from .ammo_reference import refill_before_empty_is_safe
    from .ammo_counter import AmmoCounter,poll_book,consumption_for
    from itertools import permutations
    eligible=[]
    for rule in rules:
        params=rule['ammo_parameters']
        if params['maximum']!=maximum or params['attack_cost_reference']!=cost:
            raise ValueError('补弹最大值/耗弹路径与已准备资料不一致。')
        if not refill_before_empty_is_safe(params,cost,minimum_interval):
            rule['ammo_polling_pending']=True
        else:eligible.append(rule)
    if len(eligible)>2 or len({r['relic_id'] for r in eligible})!=len(eligible):
        raise ValueError('当前只核验两本不同补弹书的单counter组合。')
    cases=[]
    # Actual acquisition-to-insertion order is not established. Enumerate every
    # legal order, and only expose an exact count when all outcomes agree.
    for order in permutations(eligible):
        counter=AmmoCounter(maximum);rounds=0;used=set();events=[]
        consumption=consumption_for(counter,scenario,cost)
        while counter.remaining>0:
            rounds+=1
            if consumption is None:counter.consume(cost)
            elif consumption.ordinary_cast()!=cost:
                raise ValueError('普通施法耗弹与已准备资料不一致。')
            for rule in order:
                event=poll_book(counter,rule['ammo_parameters'],rule['relic_id'] in used)
                if event is not None:
                    used.add(rule['relic_id'])
                    events.append({'relic_id':rule['relic_id'],'after_attack':rounds,**event})
            if rounds>maximum*(len(eligible)+1)+1:raise ValueError('弹药情景过长。')
        cases.append({'order':[r['relic_id'] for r in order],
            'attack_count':rounds,'recovered_total':counter.recovered,'events':events})
    counts=sorted({case['attack_count'] for case in cases})
    if eligible:
        scenario['_ammo_refill_reference']={'counter_count':1,'recovery_limit':maximum,
            'order_verified':False,'all_legal_orders_checked':True,
            'count_order_invariant':len(counts)==1,'attack_count_bounds':[counts[0],counts[-1]],
            'cases':cases,'event_times_verified':False,'live_state_read':False}
    if len(counts)>1:
        for rule in eligible:rule['ammo_order_pending']=True
    return counts[0]

def first_damage(components,scenario,*,normal=False):
    rules=[r for r in scenario.get('_relic_rules',[]) if r['kind']=='first_damage_scale']
    if not rules or all(r['value']==1 for r in rules):return 0
    if len(rules)!=1:raise ValueError('同一来源首伤倍率组合尚未核验。')
    if normal and scenario.get('_first_damage_consumed_in_skill'):return 0
    events=[]
    for index,c in enumerate(components):
        if c.get('damage_type') not in DAMAGE or c.get('source_unit','operator')!='operator':continue
        times=c.get('times_seconds')
        if times is None:
            # A true instantaneous single event can be placed at skill activation;
            # unscheduled counters or expected fractional hits cannot be ordered.
            if c.get('instant_event') and c.get('hits')==1:times=[0]
            elif c.get('total',0)>0:return None
            else:continue
        amounts=c.get('event_amounts') or [c.get('per_hit',c['total']/len(times) if times else 0)]*len(times)
        if len(amounts)!=len(times):return None
        for hit,(time,amount) in enumerate(zip(times,amounts)):
            if amount>0:events.append((time,index,hit,amount,amounts))
    if not events:return 0
    first_time=min(event[0] for event in events)
    first_events=[event for event in events if abs(event[0]-first_time)<1e-9]
    # The list order is presentation order, not proof of the game's callback
    # order. Different damage sources on the same frame remain unresolved.
    if len({event[1] for event in first_events})>1:return None
    _,index,hit,amount,amounts=min(first_events,key=lambda e:e[2])
    c=components[index];amounts=list(amounts);extra=amount*(rules[0]['value']-1);amounts[hit]+=extra
    c['event_amounts']=amounts;c['total']+=extra
    c['per_hit']=c['total']/c['hits'] if c.get('hits') else c['total']
    c['first_damage_relic']=rules[0]['relic_id']
    return extra

"""SP from explicitly classified callbacks, for one offline scenario.

Initial times start at deployment. Cycle times start at skill activation, so
events inside the skill or its extra lockout can be discarded, never banked.
These inputs describe callbacks; they do not infer damage from an attack,
shield loss, a probability, an enemy's attack interval, or an on-screen pose.
"""
import math
from .timing import AttackTimeline, FPS, cadence, finite, frame_time

EVENT_TYPES = {'attack': '受到攻击', 'damage': '受到伤害', 'elemental_loss': '受到元素损伤',
               'dealt_damage': '本体成功造成伤害', 'kill': '本体击倒敌人'}
SP_RULE_KINDS = {'received_sp', 'event_sp'}
INCOMING_TYPES = {'attack', 'damage', 'elemental_loss'}


def has_received_sp(scenario):
    return any(r['kind'] == 'received_sp' and not r.get('token_only')
               for r in scenario.get('_relic_rules', []))


def has_event_sp(scenario):
    return any(r['kind'] in SP_RULE_KINDS and not r.get('token_only')
               for r in scenario.get('_relic_rules', []))


def event_phases(scenario):
    timing = scenario.get('timing', {})
    if not isinstance(timing, dict):
        raise ValueError('时序情景需要是对象。')
    if 'sp_events' not in timing:
        return {}
    phases = timing['sp_events']
    if not isinstance(phases, dict) or set(phases) - {'initial', 'cycle'}:
        raise ValueError('sp_events需要包含initial/cycle事件表的对象。')
    parsed = {}
    for phase, events in phases.items():
        if not isinstance(events, list) or len(events) > 1000:
            raise ValueError('sp_events.' + phase + '需要最多1000个事件；空列表表示已确认没有事件。')
        values = []
        for event in events:
            if not isinstance(event, dict) or set(event) != {'at_seconds', 'type'}:
                raise ValueError('技力事件需要且仅包含at_seconds和type。')
            kind = event['type']
            if not isinstance(kind, str) or kind not in EVENT_TYPES:
                raise ValueError('技力事件type需要为'+ '、'.join(EVENT_TYPES)+'。')
            if not isinstance(event['at_seconds'], (int, float)):
                raise ValueError('技力事件秒数需要JSON数值。')
            time = finite(event['at_seconds'], '技力事件秒数', 3600)
            values.append((time, kind))
        # Equal timestamps may be separate hits. Keep multiplicity, not a set.
        parsed[phase] = sorted(values)
    return parsed


def charge(scenario, skill, required, rate, interval, speed, *, initial=False,
           offset=0, resume=0, stun=0, wait_next_attack=False, attack_sp=0, attribute_speed=None):
    """Return elapsed seconds after deployment/skill end and a bounded receipt.

    Native attack recovery and explicit incoming-attack recovery share the
    timeline with explicit incoming/outgoing SP modifiers. Natural SP accrues only outside the
    block. Discrete credits become usable on the next reference logic tick.
    Wine phases keep the existing public calculator's marginal envelope.
    """
    from .relics import recharge_requirement
    phase = 'initial' if initial else 'cycle'
    phases = event_phases(scenario)
    mode = scenario.get('timing_mode', 'frames')
    framed = mode == 'frames'
    tick = 1 / FPS if framed else 0
    align = (lambda t: frame_time(t) / FPS) if framed else (lambda t: t)
    origin = align(offset)
    blocked = 0 if initial else align(finite(
        scenario.get('timing', {}).get('sp_lockout_extra_seconds', 0), '额外阻回秒数', 3600))
    required = max(0, required if initial else recharge_requirement(scenario, required))
    reference = {'phase': phase, 'status': 'known', 'events_supplied': len(phases[phase]) if phase in phases else None,
                 'ignored_blocked': 0, 'credited_received_events': 0, 'credited_received_sp': 0,
                 'credited_callback_events': 0, 'credited_callback_sp': 0, 'credited_by_type': {},
                 'origin_seconds': origin, 'blocked_seconds': blocked, 'seconds': None}
    if required > 0 and phase not in phases:
        reference['status'] = 'missing'
        return reference
    if phase not in phases:
        reference['status'] = 'not_needed'
    sp_type = skill['sp_type']
    if sp_type == 'INCREASE_WHEN_TAKEN_DAMAGE' and finite(
            scenario.get('incoming_attack_interval', 0), '受击间隔', 3600) > 0:
        raise ValueError('当前技力使用分类事件表，请将incoming_attack_interval留为0，避免重复计入同一攻击。')
    rate = max(0, rate) if sp_type == 'INCREASE_WITH_TIME' else 0
    native_attack = skill['sp_increment'] if sp_type == 'INCREASE_WHEN_ATTACK' else attack_sp
    native_attack += sum(r['value'] for r in scenario.get('_relic_rules', []) if r['kind'] == 'attack_sp')
    received = {kind: sum(r['value'] for r in scenario.get('_relic_rules', [])
                         if r['kind'] in SP_RULE_KINDS and not r.get('token_only') and r['event_type'] == kind)
                for kind in EVENT_TYPES}
    native_incoming = skill['sp_increment'] if sp_type == 'INCREASE_WHEN_TAKEN_DAMAGE' else 0
    events = []
    for time, kind in phases.get(phase, []):
        time = align(time) - origin
        if time < blocked - 1e-9:
            reference['ignored_blocked'] += 1
            continue
        value = received[kind] + (native_incoming if kind == 'attack' else 0)
        if value:
            events.append((time + tick, value, kind, received[kind]))
    horizon = max(0, 3600 - origin)
    if rate > 0:
        horizon = min(horizon, align(min(3600, blocked + required / rate)) + tick)
    wines = [r for r in scenario.get('_relic_rules', []) if r['kind'] == 'periodic_sp']
    if wines and required > 0:
        from .timing import wine_events
        wine_horizon=blocked+min(w['interval']*(math.ceil(required/w['value'])+1)+2/FPS for w in wines)
        horizon=min(horizon,wine_horizon)
        events.extend((blocked+f/FPS,value,'wine',0) for f,value in
            wine_events(scenario,frame_time(max(0,horizon-blocked)),origin+blocked,initial))
    elif rate <= 0 and native_attack <= 0:
        horizon = min(horizon, max((event[0] for event in events), default=blocked))
    config = dict(scenario.get('timing', {}))
    if initial:
        for key in ('target_windows', 'movement_windows', 'interrupt_windows'):
            config.pop(key, None)
            if 'initial_' + key in config:
                config[key] = config['initial_' + key]
        config.pop('target_disappears_seconds', None)
        config.pop('post_skill_lock_frames', None)
    elif stun:
        config['interrupt_windows'] = [*config.get('interrupt_windows', []), [origin, origin + stun]]
    config['_resume_frames'] = resume
    config['_deployment_initial'] = initial
    timeline = AttackTimeline({**scenario, 'timing': config}, normal=True, offset=origin)
    stream = None
    attacks = scenario.get('continuous_attacks', True)
    if (native_attack > 0 and attacks) or wait_next_attack:
        step = cadence(interval) / FPS if framed else interval
        limit = math.ceil(required / native_attack) + 2 if native_attack > 0 else math.ceil(horizon / step) + 2
        stream = timeline.attacks(max(0, 3600 - origin) if wait_next_attack else horizon, interval, speed, attribute_speed=attribute_speed, limit=limit)
        if attacks and native_attack > 0:
            times = [f / FPS for f in stream['release_frames']] if framed else [t + stun for t in stream['times_seconds']]
            events.extend((time + tick, native_attack, 'outgoing_attack', 0)
                          for time in times if time >= blocked - 1e-9)
    ready = blocked if required <= 0 else None
    charge_value = 0
    last = blocked
    for time, value, kind, received_value in sorted(events):
        if ready is not None:
            break
        if time > max(0, 3600 - origin):
            break
        natural_time = last + max(0, required - charge_value) / rate if rate > 0 else math.inf
        natural_ready = align(natural_time) if natural_time <= 3600 else math.inf
        if natural_ready <= time + 1e-9:
            ready = natural_ready
            break
        charge_value += rate * max(0, time - last)
        last = time
        room = max(0, required - charge_value)
        if received_value:
            credited = min(room, received_value)
            reference['credited_callback_events'] += 1
            reference['credited_callback_sp'] += credited
            entry = reference['credited_by_type'].setdefault(kind, {'events': 0, 'sp': 0})
            entry['events'] += 1
            entry['sp'] += credited
            if kind in INCOMING_TYPES:
                reference['credited_received_events'] += 1
                reference['credited_received_sp'] += credited
        charge_value += value
        if charge_value >= required - 1e-9:
            ready = time
    if ready is None and rate > 0:
        remaining = last + max(0, required - charge_value) / rate
        ready = align(remaining) if remaining <= 3600 else None
    if ready is not None and ready > max(0, 3600 - origin):
        ready = None
    if ready is not None and wait_next_attack:
        # A next-attack skill requires another legal attack slot after SP credit.
        starts = [f / FPS for f in stream['start_frames']] if framed else [
            max(0, t - interval) for t in stream['times_seconds']]
        ready = next((t for t in starts if t >= ready - 1e-9), None) if attacks else None
    if ready is not None and not initial and framed:
        ready = max(ready, math.ceil(finite(config.get('post_skill_lock_frames', 0), '技能结束硬直帧')) / FPS)
    if ready is not None and ready > max(0, 3600 - origin):
        ready = None
    reference['seconds'] = ready
    return reference

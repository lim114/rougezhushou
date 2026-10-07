"""Preserve known source subtotals without publishing unplaced damage as actual."""
from .timing import phase_totals


def mask_pending_damage(result, full, shown, normal, duration, cycle):
    def pending(plan):
        return bool(plan and any(c['damage_type'] not in ('healing','regeneration','buildup') and 'actual_total' in c and c['actual_total'] is None
                                for c in plan['components']))

    def known(plan, boundary=None):
        components = [c for c in plan['components'] if 'actual_total' not in c]
        if boundary is not None:
            return phase_totals(components, boundary)[0]
        return sum(c['total'] for c in components
                   if c['damage_type'] not in ('healing', 'regeneration', 'buildup'))

    if not any(pending(plan) for plan in (full, shown, normal)):
        return
    skill = result['estimate']['skill']
    subtotal = {
        'total_damage': known(full) if skill['mode'] not in ('infinite','switch','passive','triggered_ammo') else None,
        'phase_damage': known(full, duration) if duration is not None else None,
        'window_damage': known(shown),
        'cycle_damage': (known(full, cycle) + (known(normal) if normal else 0))
                        if cycle is not None else None,
    }
    subtotal['cycle_dps'] = subtotal['cycle_damage'] / cycle if cycle else None
    subtotal['window_dps'] = subtotal['window_damage'] / shown['duration'] if shown['duration'] else None
    result['known_damage_subtotals'] = subtotal
    if pending(full):
        skill['total_damage'] = skill['phase_damage'] = None
    if cycle is not None and (pending(full) or pending(normal)):
        skill['cycle_damage'] = skill['cycle_dps'] = None
    if pending(shown):
        result['total_damage'] = None
        skill['window_damage'] = skill['window_dps'] = None
    for c in full['components']:
        if 'actual_total' in c and c['actual_total'] is None:
            skill['hit_counts'][c['name']] = None
    result['complete'] = result['estimate']['complete'] = False


def mask_pending_healing(result, full, shown, normal, duration, cycle):
    def pending(plan):
        return bool(plan and any(c['damage_type']=='healing' and 'actual_total' in c
                                and c['actual_total'] is None for c in plan['components']))

    def known(plan, boundary=None):
        components=[c for c in plan['components'] if c['damage_type']=='healing' and 'actual_total' not in c]
        return phase_totals(components,boundary)[1] if boundary is not None else sum(c['total'] for c in components)

    if not any(pending(plan) for plan in (full,shown,normal)):
        return
    skill=result['estimate']['skill']
    subtotal={'total_healing':known(full),
        'phase_healing':known(full,duration) if duration is not None else None,
        'window_healing':known(shown),
        'cycle_healing':known(full,cycle)+(known(normal) if normal else 0) if cycle is not None else None}
    subtotal['cycle_hps']=subtotal['cycle_healing']/cycle if cycle else None
    subtotal['window_hps']=subtotal['window_healing']/shown['duration'] if shown['duration'] else None
    result['known_healing_subtotals']=subtotal
    if pending(full):skill['total_healing']=skill['phase_healing']=None
    if cycle is not None and (pending(full) or pending(normal)):skill['cycle_healing']=skill['cycle_hps']=None
    if pending(shown):
        result['total_healing']=None
        skill['window_healing']=skill['window_hps']=None
    for c in full['components']:
        if c['damage_type']=='healing' and 'actual_total' in c and c['actual_total'] is None:
            skill['hit_counts'][c['name']]=None
    result['complete']=result['estimate']['complete']=False


def preserve_unplaced_sources(components, *, window, target_lifetime):
    """Keep conditional source amounts without inventing cast-time collisions.

    Owner acquisition/interrupt windows are not projectile coverage. Only an
    explicit empty observation or zero current-target lifetime excludes hits.
    """
    reference=[{k:c[k] for k in ('name','damage_type','per_hit','hits','total')} for c in components]
    possible=window!=0 and target_lifetime!=0
    for c in components:
        c.pop('times_seconds',None);c.pop('instant_event',None)
        c['timing_reference']='unplaced conditional source; actual collision clock unverified'
        if possible and c['hits']>0:c['actual_total']=None
        else:c['hits']=0;c['total']=0
    return {'conditional_components':reference,'source_possible':possible,
            'observation_seconds':window,'collision_clock_verified':False}

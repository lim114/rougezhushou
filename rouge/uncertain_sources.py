"""Preserve known source subtotals without publishing unplaced damage as actual."""
from .timing import phase_totals


def mask_pending_damage(result, full, shown, normal, duration, cycle):
    def pending(plan):
        return bool(plan and any('actual_total' in c and c['actual_total'] is None
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
        'total_damage': known(full),
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

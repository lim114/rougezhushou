"""Shared S2 replenishment budget for declared active-skill barrier breaks.

This projection has no callback scheduler, damage clock, book polling, or end
controller. Reaching zero does not itself finish the skill or remove a shield.
"""
from dataclasses import dataclass, field
from .ammo_counter import AmmoCounter, AmmoConsumption, _integer


@dataclass
class BarrierAmmoProjection:
    maximum: int
    breaks: dict = field(default_factory=lambda: {'owner': 0, 'structure': 0}, init=False)
    inactive_breaks: int = field(default=0, init=False)

    def __post_init__(self):
        _integer(self.maximum, '屏障共享弹匣', minimum=1)
        self.counter = AmmoCounter(self.maximum)
        self.consumption = AmmoConsumption(self.counter, 7, 1,
            ignore_trigger_once=True, reset_when_attack_finished=False)
        # Opening grants a shield to both available recipients without sending
        # CharSkillManualTriggerCountEvent. The structure's presence is not
        # inferred by this resource projection.
        self.consumption.on_cast_start()

    def barrier_break(self, source, *, skill_active=True):
        if source not in ('owner', 'structure'):
            raise ValueError('破屏来源需要owner或structure。')
        if type(skill_active) is not bool:
            raise ValueError('技能生效条件需要布尔值。')
        self.breaks[source] += 1
        if not skill_active:self.inactive_breaks += 1
        # The template reads the caster's remainingCount BEFORE the manual
        # count event, then recreates this recipient's barrier. A final bullet
        # therefore still funds one replenishment; actual ending is on a
        # separate controller path, whose tick order is not bound here.
        eligible = skill_active and self.counter.raw_remaining > 0
        spent = self.consumption.on_event(7) if eligible else 0
        return {'source': source, 'ammunition_consumed': spent,
                'barrier_replenished': bool(eligible),
                'remaining': self.counter.remaining}

    def output(self):
        return {'maximum': self.counter.maximum,
                'declared_breaks': sum(self.breaks.values()),
                'source_counts': dict(self.breaks), 'inactive_breaks': self.inactive_breaks,
                'ammunition_consumed_reference': self.counter.consumed,
                'barrier_replenishments_reference': self.counter.consumed,
                'ammunition_remaining_reference': self.counter.remaining,
                'progress_exhausted_reference': self.counter.raw_remaining <= 0,
                'initial_barrier_grant_ammunition_cost': 0,
                'shared_owner_structure_counter_verified': True,
                'skill_finished': None, 'actual_end_seconds': None,
                'actual_ammunition_consumption_times_seconds': None,
                'events_scheduled': False,
                'conditions': ['所声明技能主buff仍生效', '所属skill ability计数门isAffecting成立，不能由主buff存在推导', '未发生补弹或最大弹药变动'],
                'counting_ability_is_affecting_assumed': True,
                'source_evidence': 'research/p2-mechanist-s2-shared-barrier-current/receipt.json'}


def declared_barrier_ammo(maximum, count):
    """An aggregate active-break declaration, with recipient counts unknown."""
    _integer(count, '声明总破屏次数')
    projection = BarrierAmmoProjection(maximum)
    # No source ordering is invented. Both recipients use the same counter;
    # the aggregate resource arithmetic is independent of their allocation.
    spent = min(count, projection.counter.maximum)
    if spent:
        projection.counter.consume(spent)
    out = projection.output()
    out.update(declared_breaks=count, source_counts=None)
    return out

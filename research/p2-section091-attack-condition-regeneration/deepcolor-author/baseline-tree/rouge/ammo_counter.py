"""Offline counter contracts verified against the public native prefabs.

Counters describe a supplied scenario, never observed combat state. Ordinary
supported skills use one counter. Angel S2 retains separate mode counters;
their selection/consumption history must be supplied rather than inferred.
"""
from dataclasses import dataclass, field


def _integer(value, label, *, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(label + ' must be an integer within its supported range.')
    return value


@dataclass
class AmmoCounter:
    base_max: int
    consumed: int = 0
    recovered: int = 0
    ready_to_reset: bool = False
    recover_limit_override: int | None = None
    additions: dict = field(default_factory=dict)

    def __post_init__(self):
        _integer(self.base_max, 'base maximum', minimum=1)
        _integer(self.consumed, 'consumed count')
        _integer(self.recovered, 'recovered count')
        if self.recover_limit_override is not None:
            _integer(self.recover_limit_override, 'recovery limit')
        if not isinstance(self.ready_to_reset, bool):
            raise ValueError('ready_to_reset must be boolean.')
        self.additions = dict(self.additions)
        for uid, value in self.additions.items():
            self._check_addition(uid, value)

    @staticmethod
    def _check_addition(uid, value):
        if not isinstance(uid, str) or not uid or isinstance(value, bool) or not isinstance(value, int):
            raise ValueError('A capacity modifier requires its UID and integer value.')

    @property
    def maximum(self):
        return max(1, self.base_max + sum(self.additions.values()))

    @property
    def raw_remaining(self):
        return self.maximum - self.consumed

    @property
    def remaining(self):
        # Offline loop/display convenience. The ordinary native raw getter can
        # be negative after removing capacity; preserve it separately above.
        return max(0, self.raw_remaining)

    @property
    def recovery_limit(self):
        return self.maximum if self.recover_limit_override is None else self.recover_limit_override

    def set_addition(self, uid, value):
        self._check_addition(uid, value)
        self.additions[uid] = value

    def remove_addition(self, uid):
        self.additions.pop(uid, None)

    def consume(self, count):
        """Record an explicitly supplied consumption, not a callback schedule."""
        _integer(count, 'attack consumption', minimum=1)
        # Native DealCountEvent adds the complete expenditure without capping
        # m_eventCount. Clamping here loses partial-packet consumption and can
        # manufacture ammunition after a later capacity increase.
        self.consumed += count

    def recover(self, requested):
        _integer(requested, 'recovery request')
        if self.ready_to_reset:
            return 0
        budget = max(0, min(self.recovered + requested, self.recovery_limit)) - self.recovered
        actual = max(0, min(budget, self.consumed))
        self.recovered += actual
        self.consumed -= actual
        return actual


@dataclass
class AmmoConsumption:
    """Default counter's consumption gate for explicitly supplied events.

    This is not an event scheduler or the skill's completion controller. In
    particular, cast-end readiness, period waiting, effects and shared-board
    persistence are outside this projection. See ammo-events-067/REPORT.md.
    """
    counter: AmmoCounter
    count_event: int
    expend_per_trigger: int
    ignore_trigger_once: bool = False
    reset_when_attack_finished: bool = False
    triggered: bool = False
    not_count_next: bool = False
    ignore_until_cast_end: bool = False

    def __post_init__(self):
        if not isinstance(self.counter, AmmoCounter):
            raise ValueError('An ordinary ammunition counter is required.')
        _integer(self.count_event, 'count event')
        _integer(self.expend_per_trigger, 'expenditure', minimum=1)
        for name in ('ignore_trigger_once', 'reset_when_attack_finished',
                     'triggered', 'not_count_next', 'ignore_until_cast_end'):
            if type(getattr(self, name)) is not bool:
                raise ValueError(name + ' must be boolean.')

    def on_cast_start(self):
        # OnCastStart only clears m_ignoreCountEventUntilCastEnd.
        self.ignore_until_cast_end = False

    def on_event(self, event):
        _integer(event, 'ability event')
        spent = 0
        if (event == self.count_event and not self.ignore_until_cast_end
                and (not self.triggered or self.ignore_trigger_once)):
            # OnEvent calls vslot16 (DealCountEvent) after the notification
            # hook. A zero-cost event still marks m_triggerOnce.
            self.triggered = True
            spent = 0 if self.not_count_next else self.expend_per_trigger
            if spent:
                self.counter.consume(spent)
        if event in (1, 3):  # ON_DETACHED, ON_CAST_END
            self.not_count_next = self.triggered = self.ignore_until_cast_end = False
        elif event == 6 and self.reset_when_attack_finished:
            self.not_count_next = self.triggered = False
        return spent

    def ordinary_cast(self):
        """One complete uninterrupted ordinary cast, with no wall-clock claim."""
        self.on_cast_start()
        spent = self.on_event(4) + self.on_event(5)  # SPELL_ON, SPELL_END
        self.on_event(3)
        self.on_event(6)
        return spent


# Actual serialized AbilityEventCounter configurations, uniquely matched by
# MonoScript type hash; these bindings do not enable special refill paths.
_CONSUMPTION_BINDINGS = {
    ('kaltsit', 2): (4, 1, False, True),
    ('mechanist', 1): (4, 1, False, True),
    ('char_1035_wisdel', 3): (4, 1, False, True),
    ('char_1041_angel2', 1): (4, 1, True, False),
    ('char_1041_angel2', 2): (5, 1, False, False),
    ('char_1041_angel2', 3): (4, 5, False, False),
}


def consumption_for(counter, scenario, cost):
    """Bind only proven ordinary counter types; keep explicit generic callers."""
    binding = _CONSUMPTION_BINDINGS.get((scenario.get('operator'), scenario.get('skill')))
    if binding is None:
        return None
    event, actual_cost, repeat, attack_end = binding
    if cost != actual_cost:
        raise ValueError('单次耗弹与该技能已核验的计数器配置不一致。')
    return AmmoConsumption(counter, event, actual_cost, repeat, attack_end)


@dataclass
class ExtraModeCounters:
    """Main maximum; summed consumption; recovery into the active counter."""
    main: AmmoCounter
    extras: dict
    current_mode: int

    @property
    def maximum(self):
        return self.main.maximum

    @property
    def remaining(self):
        consumed = self.main.consumed + sum(c.consumed for c in self.extras.values())
        return self.maximum - min(self.maximum, consumed)

    @property
    def active(self):
        return self.extras.get(self.current_mode, self.main)

    def recover(self, requested):
        return self.active.recover(requested)


def poll_book(counter, parameters, finished):
    """The native eligible action consumes the book even if recovery is zero."""
    if finished:
        return None
    # The native action derives threshold/request from the current skill max
    # at each poll. Never silently reuse a parameter snapshot from before a
    # UID capacity change; callers must recompute it via refill_parameters.
    if parameters['maximum'] != counter.maximum:
        raise ValueError('补弹参数与当前最大弹药不一致，需要重新计算阈值和恢复数量。')
    if not 0 < counter.remaining <= parameters['threshold']:
        return None
    requested = parameters['refill_count']
    recovered = counter.recover(requested)
    return {'requested': requested, 'recovered': recovered,
        'remaining_after': counter.remaining, 'finished': True}

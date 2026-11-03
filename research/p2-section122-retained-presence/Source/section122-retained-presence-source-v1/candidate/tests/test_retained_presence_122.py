"""Public temporary raw JSON and actual consumers; author has not run these.

Section 122 changes software qualification, not game recruitment or buff-loss
mechanics. Root must run this module and the separate actual-window plan.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from rouge.catalog import catalog, operator_profiles
from rouge.damage import calculate_damage
from rouge.record_flags import (record_flag, active_record, metadata_mask,
                                projected_run_metadata, RECIPIENT_KEYS)
from rouge.recipient_state import invalidate_recipient_absence
from rouge.relic_counter_semantics import counter_resources, _verified_bindings
from rouge.relics import mechanics
from rouge.run_metadata_view import format_run_buff_status
from rouge.run_state import RunState
from rouge.training_view import (select_training_view, run_operator_metadata,
                                 format_run_training_observation)


OP = 'mechanist'
ATTACK_RELIC = 'rogue_6_relic_legacy_15'
ALTAR = 'rogue_6_relic_legacy_103'
TOOL = 'rogue_6_active_tool_5'
SNACK_PARENT = 'rogue_6_relic_assign_13'
RANDOM_PARENT = 'rogue_6_relic_assign_15'
RANDOM_BUFF = 'rogue_6_from_relic_15'
SNACK = 'rogue_6_from_relic_13'
COOKIE = 'rogue_6_from_relic_9'
UNKNOWN_FLAGS = ('false', 'true', '', 0, 1, -1, 0.0, -0.0, 1.0,
                 None, [], [False], {}, {'public': True})


def native(value, seen=None):
    """Builtin type, order, signed-float and shared-reference receipt."""
    if seen is None: seen = {}
    kind = type(value)
    if value is None: return ('None',)
    if kind is float: return ('float', value.hex())
    if kind in (bool, int, str): return (kind.__name__, value)
    if kind not in (dict, list, tuple): raise TypeError(kind.__name__)
    if id(value) in seen: return ('ref', seen[id(value)])
    label = len(seen); seen[id(value)] = label
    if kind is dict:
        return ('dict', label, tuple((native(k, seen), native(v, seen)) for k, v in value.items()))
    return (kind.__name__, label, tuple(native(item, seen) for item in value))


def member(**extra):
    return {'id': OP, 'scope': 'run', 'present': True,
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1},
            'skill_ranks': {'1': 7}, 'captured_at': 900.0,
            'recruitment_kind': 'emergency_hire', 'advanced': False,
            'char_buff_ids': [SNACK], 'char_buffs_complete': True,
            'char_buff_absent_ids': [COOKIE], 'char_buff_pending_ids': [],
            'public_opaque': {'signed_zero': -0.0, 'nullable': None}, **extra}


def observed_member(**extra):
    return {'id': OP, 'scope': 'run', 'fields': {}, 'skill_ranks': {}, **extra}


def full_bar(*identities):
    return {'relics': {'ids': list(identities), 'count': len(identities),
            'icons': [{'id': rid, 'candidates': [rid], 'confirmed': True,
                       'source': 'held_icon_and_usage'} for rid in identities],
            'source': 'held_bar'}}


class RetainedPresence122Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = operator_profiles()
        cls.implemented = catalog()['operators']

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='public-retained122-')
        self.addCleanup(temporary.cleanup)
        self.file = Path(temporary.name) / 'run.json'

    def load(self, omit_memory=False, **changes):
        saved = {'id': 'public-retained122', 'started_at': 0.0, 'last_read': 1000.0,
                 'operators': {}, 'relics': {}, 'tactical_tools': {}, 'history': [],
                 'relic_icon_memory': None, **copy.deepcopy(changes)}
        if omit_memory: saved.pop('relic_icon_memory')
        raw = (json.dumps(saved, ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
        self.file.write_bytes(raw)
        run = RunState(self.file)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(self.file.read_bytes(), raw)
        return run, raw

    def query(self, run, raw, action):
        before = native(run.state)
        result = action()
        self.assertEqual(native(run.state), before)
        self.assertEqual(self.file.read_bytes(), raw)
        self.assertFalse(self.file.with_suffix('.tmp').exists())
        return result

    def apply(self, run, observed, at=1001.0):
        before = native(observed)
        self.assertIs(run.apply(observed, at), True)
        self.assertEqual(native(observed), before)
        self.assertFalse(self.file.with_suffix('.tmp').exists())

    def flags(self, run, kind=None):
        return [event for event in run.state['history']
                if event['kind'] == 'state_flag_reconfirmed'
                and (kind is None or event['record_kind'] == kind)]

    def account(self):
        return {'id': OP, 'scope': 'operator_profile', 'fields':
                {'elite': 2, 'level': 40, 'trust': 25, 'potential': 2},
                'skill_ranks': {'1': 3}, 'captured_at': 800.0}

    def choose(self, record):
        return select_training_view(OP, self.account(), record, self.profiles, self.implemented)

    def counter(self, at=900.0):
        proof = {'id': ALTAR, 'title': _verified_bindings()[ALTAR]['name'], 'value': 1,
                 'source': 'held_full_name_usage_and_public_test',
                 'box': [[.1,.1],[.2,.1],[.2,.2],[.1,.2]]}
        result = counter_resources([proof])['altar_stacks']; result['captured_at'] = at
        return result

    def test_projection_distinguishes_exact_bool_missing_and_every_raw_json_kind(self):
        for key in ('held', 'present'):
            record = {'public_opaque': [None, -0.0]}; before = native(record)
            self.assertIs(record_flag(record, key), True)
            self.assertIs(active_record(record, key), True)
            self.assertEqual(native(record), before)
            for flag in (True, False, *UNKNOWN_FLAGS):
                with self.subTest(key=key, flag=flag, native_type=type(flag).__name__):
                    record[key] = copy.deepcopy(flag); before = native(record)
                    self.assertIs(record_flag(record, key), flag if type(flag) is bool else None)
                    self.assertIs(active_record(record, key), flag is True)
                    self.assertEqual(native(record), before)

    def test_raw_nonbool_item_flags_are_retained_but_do_not_complete_or_apply(self):
        for flag in UNKNOWN_FLAGS:
            with self.subTest(flag=flag, native_type=type(flag).__name__):
                run, raw = self.load(relics={ATTACK_RELIC: {'held': flag}},
                                     tactical_tools={TOOL: {'held': flag}},
                                     relic_count=0, inventory_verified=True)
                self.assertEqual(self.query(run, raw, run.held_relic_ids), [])
                self.assertEqual(self.query(run, raw, run.held_tool_ids), [])
                status = self.query(run, raw, run.inventory_status)
                self.assertIs(status['complete'], False)
                self.assertEqual(status['unconfirmed_item_ids'], [ATTACK_RELIC, TOOL])
                self.assertIn('持有状态未确认', self.query(run, raw, run.summary))
                scenario = {'operator': OP, 'skill': 3, 'relic_ids': run.held_relic_ids()}
                before = native(scenario); result = calculate_damage(scenario)
                self.assertEqual(result, calculate_damage({'operator': OP, 'skill': 3, 'relic_ids': []}))
                self.assertEqual(native(scenario), before)

    def test_qualified_real_relic_still_changes_actual_attack(self):
        run, raw = self.load(relics={ATTACK_RELIC: {'held': True}},
                             tactical_tools={TOOL: {'held': False}},
                             relic_count=1, inventory_verified=True)
        status = self.query(run, raw, run.inventory_status)
        self.assertNotIn('unconfirmed_item_ids', status); self.assertIs(status['complete'], True)
        base = calculate_damage({'operator': OP, 'skill': 3, 'relic_ids': []})
        held = calculate_damage({'operator': OP, 'skill': 3, 'relic_ids': run.held_relic_ids()})
        self.assertGreater(held['estimate']['base_stats']['attack'], base['estimate']['base_stats']['attack'])

    def test_missing_flags_keep_legacy_active_contract_without_writing_flags(self):
        record = member(); record.pop('present')
        run, raw = self.load(operators={OP: record}, relics={ATTACK_RELIC: {}},
                             tactical_tools={TOOL: {}}, relic_count=2, inventory_verified=True)
        self.assertEqual(self.query(run, raw, run.held_relic_ids), [ATTACK_RELIC])
        self.assertEqual(self.query(run, raw, run.held_tool_ids), [TOOL])
        self.assertIs(self.query(run, raw, run.inventory_status)['complete'], True)
        self.assertIn('当前已识别 1 /', self.query(run, raw, run.summary))
        self.assertEqual(self.choose(run.state['operators'][OP])['selection'], 'run_and_account')
        self.assertIs(run_operator_metadata(run.state['operators'][OP]), run.state['operators'][OP])
        self.assertNotIn('held', run.state['relics'][ATTACK_RELIC]); self.assertNotIn('present', record)

    def test_nonbool_presence_uses_account_and_explicit_unconfirmed_displays(self):
        for flag in UNKNOWN_FLAGS:
            with self.subTest(flag=flag, native_type=type(flag).__name__):
                run, raw = self.load(operators={OP: member(present=flag)})
                record = run.state['operators'][OP]
                chosen = self.query(run, raw, lambda: self.choose(record))
                self.assertEqual(chosen['selection'], 'account_after_unconfirmed_presence')
                self.assertEqual(chosen['state']['skill_ranks'], {'1': 3})
                self.assertIn('在场标记未确认', chosen['notice'])
                self.assertEqual(self.query(run, raw, lambda: run_operator_metadata(record)), {})
                self.assertIn('在场状态未确认', self.query(run, raw, run.summary))
                self.assertNotIn('已离队', run.summary())
                self.assertIn('在场状态未确认', format_run_training_observation(OP, record))
                self.assertIn('在场状态未确认', format_run_buff_status(record, mechanics()['char_buffs']))

    def test_false_presence_keeps_departure_label_and_inactive_metadata(self):
        run, raw = self.load(operators={OP: member(present=False)})
        record = run.state['operators'][OP]
        self.assertIn('已离队', self.query(run, raw, run.summary))
        self.assertNotIn('在场状态未确认', run.summary())
        self.assertEqual(self.choose(record)['selection'], 'account')
        self.assertEqual(run_operator_metadata(record), {})
        self.assertEqual(format_run_buff_status(record, mechanics()['char_buffs']),
                         '个人强化归属尚未确认；不会根据持有藏品推断')

    def test_legacy_signature_cannot_requalify_unknown_possession_at_load(self):
        run, raw = self.load(relics={ATTACK_RELIC: {'held': 'false'}}, relic_count=1,
                             bar_signature=[[ATTACK_RELIC]], inventory_verified=True, omit_memory=True)
        self.assertIs(run.state['relic_icon_memory'], None)
        self.assertEqual(self.query(run, raw, run.held_relic_ids), [])
        self.assertFalse(self.query(run, raw, run.inventory_status)['complete'])

    def test_suspended_raw_icon_memory_survives_unread_and_unqualified_cards(self):
        memory = {'icons': [{'id': ATTACK_RELIC, 'candidates': [ATTACK_RELIC],
                            'confirmed': True, 'source': 'held_icon_and_usage'}],
                  'count': 1, 'complete_bar': True, 'captured_at': 900.0, 'source': 'held_bar'}
        for extra in ({}, {'relics': {'ids': [], 'icons': [], 'count': None, 'source': 'unread',
                         'cards': [{'id': ATTACK_RELIC, 'confirmed': False, 'source': 'public_unowned'}]}}):
            run, _ = self.load(relics={ATTACK_RELIC: {'held': 'false'}}, relic_count=1,
                               inventory_verified=True, relic_icon_memory=memory)
            self.apply(run, {'operators': [], **extra})
            self.assertEqual(native(run.state['relic_icon_memory']), native(memory))
            self.assertEqual(run.state['relics'][ATTACK_RELIC]['held'], 'false')
            self.assertEqual(run.held_relic_ids(), []); self.assertEqual(self.flags(run), [])

    def test_fresh_grade_cannot_replay_suspended_unconfirmed_variant_memory(self):
        base = 'rogue_6_relic_legacy_24'; candidates = [base, base+'_a', base+'_b', base+'_c']
        memory = {'icons': [{'id': base, 'candidates': candidates, 'confirmed': False,
                            'source': 'held_bar', 'score': .97}],
                  'count': 1, 'complete_bar': True, 'captured_at': 900.0, 'source': 'held_bar'}
        run, _ = self.load(relics={base+'_b': {'held': 'false'}}, relic_count=1,
                           inventory_verified=True, relic_icon_memory=memory)
        self.apply(run, {'config': {'difficulty': {'value': 3, 'source': '本局等级标签'}}})
        self.assertEqual(native(run.state['relic_icon_memory']), native(memory))
        self.assertEqual(run.state['relics'][base+'_b']['held'], 'false')
        self.assertEqual(run.held_relic_ids(), []); self.assertEqual(self.flags(run), [])
        self.assertEqual(set(run.state['relics']), {base+'_b'})

    def test_direct_positive_requalifies_unknown_without_acquisition_or_fake_recipient_grant(self):
        retained = {'held': 'false', 'public_old_proof': {'nullable': None, 'zero': -0.0}}
        run, _ = self.load(relics={RANDOM_PARENT: retained},
                           operators={OP: member(char_buff_ids=[], char_buffs_complete=True)})
        self.apply(run, full_bar(RANDOM_PARENT))
        self.assertIs(run.state['relics'][RANDOM_PARENT]['held'], True)
        events = self.flags(run, 'relic'); self.assertEqual(len(events), 1)
        self.assertEqual(native(events[0]['previous_record']), native(retained))
        kinds = [e['kind'] for e in run.state['history']]
        self.assertNotIn('relic_confirmed', kinds); self.assertNotIn('char_buff_absence_invalidated', kinds)
        self.assertTrue(run.state['operators'][OP]['char_buffs_complete'])

    def test_exact_false_gain_random_item_keeps_original_negative_invalidation(self):
        run, _ = self.load(relics={RANDOM_PARENT: {'held': False}},
                           operators={OP: member(char_buff_ids=[], char_buffs_complete=True)})
        self.apply(run, full_bar(RANDOM_PARENT))
        self.assertEqual(self.flags(run), [])
        self.assertTrue(any(e['kind']=='char_buff_absence_invalidated' for e in run.state['history']))
        self.assertIn(RANDOM_BUFF, run.state['operators'][OP]['char_buff_pending_ids'])

    def test_exact_false_positive_keeps_real_previous_confirmation_event(self):
        run, _ = self.load(relics={ATTACK_RELIC: {'held': False}})
        self.apply(run, full_bar(ATTACK_RELIC))
        self.assertEqual(self.flags(run), [])
        self.assertTrue(any(e['kind']=='relic_confirmed' and e['id']==ATTACK_RELIC for e in run.state['history']))

    def test_fresh_full_zero_closes_unknown_relic_and_tool_without_false_loss_events(self):
        run, _ = self.load(relics={ATTACK_RELIC: {'held': 'false'}},
                           tactical_tools={TOOL: {'held': 1}}, relic_count=0, inventory_verified=True)
        self.apply(run, full_bar())
        self.assertIs(run.state['relics'][ATTACK_RELIC]['held'], False)
        self.assertIs(run.state['tactical_tools'][TOOL]['held'], False)
        self.assertEqual(len(self.flags(run)), 2)
        self.assertFalse(any(e['kind'] in ('relic_no_longer_held','tool_no_longer_held') for e in run.state['history']))
        self.assertIs(run.inventory_status()['complete'], True)
        self.assertNotIn('unconfirmed_item_ids', run.inventory_status())

    def test_fresh_empty_crew_closes_unknown_without_manufacturing_departure(self):
        old = member(present='false'); run, _ = self.load(operators={OP: old})
        self.apply(run, {'crew_count': 0, 'operators': []})
        record = run.state['operators'][OP]
        self.assertIs(record['present'], False)
        self.assertEqual(record['fields'], old['fields']); self.assertEqual(record['char_buff_ids'], old['char_buff_ids'])
        self.assertEqual(self.flags(run, 'operator')[0]['previous_record'], old)
        self.assertFalse(any(e['kind']=='operator_no_longer_present' for e in run.state['history']))
        self.assertTrue(metadata_mask(record).intersection(RECIPIENT_KEYS))

    def test_identity_only_reconfirmation_masks_old_training_origin_and_buffs(self):
        old = member(present='false'); run, _ = self.load(operators={OP: old})
        self.apply(run, {'operators': [observed_member()]})
        record = run.state['operators'][OP]; view = run_operator_metadata(record)
        self.assertIs(record['present'], True)
        self.assertEqual(record['fields'], old['fields']); self.assertEqual(record['skill_ranks'], old['skill_ranks'])
        self.assertEqual(record['char_buff_ids'], old['char_buff_ids'])
        self.assertEqual(record['char_buff_absent_ids'], old['char_buff_absent_ids'])
        self.assertIs(record['char_buffs_complete'], True)
        self.assertEqual(view['char_buff_ids'], []); self.assertIs(view['char_buffs_complete'], False)
        self.assertIs(view['recruitment_kind'], None); self.assertNotIn('advanced', view)
        chosen = self.choose(record)['state']; self.assertEqual(chosen['fields'], self.account()['fields'])
        self.assertEqual(chosen['skill_ranks'], {}); self.assertIs(chosen['recruitment_kind'], None)
        self.assertEqual(self.flags(run, 'operator')[0]['previous_record'], old)
        self.assertFalse(any(e['kind']=='recruitment_changed' for e in run.state['history']))
        restored = RunState(self.file); self.assertEqual(run_operator_metadata(restored.state['operators'][OP])['char_buff_ids'], [])

    def test_explicit_training_and_origin_fields_only_unmask_their_new_evidence(self):
        run, _ = self.load(operators={OP: member(present=1)})
        self.apply(run, {'operators': [observed_member(fields={'level': 55}, skill_ranks={'1': 4},
                                   recruitment_kind='non_emergency', advanced=True)]})
        record = run.state['operators'][OP]; selected = self.choose(record)['state']
        self.assertEqual(selected['fields']['level'], 55); self.assertEqual(selected['fields']['elite'], 2)
        self.assertEqual(selected['skill_ranks'], {'1': 4}); self.assertIn('elite', record['invalid_fields'])
        metadata = run_operator_metadata(record)
        self.assertEqual(metadata['recruitment_kind'], 'non_emergency'); self.assertIs(metadata['advanced'], True)
        self.assertEqual(metadata['char_buff_ids'], [])
        self.assertFalse(any(e['kind'] in ('recruitment_changed','char_buff_absence_invalidated') for e in run.state['history']))

    def test_partial_popup_qualifies_only_fresh_ids_and_full_popup_then_replaces_group(self):
        run, _ = self.load(operators={OP: member(present='false')})
        self.apply(run, {'operators': [observed_member(char_buff_ids=[COOKIE], char_buffs_complete=False)]})
        record = run.state['operators'][OP]
        self.assertEqual(record['char_buff_ids'], [SNACK, COOKIE])
        self.assertEqual(run_operator_metadata(record)['char_buff_ids'], [COOKIE])
        self.assertTrue(metadata_mask(record).intersection(RECIPIENT_KEYS))
        self.apply(run, {'operators': [observed_member()]}, at=1002.0)
        self.assertEqual(run_operator_metadata(run.state['operators'][OP])['char_buff_ids'], [COOKIE])
        self.apply(run, {'operators': [observed_member(char_buff_ids=[SNACK], char_buffs_complete=False)]}, at=1003.0)
        self.assertEqual(run_operator_metadata(run.state['operators'][OP])['char_buff_ids'], [COOKIE, SNACK])
        self.apply(run, {'operators': [observed_member(char_buff_ids=[], char_buffs_complete=True)]}, at=1004.0)
        record = run.state['operators'][OP]
        self.assertFalse(metadata_mask(record).intersection(RECIPIENT_KEYS))
        self.assertEqual(run_operator_metadata(record)['char_buff_ids'], [])
        self.assertIs(run_operator_metadata(record)['char_buffs_complete'], True)
        self.assertIn('已核对：无个人强化', format_run_buff_status(record, mechanics()['char_buffs']))

    def test_masked_old_snack_never_changes_sp_until_its_own_fresh_popup(self):
        run, _ = self.load(operators={OP: member(present='false')})
        self.apply(run, {'operators': [observed_member()]})
        view = run_operator_metadata(run.state['operators'][OP])
        self.assertEqual(calculate_damage({'operator': OP, 'skill': 3, 'char_buff_ids': view['char_buff_ids']})['estimate']['skill']['sp_cost'], 35)
        self.apply(run, {'operators': [observed_member(char_buff_ids=[SNACK], char_buffs_complete=False)]}, at=1002.0)
        view = run_operator_metadata(run.state['operators'][OP])
        self.assertEqual(calculate_damage({'operator': OP, 'skill': 3, 'char_buff_ids': view['char_buff_ids']})['estimate']['skill']['sp_cost'], 28)

    def test_unknown_prior_elite_and_origin_do_not_generate_promotion_recruitment_or_gold_correction(self):
        old = member(present='true', fields={'elite': 1, 'level': 40},
                     sources={'recruitment_kind': {'source': '金色应急雇佣标记'}})
        run, _ = self.load(operators={OP: old}, relics={SNACK_PARENT: {'held': True}})
        self.apply(run, {'operators': [observed_member(fields={'elite': 2}, advanced=True,
                                                     recruitment_kind='non_emergency')]})
        kinds = [e['kind'] for e in run.state['history']]
        self.assertFalse(set(kinds).intersection(('recruitment_changed','classification_corrected','char_buff_absence_invalidated')))
        self.assertEqual(run_operator_metadata(run.state['operators'][OP])['char_buff_ids'], [])

    def test_exact_true_promotion_keeps_original_recipient_invalidation(self):
        old = member(fields={'elite': 1, 'level': 40}, char_buff_ids=[], char_buffs_complete=True)
        run, _ = self.load(operators={OP: old}, relics={SNACK_PARENT: {'held': True, 'captured_at': 800.0}})
        self.apply(run, {'operators': [observed_member(fields={'elite': 2}, advanced=True)]})
        self.assertTrue(any(e['kind']=='char_buff_absence_invalidated' for e in run.state['history']))
        self.assertIn(SNACK, run.state['operators'][OP]['char_buff_pending_ids'])

    def test_second_page_does_not_use_unconfirmed_old_origin_elite_or_advanced_as_baseline(self):
        old = member(present='true', fields={'elite': 1, 'level': 40},
                     sources={'recruitment_kind': {'source': '金色应急雇佣标记'}})
        run, _ = self.load(operators={OP: old}, relics={SNACK_PARENT: {'held': True}})
        self.apply(run, {'operators': [observed_member()]})
        self.apply(run, {'operators': [observed_member(fields={'elite': 2}, advanced=True,
                                                     recruitment_kind='non_emergency')]}, at=1002.0)
        kinds = [e['kind'] for e in run.state['history']]
        self.assertFalse(set(kinds).intersection(('recruitment_changed','classification_corrected','char_buff_absence_invalidated')))
        record = run.state['operators'][OP]
        self.assertEqual(record['char_buff_ids'], [SNACK])
        self.assertEqual(run_operator_metadata(record)['char_buff_ids'], [])
        self.assertEqual(run_operator_metadata(record)['recruitment_kind'], 'non_emergency')

    def test_healthy_counter_still_reuses_exact_original_resource_and_history(self):
        old = self.counter()
        run, raw = self.load(relics={ALTAR: {'held': True}}, resources={'altar_stacks': old})
        resources = self.query(run, raw, run.calculation_resources)
        self.assertEqual(native(resources['altar_stacks']), native(old))
        self.assertEqual(self.flags(run), [])

    def test_recipient_lifecycle_does_not_consume_unconfirmed_presence_or_masked_absences(self):
        for record in (member(present='false', char_buff_ids=[]),
                       member(char_buff_ids=[], unconfirmed_run_metadata=list(RECIPIENT_KEYS))):
            run, raw = self.load(operators={OP: record}, relics={SNACK_PARENT: {'held': True, 'captured_at': 1001.0}})
            before = native(run.state)
            invalidate_recipient_absence(run.state, [], {SNACK_PARENT}, {OP}, 1001.0)
            self.assertEqual(native(run.state), before); self.assertEqual(self.file.read_bytes(), raw)

    def test_counter_proof_is_retained_but_unavailable_until_new_held_counter_read(self):
        old = self.counter(); run, raw = self.load(relics={ALTAR: {'held': 'false'}}, resources={'altar_stacks': old})
        self.assertEqual(self.query(run, raw, run.calculation_resources), {})
        self.apply(run, full_bar(ALTAR))
        self.assertEqual(run.state['resources']['altar_stacks'], old)
        self.assertEqual(run.calculation_resources(), {})
        fresh = {k:v for k,v in self.counter().items() if k!='captured_at'}
        self.apply(run, {**full_bar(ALTAR), 'resources': {'altar_stacks': fresh}}, at=1002.0)
        self.assertEqual(run.calculation_resources()['altar_stacks']['value'], 1)
        self.assertEqual(RunState(self.file).calculation_resources()['altar_stacks']['value'], 1)

    def test_unknown_false_then_true_does_not_revive_counter_before_qualification_cutoff(self):
        old = self.counter(); run, _ = self.load(relics={ALTAR: {'held': None}}, resources={'altar_stacks': old})
        self.apply(run, full_bar())
        self.assertIs(self.flags(run, 'relic')[0]['value'], False)
        self.apply(run, full_bar(ALTAR), at=1002.0)
        self.assertEqual(run.calculation_resources(), {})
        self.assertEqual(run.state['resources']['altar_stacks'], old)

    def test_same_packet_counter_proof_at_qualification_cutoff_is_current(self):
        run, _ = self.load(relics={ALTAR: {'held': 'false'}})
        fresh = {k:v for k,v in self.counter().items() if k!='captured_at'}
        self.apply(run, {**full_bar(ALTAR), 'resources': {'altar_stacks': fresh}})
        self.assertEqual(run.calculation_resources()['altar_stacks']['captured_at'], 1001.0)

    def test_stale_or_other_run_packet_does_not_requalify_or_write(self):
        run, raw = self.load(operators={OP: member(present='false')}, relics={ATTACK_RELIC: {'held': 'false'}})
        for observed, at in (({'operators': [observed_member()]}, 999.0),
                             ({**full_bar(ATTACK_RELIC), 'config_reuse': {'run_id': 'public-other122'}}, 1001.0)):
            before = native(run.state); caller = native(observed)
            self.assertIs(run.apply(observed, at), False)
            self.assertEqual(native(run.state), before); self.assertEqual(native(observed), caller)
            self.assertEqual(self.file.read_bytes(), raw); self.assertEqual(self.flags(run), [])

    def test_healthy_metadata_identity_and_labels_stay_byte_exact(self):
        for present in (True, 'missing'):
            record = member();
            if present == 'missing': record.pop('present')
            self.assertIs(projected_run_metadata(record), record)
            self.assertIs(run_operator_metadata(record), record)
            self.assertEqual(format_run_buff_status(record, mechanics()['char_buffs']), mechanics()['char_buffs'][SNACK]['name'])
            self.assertEqual(self.choose(record)['state']['recruitment_kind'], 'emergency_hire')


if __name__ == '__main__':
    unittest.main()

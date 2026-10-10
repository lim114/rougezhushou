"""Real persisted JSON reuse and explicit unavailable-evidence display contracts."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from rouge.damage import calculate_damage
from rouge.relic_counter_semantics import (
    COUNTER_BINDINGS, _verified_bindings, counter_resources, valid_counter_resource,
)
from rouge.relics import mechanics
from rouge.run_metadata_view import format_run_buff_status
from rouge.run_state import RunState


SNACK = 'rogue_6_from_relic_13'
COOKIE = 'rogue_6_from_relic_9'
UNKNOWN = 'public-unknown-char-buff-101'
ALTAR = 'rogue_6_relic_legacy_103'
OTHER = 'rogue_6_relic_cargo_10'


def native(value, seen=None):
    """Builtin type/order/float/alias snapshot of these public JSON callers."""
    if seen is None:seen = {}
    kind = type(value)
    if value is None:return ('None',)
    if kind is float:return ('float', value.hex())
    if kind in (bool, int, str):return (kind.__name__, value)
    if kind not in (dict, list, tuple):raise TypeError(kind.__name__)
    if id(value) in seen:return ('ref', seen[id(value)])
    sequence = len(seen);seen[id(value)] = sequence
    if kind is dict:
        return ('dict', sequence, tuple((native(k, seen), native(v, seen)) for k, v in value.items()))
    return (kind.__name__, sequence, tuple(native(item, seen) for item in value))


class CacheConsumer101Tests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='public-cache101-')
        self.addCleanup(self.directory.cleanup)
        self.file = Path(self.directory.name)/'run.json'

    def load(self, changes):
        saved = {'id': 'public-cache101', 'started_at': 0.0, 'last_read': 1000.0,
                 'operators': {}, 'relics': {}, 'history': [], 'relic_icon_memory': None}
        saved.update(copy.deepcopy(changes))
        raw = (json.dumps(saved, ensure_ascii=False, allow_nan=False, indent=2)+'\n').encode()
        self.file.write_bytes(raw)
        run = RunState(self.file)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(self.file.read_bytes(), raw)
        return run, raw

    def view_unchanged(self, run, raw, action):
        original = native(run.state)
        result = action()
        self.assertEqual(native(run.state), original)
        self.assertEqual(self.file.read_bytes(), raw)
        self.assertFalse(self.file.with_suffix('.tmp').exists())
        return result

    def apply(self, run, observed):
        original = native(observed)
        self.assertIs(run.apply(observed, 1001.0), True)
        self.assertEqual(native(observed), original)
        self.assertFalse(self.file.with_suffix('.tmp').exists())

    def proof(self, rid=ALTAR, value=1):
        return {'id': rid, 'title': _verified_bindings()[rid]['name'], 'value': value,
                'source': 'held_full_name_usage_and_public_test',
                'box': [[.1, .1], [.2, .1], [.2, .2], [.1, .2]]}

    def member(self, **extra):
        return {'scope': 'run', 'present': True, 'char_buff_ids': [SNACK],
                'char_buffs_complete': False, 'char_buff_absent_ids': [],
                'char_buff_pending_ids': [], 'recruitment_kind': 'non_emergency', **extra}

    def label(self, member):
        before = native(member)
        value = format_run_buff_status(member, mechanics()['char_buffs'])
        self.assertEqual(native(member), before)
        return value

    def test_saved_text_count_remains_raw_and_readable_before_observation(self):
        run, raw = self.load({'relic_count': '0'})
        self.view_unchanged(run, raw, run.summary)
        self.assertIs(type(run.state['relic_count']), str)
        self.assertEqual(run.state['relic_count'], '0')

    def test_unread_empty_page_reuses_text_count_without_false_full_inventory(self):
        run, _ = self.load({'relic_count': '0', 'inventory_verified': False})
        self.apply(run, {'operators': []})
        self.assertEqual(run.state['relic_count'], '0')
        self.assertFalse(run.state['inventory_verified'])
        self.assertFalse(run.inventory_status()['complete'])
        self.assertFalse(any(e['kind']=='relic_no_longer_held' for e in run.state['history']))
        restored = RunState(self.file)
        self.assertIs(type(restored.state['relic_count']), str)
        self.assertEqual(restored.state['relic_count'], '0')

    def test_unread_positive_page_keeps_old_holdings_with_opaque_count(self):
        run, _ = self.load({'relic_count': '0', 'relics': {OTHER: {'held': True}}})
        self.apply(run, {'relics': {'ids': [ALTAR], 'count': None, 'icons': [], 'source': 'held_card'}})
        self.assertEqual(set(run.held_relic_ids()), {OTHER, ALTAR})
        self.assertEqual(run.state['relic_count'], '0')
        self.assertFalse(run.inventory_status()['complete'])

    def test_fresh_explicit_zero_authoritatively_replaces_legacy_text_and_holdings(self):
        run, _ = self.load({'relic_count': '0', 'relics': {OTHER: {'held': True}}})
        self.apply(run, {'relics': {'ids': [], 'count': 0, 'icons': [], 'source': 'held_bar'}})
        self.assertIs(type(run.state['relic_count']), int)
        self.assertEqual(run.state['relic_count'], 0)
        self.assertEqual(run.held_relic_ids(), [])
        self.assertTrue(run.inventory_status()['complete'])

    def test_known_numeric_legacy_counts_keep_original_consumption(self):
        for count in (None, False, True, 0, 1, 0.0, -1, 1.5):
            with self.subTest(count=count, kind=type(count).__name__):
                run, _ = self.load({'relic_count': count})
                self.apply(run, {'operators': []})
                self.assertIs(type(run.state['relic_count']), type(count))
                self.assertEqual(run.state['relic_count'], count)

    def test_non_numeric_saved_counts_are_not_global_rejection_or_normalization(self):
        for count in ('0', [], {}, 'public-opaque'):
            with self.subTest(count=count):
                run, _ = self.load({'relic_count': count})
                self.apply(run, {'operators': []})
                self.assertEqual(native(run.state['relic_count']), native(count))
                self.assertFalse(run.inventory_status()['complete'])

    def test_incoming_bool_still_follows_existing_unread_path(self):
        for value in (False, True):
            with self.subTest(value=value):
                run, _ = self.load({'relic_count': '0'})
                observed = {'relics': {'ids': [], 'icons': [], 'count': value, 'source': 'held_bar'}}
                self.apply(run, observed)
                self.assertIs(observed['relics']['count'], value)
                self.assertIs(type(run.state['relic_count']), str)
                self.assertFalse(run.inventory_status()['complete'])

    def test_fresh_float_zero_retains_existing_native_numeric_contract(self):
        run, _ = self.load({'relic_count': '0', 'relics': {OTHER: {'held': True}}})
        self.apply(run, {'relics': {'ids': [], 'icons': [], 'count': 0.0, 'source': 'held_bar'}})
        self.assertIs(type(run.state['relic_count']), float)
        self.assertEqual(run.state['relic_count'], 0.0)
        self.assertEqual(run.held_relic_ids(), [])

    def test_summary_counts_only_qualified_presence_and_retains_unknown_raw_flags(self):
        # Section122 intentionally replaces the old non-bool truthiness claim.
        # Boolean controls and the next method's missing-default contract stay.
        for value in ('yes', None, [], [1], {}, {'public': 1}, False, True, 0, 1):
            with self.subTest(value=value):
                run, raw = self.load({'operators': {'mechanist': {'present': value}}})
                text = self.view_unchanged(run, raw, run.summary)
                self.assertIn(f'当前已识别 {int(value is True)} /', text)
                if type(value) is not bool:self.assertIn('在场状态未确认', text)
                self.assertEqual(native(run.state['operators']['mechanist']['present']), native(value))

    def test_missing_presence_keeps_original_default_present_member(self):
        run, raw = self.load({'operators': {'mechanist': {}}})
        text = self.view_unchanged(run, raw, run.summary)
        self.assertIn('当前已识别 1 /', text)
        self.assertNotIn('present', run.state['operators']['mechanist'])

    def test_invalid_counter_proof_id_stays_history_without_rewrite_or_zero(self):
        for identity in ([], {}):
            with self.subTest(identity=identity):
                record = {'value': 1, 'captured_at': 0, 'source': 'held_card_counter',
                          'counter_evidence': {'id': identity}}
                run, raw = self.load({'resources': {'public_counter': record}})
                text = self.view_unchanged(run, raw, run.summary)
                self.assertIn('public_counter 1', text)
                self.assertIn('历史值，当前层数待确认', text)
                self.assertEqual(self.view_unchanged(run, raw, run.calculation_resources), {})
                self.assertEqual(native(run.state['resources']['public_counter']), native(record))

    def test_unknown_safe_counter_identity_remains_unavailable(self):
        for identity in ('unknown-public-id', None, False, 1, 0.0):
            with self.subTest(identity=identity):
                record = {'value': 1, 'source': 'held_card_counter', 'counter_evidence': {'id': identity}}
                before = native(record)
                self.assertIs(valid_counter_resource('public_counter', record), False)
                self.assertEqual(native(record), before)

    def test_every_verified_counter_still_uses_its_original_proof_and_bounds(self):
        for rid, (key, _, maximum) in COUNTER_BINDINGS.items():
            for value in (0, 1, maximum):
                with self.subTest(rid=rid, value=value):
                    proof = self.proof(rid, value);before = native(proof)
                    resource = counter_resources([proof])[key]
                    self.assertIs(valid_counter_resource(key, resource), True)
                    self.assertEqual(native(proof), before)
                    self.assertIs(type(resource['value']), int)
                    self.assertEqual(resource['value'], value)

    def test_known_counter_with_unusable_provenance_is_historical_without_edits(self):
        for source in (None, [], 1):
            with self.subTest(source=source):
                record = counter_resources([self.proof()])['altar_stacks']
                record['counter_evidence']['source'] = source
                record['captured_at'] = 0
                run, raw = self.load({'relics': {ALTAR: {'held': True}},
                                      'resources': {'altar_stacks': record}})
                text = self.view_unchanged(run, raw, run.summary)
                self.assertIn('圆石祭坛层数 1', text)
                self.assertIn('历史值，当前层数待确认', text)
                self.assertEqual(self.view_unchanged(run, raw, run.calculation_resources), {})
                self.assertEqual(native(run.state['resources']['altar_stacks']), native(record))

    def test_invalid_value_or_title_keeps_original_unavailable_short_circuit(self):
        for source in (None, [], 1):
            for change in ({'value': True}, {'value': None}, {'title': 'public-unrecognized-counter-title'}):
                with self.subTest(source=source, change=change):
                    record = counter_resources([self.proof()])['altar_stacks']
                    record['counter_evidence'].update(change)
                    record['counter_evidence']['source'] = source
                    before = native(record)
                    self.assertIs(valid_counter_resource('altar_stacks', record), False)
                    self.assertEqual(native(record), before)

    def test_fresh_verified_counter_can_replace_saved_bad_proof(self):
        bad = {'value': 1, 'captured_at': 0, 'source': 'held_card_counter',
               'counter_evidence': {'id': []}}
        run, raw = self.load({'resources': {'altar_stacks': bad}})
        self.assertEqual(self.view_unchanged(run, raw, run.calculation_resources), {})
        resource = counter_resources([self.proof()])
        self.apply(run, {'relics': {'ids': [ALTAR], 'count': None, 'icons': [], 'source': 'held_card'},
                         'resources': resource})
        self.assertEqual(run.calculation_resources()['altar_stacks']['value'], 1)
        self.assertEqual(RunState(self.file).calculation_resources()['altar_stacks']['value'], 1)

    def test_healthy_positive_buff_name_and_duplicate_labels_stay_exact(self):
        name = mechanics()['char_buffs'][SNACK]['name']
        self.assertEqual(self.label(self.member()), name)
        self.assertEqual(self.label(self.member(char_buff_ids=[SNACK, SNACK])), name+'、'+name)

    def test_complete_and_incomplete_empty_lists_keep_distinct_confirmation(self):
        self.assertEqual(self.label(self.member(char_buff_ids=[], char_buffs_complete=True)), '已核对：无个人强化')
        self.assertEqual(self.label(self.member(char_buff_ids=[], char_buffs_complete=False)),
                         '个人强化归属尚未确认；不会根据持有藏品推断')

    def test_healthy_pending_notice_preserves_the_original_positive_prefix(self):
        name = mechanics()['char_buffs'][SNACK]['name'];pending = mechanics()['char_buffs'][COOKIE]['name']
        self.assertEqual(self.label(self.member(char_buff_pending_ids=[COOKIE])),
                         '已确认：'+name+'；'+pending+'归属待更新：本局藏品或进阶情况已变化，旧的未领取结论已失效。')

    def test_inactive_scope_does_not_consume_invalid_unused_buff_metadata(self):
        value = self.member(scope='account', char_buff_ids=None, char_buff_pending_ids=[UNKNOWN])
        self.assertEqual(self.label(value), '个人强化归属尚未确认；不会根据持有藏品推断')

    def test_unknown_positive_is_displayed_unusable_and_raw_evidence_is_kept(self):
        member = self.member(char_buff_ids=[UNKNOWN])
        text = self.label(member)
        self.assertIn(UNKNOWN, text);self.assertIn('暂不可确认', text)
        self.assertNotIn('已确认', text);self.assertNotIn('已核对', text)
        self.assertEqual(member['char_buff_ids'], [UNKNOWN])

    def test_unknown_pending_does_not_call_an_incompatible_record_confirmed(self):
        member = self.member(char_buff_pending_ids=[UNKNOWN])
        text = self.label(member)
        self.assertIn(UNKNOWN, text);self.assertIn('暂不可确认', text)
        self.assertNotIn('已确认', text)
        self.assertEqual(member['char_buff_ids'], [SNACK])
        self.assertEqual(member['char_buff_pending_ids'], [UNKNOWN])

    def test_mixed_unknown_list_is_not_silently_filtered_into_valid_calculation(self):
        member = self.member(char_buff_ids=[SNACK, UNKNOWN])
        self.label(member)
        args = {'operator': 'mechanist', 'skill': 3,
                'char_buff_ids': member['char_buff_ids'], 'char_buffs_complete': False}
        original = native(args)
        with self.assertRaisesRegex(ValueError, '未知干员定向强化'):
            calculate_damage(args)
        self.assertEqual(native(args), original)

    def test_unknown_pending_keeps_original_numerical_api_error(self):
        member = self.member(char_buff_pending_ids=[UNKNOWN]);self.label(member)
        args = {'operator': 'mechanist', 'skill': 3, 'char_buff_ids': [SNACK],
                'char_buffs_complete': False, 'char_buff_pending_ids': member['char_buff_pending_ids']}
        original = native(args)
        with self.assertRaisesRegex(ValueError, '待更新的个人强化'):
            calculate_damage(args)
        self.assertEqual(native(args), original)

    def test_known_wrong_profession_still_uses_existing_numerical_rejection(self):
        member = self.member(char_buff_ids=['rogue_6_from_relic_5'])
        self.assertEqual(self.label(member), mechanics()['char_buffs']['rogue_6_from_relic_5']['name'])
        with self.assertRaisesRegex(ValueError, '职业不符'):
            calculate_damage({'operator': 'mechanist', 'skill': 3, 'char_buff_ids': member['char_buff_ids']})

    def test_healthy_snack_cost_and_independent_recruitment_fields_are_unchanged(self):
        member = self.member();self.label(member)
        self.assertEqual(member['recruitment_kind'], 'non_emergency')
        args = {'operator': 'mechanist', 'skill': 3, 'char_buff_ids': member['char_buff_ids'],
                'char_buffs_complete': False, 'recruitment_kind': member['recruitment_kind']}
        original = native(args)
        self.assertEqual(calculate_damage(args)['estimate']['skill']['sp_cost'], 28)
        self.assertEqual(native(args), original)


if __name__ == '__main__':
    unittest.main()

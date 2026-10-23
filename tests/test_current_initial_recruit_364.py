"""Necessary source/association checks; prepare only until formal integration."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest

from rouge import current_initial_recruit as model


def clone(root):
    manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
    for name in (model.MANIFEST, *manifest['files']):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((model.ROOT / name).read_bytes())


class CurrentInitialRecruit364Tests(unittest.TestCase):
    def test_all_exact_associations_and_four_part_monthly_identity(self):
        packet = model.packet()
        self.assertIsNotNone(packet)
        data = packet['data']
        source = model.version.packet()['current']['details']
        initial = {r['id']: r for r in data['initial']}
        groups = {r['id']: r for r in data['groups']}
        self.assertEqual(len(initial), 21)
        self.assertEqual(len(groups), 14)
        self.assertEqual(sum(len(r['group_ids']) for r in initial.values()), 106)
        for original in source['init']:
            row = initial[model.initial_key(original)]
            self.assertEqual(row['original'], original)
            self.assertEqual(row['group_ids'], original['initialRecruitGroup'])
            for group in row['group_ids']:
                self.assertIn(row['id'], groups[group]['initial_ids'])
        for key, group in groups.items():
            self.assertEqual(group['original'], source['recruitGrps'][key])
            self.assertEqual(set(group['initial_ids']), {r['id'] for r in initial.values() if key in r['group_ids']})
        monthly = [r for r in initial.values() if r['scope'] == 'monthly']
        self.assertEqual(len({r['id'] for r in monthly}), 4)
        self.assertEqual({r['original']['modeGrade'] for r in monthly}, {0})
        self.assertEqual(len({r['original']['predefinedId'] for r in monthly}), 4)
        self.assertTrue(data['raw_group_definitions_equal_previous_baseline'])
        self.assertFalse(data['run_updated'])

    def test_default_filters_and_unassociated_groups_never_invent_future_months(self):
        self.assertEqual([len(model.catalog('initial', scope)['rows']) for scope in ('all', 'normal', 'monthly')], [21, 17, 4])
        self.assertEqual([len(model.catalog('group', scope)['rows']) for scope in ('all', 'normal', 'monthly', 'unlinked')], [14, 6, 4, 4])
        self.assertIsNone(model.catalog('initial', 'unlinked'))
        self.assertEqual(len(model.catalog('initial', 'monthly', '2026年10月')['rows']), 1)
        self.assertEqual(len(model.catalog('group', 'normal', '随心所欲')['rows']), 1)
        rows = model.catalog('group', 'unlinked')['rows']
        self.assertEqual({r['id'] for r in rows}, {'recruit_group_m5', 'recruit_group_m6', 'recruit_group_m7', 'recruit_group_m8'})
        for row in rows:
            self.assertEqual(row['initial_ids'], [])
            self.assertNotIn('月', row['label'])
            self.assertIsNone(row['actual_unlocked'])
            self.assertIsNone(row['guaranteed_temporary_rarity_reference'])

    def test_specific_five_star_and_generic_four_star_have_separate_originals(self):
        result = model.detail('group', model.RANDOM)
        row = result['row']
        self.assertEqual(row['guaranteed_temporary_rarity_reference'], 5)
        self.assertEqual(row['ticket_count_reference'], 3)
        self.assertEqual(row['slots_reference'][0]['guaranteed_temporary_rarity'], 5)
        self.assertIsNone(row['slots_reference'][0]['professions'])
        self.assertEqual(row['slots_reference'][1]['professions'], ['先锋', '近卫', '重装', '特种'])
        self.assertEqual(row['slots_reference'][2]['professions'], ['狙击', '术师', '医疗', '辅助'])
        self.assertIn('5星临时招募', model.plain_html(result['documents']['theme_rows_html']['随心所欲']))
        self.assertIn('4星临时招募', model.plain_html(result['documents']['generic_rows_html']['随心所欲']))
        self.assertFalse(result['data']['source_scope']['generic_four_star_applied_to_current_theme'])
        self.assertFalse(result['data']['source_scope']['current_server_verified'])
        text = model.player_text(result)
        self.assertIn('不等于“三张职业都不同”', text)
        self.assertIn('第一张的完整职业', text)
        self.assertIn('通用“集成战略”修订440806', text)

    def test_fixed_and_support_groups_do_not_inherit_random_guarantees(self):
        for key, (name, professions) in model.FIXED.items():
            result = model.detail('group', key)
            row = result['row']
            self.assertEqual(row['original']['name'], name)
            self.assertEqual([v['professions'][0] for v in row['slots_reference']], professions)
            self.assertTrue(all(v['order_verified'] is False for v in row['slots_reference']))
            self.assertIsNone(row['guaranteed_temporary_rarity_reference'])
            self.assertIsNone(model.detail('group', key, True))
        for index in range(1, 9):
            result = model.detail('group', 'recruit_group_m' + str(index))
            self.assertEqual(result['row']['ticket_count_reference'], 2)
            self.assertEqual(result['row']['slots_reference'], [])
            self.assertIsNone(result['row']['guaranteed_temporary_rarity_reference'])
            self.assertIsNone(result['row']['actual_candidates'])
            self.assertIn('不能套入5星保证', model.player_text(result))

    def test_manual_unlock_description_never_claims_account_eligibility(self):
        for value in (None, False, True):
            result = model.detail('group', model.RANDOM, value)
            self.assertIs(result['listed_unlock_description_matches'], value)
            self.assertIs(result['other_exploration_declared'], value)
            for key in ('actual_unlocked', 'actual_eligible', 'actual_menu', 'actual_recruits'):
                self.assertIsNone(result[key])
            self.assertFalse(result['run_updated'])
        for value in (0, 1, '是', [], {}):
            self.assertIsNone(model.detail('group', model.RANDOM, value))
        first = model.catalog()['rows'][0]['id']
        self.assertIsNone(model.detail('initial', first, True))
        self.assertEqual(model.locate('initial', first), {'kind': 'initial', 'key': first})
        for category, key in (('groups', model.RANDOM), ('initial', '常规行动'), ('initial', True), (True, first)):
            self.assertIsNone(model.locate(category, key))

    def test_explicit_forward_reverse_links_and_invalid_targets(self):
        data = model.packet()['data']
        normal_key = next(r['id'] for r in data['initial'] if r['scope'] == 'normal')
        normal = model.detail('initial', normal_key)
        self.assertEqual([r['target']['key'] for r in normal['related']], normal['row']['group_ids'])
        key = next(r['id'] for r in data['initial'] if r['scope'] == 'monthly')
        result = model.detail('initial', key)
        self.assertEqual(len(result['related']), 1)
        group = result['related'][0]['target']
        reverse = model.detail(group['kind'], group['key'])
        self.assertEqual([r['target'] for r in reverse['related']], [{'kind': 'initial', 'key': key}])
        for kind, key in (('other', key), ('initial', 'MONTH_TEAM'), ('group', '支援作战'), (True, key)):
            self.assertIsNone(model.detail(kind, key))
        for kind, scope, query in ((True, 'all', ''), ('initial', True, ''), ('group', 'all', [])):
            self.assertIsNone(model.catalog(kind, scope, query))

    def test_each_pinned_source_mutation_fails_closed_then_recovers(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            clone(root)
            with patch.object(model, 'ROOT', root):
                self.assertIsNotNone(model.packet())
                for name in (model.MANIFEST, *json.loads((root / model.MANIFEST).read_bytes())['files']):
                    path = root / name
                    original = path.read_bytes()
                    path.write_bytes(original + b'x')
                    self.assertIsNone(model.packet(), name)
                    self.assertIsNone(model.detail('group', model.RANDOM), name)
                    path.write_bytes(original)
                    self.assertIsNotNone(model.packet(), name)
        with patch.object(model.version, 'packet', return_value=None):
            self.assertIsNone(model.packet())

    def test_semantic_guards_and_independent_results(self):
        packet = model.packet()
        version = model.version.packet()
        for mutate in ('duplicate_pointer', 'unknown_group', 'same_initial_identity', 'four_star'):
            current = deepcopy(version['current'])
            if mutate == 'duplicate_pointer':
                current['details']['init'][0]['initialRecruitGroup'].append(current['details']['init'][0]['initialRecruitGroup'][0])
            elif mutate == 'unknown_group':
                current['details']['init'][0]['initialRecruitGroup'][0] = 'recruit_group_unseen'
            elif mutate == 'same_initial_identity':
                current['details']['init'][1] = deepcopy(current['details']['init'][0])
            else:
                current['details']['recruitGrps'][model.RANDOM]['desc'] = '三张随机的招募券，其中一张必定出现4星临时招募'
            with self.assertRaises(ValueError, msg=mutate):
                model.derive_data(current, version['baseline'], packet['documents'])
        first = model.detail('group', model.RANDOM)
        first['row']['slots_reference'][1]['professions'].clear()
        self.assertEqual(len(model.detail('group', model.RANDOM)['row']['slots_reference'][1]['professions']), 4)


if __name__ == '__main__':
    unittest.main()

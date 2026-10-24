from collections import Counter
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json, shutil, unittest

from rouge import current_enemy_stage_index as model
from rouge import current_battle_reference as battle
from scripts.build_current_enemy_stage_index_370 import build

ROOT = Path(__file__).resolve().parents[1]


class CurrentEnemyStageIndex370Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = model.packet()
        if cls.ref is None: raise AssertionError('Public source chain unavailable')

    def test_source_rebuild_is_byte_identical_and_all_original_references_have_unique_targets(self):
        blobs, counts = build(ROOT)
        for name, raw in blobs.items(): self.assertEqual((ROOT / name).read_bytes(), raw)
        current = battle.packet(); expected = set()
        for sid, stage in current['version']['current']['details']['stages'].items():
            level = current['inputs']['levels']['levels/' + stage['levelId'].lower() + '.json']
            for i, raw in enumerate(level['enemyDbRefs']):
                expected.add((sid, str(i)))
                row = model.locate(sid, str(i), reference=self.ref)
                self.assertEqual(row['binding_sha256'], model.digest(raw))
        got = [(r['stage_id'], r['enemy_key']) for r in self.ref['data']['rows']]
        self.assertEqual(len(got), len(set(got))); self.assertEqual(set(got), expected)
        self.assertEqual((counts['stage_configurations'], counts['exact_enemy_references']), (184, 2060))

    def test_all_category_branches_partition_references_without_forcing_unknown_to_normal(self):
        got = []
        for tier, _ in model.TIERS[1:]:
            got.extend((r['stage_id'], r['enemy_key']) for r in model.rows(tier=tier, reference=self.ref))
        expected = [(r['stage_id'], r['enemy_key']) for r in self.ref['data']['rows']]
        self.assertEqual(Counter(got), Counter(expected))
        unknown = model.rows(tier='UNKNOWN', reference=self.ref)
        self.assertEqual(len(unknown), 9)
        self.assertTrue(all(r['tier'] is None for r in unknown))
        self.assertTrue(any(r['name'] == '净浊之焰' for r in unknown))

    def test_not_counted_filter_is_flag_based_and_keeps_original_tier(self):
        rows = model.rows(scope='not_counted', reference=self.ref)
        self.assertEqual(len(rows), 10); self.assertTrue(all(r['not_counted'] is True for r in rows))
        self.assertEqual({r['tier'] for r in rows}, {'NORMAL', 'ELITE'})
        independent = [r for r in self.ref['data']['rows'] if r['use_db'] is False]
        self.assertEqual(len(independent), 95)
        self.assertTrue(any(r['tier'] == 'BOSS' for r in independent))
        self.assertTrue(all(r not in rows for r in independent))

    def test_chinese_search_and_intersecting_floor_type_category_filters(self):
        result = model.rows('  鸭爵  ', tier='ELITE', floor='floor1', kind='normal', reference=self.ref)
        self.assertTrue(result)
        self.assertTrue(all('鸭爵' in r['name'] and r['tier'] == 'ELITE' for r in result))
        self.assertTrue(all(self.ref['data']['stages'][r['stage_id']]['floor'] == 'floor1' for r in result))
        self.assertTrue(all(self.ref['data']['stages'][r['stage_id']]['play_kind'] == 'normal' for r in result))
        self.assertEqual(model.rows('不存在的测试敌人', reference=self.ref), [])
        for kwargs in ({'tier': 'common'}, {'scope': 'is_helper'}, {'floor': 'floor7'}, {'kind': 'madeup'}, {'query': None}):
            self.assertEqual(model.rows(reference=self.ref, **kwargs), [])

    def test_same_name_different_database_levels_stay_distinct(self):
        ducks = model.rows('鸭爵', reference=self.ref)
        self.assertGreater(len({r['database_level'] for r in ducks}), 1)
        self.assertEqual(len(ducks), len({(r['stage_id'], r['enemy_key']) for r in ducks}))
        for row in ducks[:3]:
            info = model.detail(row['stage_id'], row['enemy_key'], reference=self.ref)
            self.assertIn('不合并等级', model.player_text(info)); self.assertIsNone(info['expected_stats'])

    def test_same_stage_same_name_independent_configs_are_not_collapsed(self):
        rows = [r for r in model.rows('空植体', reference=self.ref) if r['stage_id'] == 'ro6_n_2_3']
        self.assertEqual(len(rows), 4); self.assertEqual(len({r['binding_sha256'] for r in rows}), 4)
        for row in rows:
            info = model.detail(row['stage_id'], row['enemy_key'], reference=self.ref)
            self.assertIn('本关也有多个同名记录', model.player_text(info))
            self.assertIn('本关独立配置', model.player_text(info))

    def test_exact_shop_boss_target_keeps_its_own_override(self):
        a = model.detail('ro6_t_6', '0', reference=self.ref)
        b = model.detail('ro6_t_7', '0', reference=self.ref)
        self.assertEqual(a['row']['enemy_id'], 'enemy_2153_shcan'); self.assertEqual(b['row']['enemy_id'], a['row']['enemy_id'])
        self.assertIn('attributes.maxHp', a['row']['enabled_override_paths'])
        self.assertNotIn('attributes.maxHp', b['row']['enabled_override_paths'])
        self.assertNotEqual(a['row']['binding_sha256'], b['row']['binding_sha256'])
        target = model.exact_target(a); self.assertEqual(target['stage_id'], 'ro6_t_6'); self.assertEqual(target['enemy_key'], '0')
        self.assertEqual(target['enemy']['raw_binding']['overwrittenData']['attributes']['maxHp']['m_value'], 60000)

    def test_forged_cross_stage_or_name_target_and_nonstring_key_are_refused(self):
        info = model.detail('ro6_t_6', '0', reference=self.ref)
        for key, value in [('stage_id', 'ro6_t_7'), ('name', '冒名'), ('enemy_key', 0), ('binding_sha256', '0' * 64)]:
            forged = deepcopy(info); forged['row'][key] = value
            self.assertIsNone(model.exact_target(forged))
        self.assertIsNone(model.locate('ro6_t_6', 0, reference=self.ref))
        self.assertIsNone(model.locate('ro6_t_6', True, reference=self.ref))
        self.assertIsNone(model.locate('no-stage', '0', reference=self.ref))

    def test_precise_images_are_reused_and_missing_images_stay_missing(self):
        current = battle.packet(); found = 0; missing = 0
        for sid, stage in current['version']['current']['details']['stages'].items():
            level = current['inputs']['levels']['levels/' + stage['levelId'].lower() + '.json']
            for enemy in battle.enemy_records(level, current):
                row = model.locate(sid, enemy['key'], reference=self.ref)
                self.assertEqual(row['portrait'], enemy['portrait'])
                if row['portrait'] is None:
                    missing += 1; self.assertIn('不借用同名图', model.player_text(model.detail(sid, enemy['key'], reference=self.ref)))
                else: found += 1
        self.assertEqual((found, missing), (2047, 13))

    def test_actual_tampered_public_data_or_manifest_and_dependency_loss_clear_packet(self):
        manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in (model.MANIFEST, *manifest['files']):
                out = root / name; out.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / name, out)
            with patch.object(model, 'ROOT', root):
                self.assertIsNotNone(model.packet())
                source = root / model.DATA; raw = source.read_bytes(); source.write_bytes(raw + b' ')
                self.assertIsNone(model.packet()); source.write_bytes(raw)
                source = root / model.MANIFEST; source.write_bytes(source.read_bytes() + b' ')
                self.assertIsNone(model.packet())
        with patch.object(battle, 'packet', return_value=None): self.assertIsNone(model.packet())

    def test_disabled_placeholders_are_not_overrides_or_classification(self):
        raw = {'levelType': {'m_defined': False, 'm_value': 'NORMAL'},
               'attributes': {'maxHp': {'m_defined': True, 'm_value': 1}, 'atk': {'m_defined': False, 'm_value': 0}}}
        self.assertEqual(model.enabled_paths(raw), ['attributes.maxHp'])
        rows = [r for r in model.rows('空植体', tier='UNKNOWN', reference=self.ref) if r['stage_id'] == 'ro6_n_2_3']
        self.assertEqual(len(rows), 4)
        self.assertTrue(all('levelType' not in r['enabled_override_paths'] for r in rows))

    def test_player_text_and_scope_never_claim_actual_spawn_counts_or_final_panel(self):
        info = model.detail('ro6_t_6', '0', reference=self.ref); text = model.player_text(info)
        for word in ('关卡：', '层数：', '作战来源：', '不等于实际出场', '不能把检索结果数当敌人数'):
            self.assertIn(word, text)
        for word in ('enemyDbRefs', 'enemy_2153', 'm_defined', 'useDb', 'maxHp', '60000'):
            self.assertNotIn(word, text)
        self.assertIsNone(info['actual_spawned']); self.assertIsNone(info['actual_count'])
        self.assertFalse(info['actual_server_verified']); self.assertFalse(info['run_updated'])


if __name__ == '__main__': unittest.main()

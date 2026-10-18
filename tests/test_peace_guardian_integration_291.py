"""UNEXECUTED DRAFT: exact MOVE information, independent positions and previews.

Promote source packets and archive the pinned original290 planning before running.
The App guard tests below use a public in-memory holder, not an actual window.
Separate native isolated Windows acceptance remains required.
"""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import event_planning, peace_guardian_results, node_catalog as catalog
from rouge import choice_recruitment_results
from rouge import app as app_module
from rouge.node_catalog_view import NodeCatalogPanel, event_details_text
from rouge.player_node_information import node_information_text
from rouge.resident_location_references import resident_location_references
from tests.test_readable_map_047 import graph as existing_public_graph


ROOT = Path(__file__).resolve().parents[1]
EVENT = 'community_group_019'
SCENE = EVENT + ':scene:1'
CHOICE = SCENE + ':choice:0'
MARK = SCENE + ':choice:1'
BASELINE = 'verification/sections/291-preparation/before-integration/rouge/event_planning.py'
BASELINE_SHA = 'f7455c11558d828f4a79ca7a82db1660c143597b927d6d2aa9ef55274ff3ff01'


def previous_planning():
    raw = (ROOT / BASELINE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASELINE_SHA:
        raise AssertionError('Archive the exact original290 planning before formal291 checks.')
    module = types.ModuleType('rouge._planning_before291_comparison')
    module.__package__ = 'rouge'
    module.__file__ = str(ROOT / 'rouge/event_planning.py')
    exec(compile(raw, str(ROOT / BASELINE), 'exec'), module.__dict__)
    return module


def event_entry(identity=EVENT, **extra):
    record = next(row for row in catalog.all_events(include_indirect=True)['rows'] if row['id'] == identity)
    return {'kind': 'event', 'record': record, **extra}


def move_row(context=None):
    return next(row for row in event_planning.choice_eligibility(EVENT, SCENE, context)['rows'] if row['choice_key'] == CHOICE)


def graph():
    source = existing_public_graph()
    source['nodes'][0]['observed_type'] = '“居民”据点'
    source['nodes'][1]['remembered_type'] = '“居民”据点'
    return source


def restore_prior_row(row):
    reference = row.pop('movement_result_reference', None)
    if reference is not None:
        if row['choice_key'] != CHOICE:
            raise AssertionError('Only the exact MOVE may have this annotation')
        row['unparsed_condition_text'] = row['conditional_text']
    return row


@contextmanager
def isolated_public_source():
    model = peace_guardian_results
    manifest = json.loads((ROOT / model.MANIFEST).read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='rouge-291-public-source-') as directory:
        clone = Path(directory)
        for relative in (model.MANIFEST, *manifest['files']):
            output = clone / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes((ROOT / relative).read_bytes())
        html = clone / next(relative for relative in manifest['files'] if relative.endswith('440271.html'))
        with patch.object(model, 'ROOT', clone):
            yield html


class PeaceGuardianPlanning291Tests(unittest.TestCase):
    def test_all_fixed_events_and_contexts_keep_status_checks_ids_and_non_target_fields(self):
        previous = previous_planning()
        # Verify the exact section298 addition before comparing all pre291 fields.
        # Keep the actual source active; no source/helper mocking or status copying.
        rule_raw = (ROOT / 'rouge/data/event-node-requirements.json').read_bytes()
        self.assertEqual(hashlib.sha256(rule_raw).hexdigest(),
                         'f11c6d83a048ffdea14cbccdd1506ff02c3ef35a1cf94f107e30845b2d1deab3')
        rules = json.loads(rule_raw)
        expected_forbidden = {'community_group_024':[1,5,6], 'community_group_025':[1,6],
                              'community_group_027':[1,2,6], 'community_group_028':[1,2,6],
                              'community_group_029':[1,2,6], 'community_group_037':[1]}
        self.assertEqual({identity:rule['documented_excluded_main_floors']
                          for identity,rule in rules['events'].items()}, expected_forbidden)
        for context in ({}, {'floor': 2, 'node_type': '不期而遇', 'entry_mode': 'content', 'resources': {'hope': 20}},
                        {'floor': 1, 'difficulty': 3, 'node_type': '作战', 'entry_mode': 'natural'}):
            for event in catalog._data()['events']:
                for scene in event['scenes']:
                    before = previous.choice_eligibility(event['id'], scene['key'], context)
                    after = event_planning.choice_eligibility(event['id'], scene['key'], context)
                    for row in after['rows']:
                        added = [check for check in row['checks']
                                 if check['key']=='documented_node_natural_main_floor']
                        applies = (event['id'] in expected_forbidden
                                   and context.get('entry_mode')=='natural'
                                   and context.get('floor') is not None
                                   and not context.get('special_region',False))
                        self.assertEqual(len(added), 1 if applies else 0)
                        if applies:
                            rule = rules['events'][event['id']]
                            self.assertEqual(added[0], {
                                'key':'documented_node_natural_main_floor',
                                'kind':'source_node_floor_requirement',
                                'matches':context['floor'] not in expected_forbidden[event['id']],
                                'source_text':rule['source_text'], 'context_applicable':True,
                                'documented_excluded_main_floors':expected_forbidden[event['id']],
                                'source_revision':rules['source']['main']['revision'],
                                'actual_server_eligible':None})
                            row['checks'] = [check for check in row['checks']
                                if check['key']!='documented_node_natural_main_floor']
                            matches = [check['matches'] for check in row['checks']]
                            row['status'] = ('excluded' if False in matches else
                                'unknown' if None in matches or not matches else 'matched')
                        restore_prior_row(row)
                    self.assertEqual(after, before, (event['id'], scene['key'], context))

    def test_only_MOVE_result_is_reclassified_VISION_keeps_independent_original(self):
        previous = previous_planning().choice_eligibility(EVENT, SCENE)
        result = event_planning.choice_eligibility(EVENT, SCENE)
        move, mark = result['rows']
        self.assertEqual(move['choice_key'], CHOICE)
        self.assertEqual(mark['choice_key'], MARK)
        self.assertIsNone(move['unparsed_condition_text'])
        self.assertEqual(move['conditional_text'], '若已完成当前层的【“居民”据点】作战则不会移动')
        reference = move['movement_result_reference']
        self.assertEqual(reference['annotation_role'], 'selection_result')
        self.assertFalse(reference['source_scene_link_verified'])
        self.assertFalse(reference['completion_exception_reference']['negation_implies_successful_movement_verified'])
        self.assertIsNone(reference['actual_moved'])
        self.assertNotIn('movement_result_reference', mark)
        self.assertEqual(mark, previous['rows'][1])

    def test_other_ten_unparsed_texts_and_their_qualification_are_preserved(self):
        previous = previous_planning()
        remaining = []
        for event in catalog._data()['events']:
            for scene in event['scenes']:
                before = previous.choice_eligibility(event['id'], scene['key'])
                after = event_planning.choice_eligibility(event['id'], scene['key'])
                for old, new in zip(before['rows'], after['rows']):
                    if old['choice_key'] != CHOICE and old['unparsed_condition_text']:
                        self.assertEqual(new, old)
                        remaining.append(new['choice_key'])
        self.assertEqual(len(remaining), 10)

    def test_resources_and_context_are_unchanged_and_no_move_cost_or_target_is_added(self):
        previous = previous_planning()
        context = {'resources': {'hope': 20, 'ap': 6}, 'entry_mode': 'content', 'floor': 2}
        saved = deepcopy(context)
        before = previous.choice_resources(EVENT, SCENE, context)
        after = event_planning.choice_resources(EVENT, SCENE, context)
        for row in after['rows']:
            restore_prior_row(row['choice_eligibility'])
        self.assertEqual(after, before)
        self.assertEqual(context, saved)

    def test_player_text_keeps_one_way_unknowns_and_marking_option_separate(self):
        text = node_information_text(event_entry())
        for expected in ('资料记载：若已完成当前层的【“居民”据点】作战则不会移动。',
                         '本层是否已完成、实际目的地和是否移动：尚未确认。',
                         '未完成不代表一定移动', '从长计议', '仅标记地图上最近的“居民”据点，暂不前往'):
            self.assertIn(expected, text)
        for forbidden in ('https://', 'choice_ro6_task1_', 'current_floor_resident_post', '未完成就一定移动'):
            self.assertNotIn(forbidden, text)
        technical = event_details_text(EVENT)
        self.assertIn('选择后移动例外说明（原文）', technical)
        self.assertIn('427904', technical)
        self.assertIn('440271', technical)

    def test_source_valid_invalid_restored_keeps_original_conditional_and_unknown_actuals(self):
        with isolated_public_source() as html:
            raw = html.read_bytes()
            self.assertEqual(move_row()['movement_result_reference']['status'], 'documented_reference')
            html.write_bytes(raw + b' ')
            row = move_row()
            self.assertEqual(row['movement_result_reference']['status'], 'unknown')
            self.assertEqual(row['unparsed_condition_text'], row['conditional_text'])
            self.assertIn('补充移动资料暂时无法核对', node_information_text(event_entry()))
            self.assertIn('补充移动来源未通过核对', event_details_text(EVENT))
            self.assertIsNone(row['movement_result_reference']['actual_current_floor_completion'])
            html.write_bytes(raw)
            self.assertEqual(move_row()['movement_result_reference']['status'], 'documented_reference')

    def test_history_does_not_supply_current_completion_or_position(self):
        context = {'resources': {'hope': 20, 'gold': 51}}
        saved = deepcopy(context)
        text = node_information_text(event_entry(history_read=True), context=context)
        self.assertIn('历史', text)
        self.assertIn('本层是否已完成、实际目的地和是否移动：尚未确认', text)
        self.assertEqual(context, saved)

    def test_known_direct_promotion_term_does_not_rewrite290_source_or_claim_cultivation(self):
        before = choice_recruitment_results.choice_reference('community_group_018',
            catalog._scene('community_group_018', 'community_group_018:scene:0')['choices'][1],
            scene_key='community_group_018:scene:0')
        text = node_information_text(event_entry('community_group_018'))
        self.assertIn('直升：首次招募即已进阶。', text)
        self.assertIn('实际等级、技能及模组等培养信息仍待读取确认', text)
        after = choice_recruitment_results.choice_reference('community_group_018',
            catalog._scene('community_group_018', 'community_group_018:scene:0')['choices'][1],
            scene_key='community_group_018:scene:0')
        self.assertEqual(before, after)
        self.assertIsNone(after['actual_cultivation'])
        self.assertIsNone(after['recruitment_cost'])
        self.assertNotIn('精二满级', text)
        self.assertNotIn('免费招募', text)


class PeaceGuardianPanel291Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = NodeCatalogPanel()
        self.addCleanup(self.panel.close)
        self.panel.set_map_context(graph(), {'floor': 2}, epoch='public-run', historical=False)
        self.select_event(EVENT)

    def select_event(self, identity):
        self.panel.list.setCurrentRow(next(index for index, entry in enumerate(self.panel.entries)
            if entry['kind'] == 'event' and entry['record']['id'] == identity))

    def test_independent_position_and_two_stage_lists_default_to_no_selection(self):
        panel = self.panel
        self.assertFalse(panel.resident_location.isHidden())
        self.assertEqual(panel.resident_location.count(), 3)
        self.assertIsNone(panel.resident_location.currentData())
        self.assertFalse(panel.resident_map_button.isEnabled())
        self.assertEqual({panel.resident_stage.itemData(i) for i in range(1, panel.resident_stage.count())},
                         {'ro6_t_10', 'ro6_t_11'})
        self.assertIsNone(panel.resident_stage.currentData())
        self.assertFalse(panel.resident_stage_button.isEnabled())
        self.assertEqual(panel.event_stage.count(), 0)
        self.assertEqual(panel.map_location.count(), 0)
        self.assertIn('“守卫和平！”', panel.resident_reference_label.text())

    def test_selecting_position_emits_copy_without_changing_event_reading_or_binding_it(self):
        panel = self.panel; key = panel.detail_key
        calls = []; panel.mapNodeSelected.connect(lambda *args: calls.append(args))
        panel.resident_location.setCurrentIndex(1)
        saved = deepcopy(panel.resident_location.currentData())
        panel.resident_map_button.click()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], '0,2')
        self.assertEqual(calls[0][1], saved)
        calls[0][1]['grid']['rows'] = 99
        self.assertEqual(panel.resident_location.currentData(), saved)
        self.assertEqual(panel.detail_key, key)
        self.assertIsNone(panel.dossier)

    def test_each_fixed_stage_preview_is_manual_and_not_added_to_event_outcomes(self):
        panel = self.panel; calls = []; panel.stageSelected.connect(calls.append)
        self.assertEqual(event_planning.event_battle_links(EVENT)['rows'], [])
        for identity in ('ro6_t_10', 'ro6_t_11'):
            panel.resident_stage.setCurrentIndex(panel.resident_stage.findData(identity))
            panel.resident_stage_button.click()
        self.assertEqual(calls, ['ro6_t_10', 'ro6_t_11'])
        self.assertEqual(event_planning.event_battle_links(EVENT)['rows'], [])
        self.assertIsNone(move_row()['movement_result_reference']['actual_battle_triggered'])

    def test_source_failure_hides_clears_and_disables_both_lists_then_restores_placeholders(self):
        panel = self.panel
        with isolated_public_source() as html:
            raw = html.read_bytes()
            panel.refresh()
            panel.resident_location.setCurrentIndex(1)
            panel.resident_stage.setCurrentIndex(1)
            html.write_bytes(raw + b' ')
            panel.refresh()
            for widget in (panel.resident_reference_label, panel.resident_location, panel.resident_map_button,
                           panel.resident_stage, panel.resident_stage_button):
                self.assertTrue(widget.isHidden())
            self.assertEqual(panel.resident_location.count(), 0)
            self.assertEqual(panel.resident_stage.count(), 0)
            self.assertEqual(panel.resident_reference_label.text(), '')
            self.assertFalse(panel.resident_map_button.isEnabled())
            self.assertFalse(panel.resident_stage_button.isEnabled())
            html.write_bytes(raw)
            panel.refresh()
            self.assertIsNone(panel.resident_location.currentData())
            self.assertIsNone(panel.resident_stage.currentData())

    def test_latest_panel_context_rejects_a_stale_position_before_emitting(self):
        panel = self.panel; calls = []; panel.mapNodeSelected.connect(lambda *args: calls.append(args))
        panel.resident_location.setCurrentIndex(1)
        latest = graph(); latest['nodes'][0]['col'] = 4
        panel.map_context = (latest, {'floor': 2}, 'public-run', False)
        panel.resident_map_button.click()
        self.assertEqual(calls, [])
        self.assertIn('链接已过期', panel.status.text())
        self.assertIsNone(panel.resident_location.currentData())

    def test_historical_labels_and_invalid_historical_source_type_do_not_get_coerced(self):
        panel = self.panel
        panel.set_map_context(graph(), {}, epoch='public-run', historical=True)
        self.assertIn('记录时读到的据点', panel.resident_location.itemText(1))
        self.assertIn('历史地图记录', panel.resident_location.itemText(1))
        panel.set_map_context(graph(), {}, epoch='public-run', historical=1)
        self.assertEqual(panel.resident_location.count(), 1)
        self.assertIsNone(panel.resident_location.currentData())
        self.assertFalse(panel.resident_map_button.isEnabled())
        self.assertEqual(panel.resident_stage.count(), 3)

    def test_unrelated_event_hides_and_clears_new_widgets_without_changing_old_navigation(self):
        panel = self.panel; panel.resident_location.setCurrentIndex(1)
        identity = next(entry['record']['id'] for entry in panel.entries if entry['title'] == '思乡心切')
        self.select_event(identity)
        self.assertTrue(panel.resident_location.isHidden())
        self.assertEqual(panel.resident_location.count(), 0)
        self.assertEqual(panel.event_stage.currentData(), 'ro6_t_1')

    def test_refresh_keeps_exact_choices_tab_selection_and_nonzero_scroll(self):
        panel = self.panel; panel.resize(1000, 480); panel.show(); self.qt.processEvents()
        panel.resident_location.setCurrentIndex(2)
        panel.resident_stage.setCurrentIndex(2)
        binding = deepcopy(panel.resident_location.currentData()); stage = panel.resident_stage.currentData()
        panel.reading_tabs.setCurrentWidget(panel.detail)
        cursor = panel.detail.textCursor(); cursor.setPosition(3)
        cursor.setPosition(18, QTextCursor.MoveMode.KeepAnchor); panel.detail.setTextCursor(cursor)
        self.assertGreater(panel.detail.verticalScrollBar().maximum(), 0)
        panel.detail.verticalScrollBar().setValue(min(9, panel.detail.verticalScrollBar().maximum()))
        selected = panel.detail.textCursor().selectedText(); scroll = panel.detail.verticalScrollBar().value()
        key = panel.detail_key; panel.refresh(); self.qt.processEvents()
        self.assertEqual(panel.detail_key, key)
        self.assertEqual(panel.resident_location.currentData(), binding)
        self.assertEqual(panel.resident_stage.currentData(), stage)
        self.assertIs(panel.reading_tabs.currentWidget(), panel.detail)
        self.assertEqual(panel.detail.textCursor().selectedText(), selected)
        self.assertEqual(panel.detail.verticalScrollBar().value(), scroll)


class PeaceGuardianAppGuard291Tests(unittest.TestCase):
    def holder(self, source, historical=False):
        selected = []; status = []; tabs = []
        map_view = types.SimpleNamespace(graph=deepcopy(source), historical=historical,
            select_node=lambda node_id, **_kwargs:selected.append(node_id))
        holder = types.SimpleNamespace(map_view=map_view, run=types.SimpleNamespace(state={'id': 'public-run'}),
            node_catalog=types.SimpleNamespace(status=types.SimpleNamespace(setText=status.append)),
            exploration_map_tab='assistant-map-tab', centralWidget=lambda: types.SimpleNamespace(setCurrentWidget=tabs.append))
        return holder, selected, status, tabs

    def test_latest_App_map_rejects_duplicates_changed_roles_and_grid_even_if_old_six_fields_match(self):
        original = graph()
        binding = resident_location_references(original, epoch='public-run', historical=False)['rows'][0]['binding']
        variants = []
        changed = deepcopy(original); changed['nodes'][2]['id'] = '0,2'; variants.append(changed)
        changed = deepcopy(original); changed['nodes'][0].update(observed_type='林间空地', remembered_type='“居民”据点'); variants.append(changed)
        changed = deepcopy(original); changed['grid']['cols'] += 1; variants.append(changed)
        for changed in variants:
            holder, selected, status, tabs = self.holder(changed)
            app_module.MainWindow.show_catalog_map_node(holder, '0,2', deepcopy(binding))
            self.assertEqual(selected, [])
            self.assertEqual(tabs, [])
            self.assertIn('链接已过期', status[-1])

    def test_same_position_and_history_context_emit_only_after_second_guard(self):
        source = graph()
        binding = resident_location_references(source, epoch='public-run', historical=True)['rows'][1]['binding']
        holder, selected, status, tabs = self.holder(source, historical=True)
        app_module.MainWindow.show_catalog_map_node(holder, '1,1', binding)
        self.assertEqual(selected, ['1,1'])
        self.assertEqual(tabs, ['assistant-map-tab'])
        self.assertEqual(status, [])
        holder, selected, status, tabs = self.holder(source, historical=False)
        app_module.MainWindow.show_catalog_map_node(holder, '1,1', binding)
        self.assertEqual(selected, [])

    def test_existing_plain_binding_keeps_original_six_field_behavior(self):
        source = existing_public_graph()
        holder, selected, status, tabs = self.holder(source)
        binding = {'epoch': 'public-run', 'zone_id': 'zone_1', 'template_id': '1a',
                   'node_id': '0,2', 'row': 0, 'col': 2}
        app_module.MainWindow.show_catalog_map_node(holder, '0,2', binding)
        self.assertEqual(selected, ['0,2'])
        self.assertEqual(status, [])


if __name__ == '__main__':
    unittest.main()

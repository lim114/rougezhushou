"""Documented recruitment results are alternatives, never eligibility or grants."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import node_catalog as catalog, event_planning
from rouge.node_catalog_view import NodeCatalogPanel, event_details_text
from rouge.player_node_information import node_information_text

ROOT = Path(__file__).resolve().parents[1]
EVENT = 'community_group_018'
SCENE = EVENT + ':scene:0'
CHOICE = SCENE + ':choice:1'
PAIRS = [['先锋', '近卫'], ['重装', '辅助'], ['医疗', '狙击'], ['术师', '特种']]


def previous_planning():
    path = ROOT / 'verification/sections/290-preparation/prior-289/rouge/event_planning.py'
    raw = path.read_bytes()
    # Frozen source is used by both root boundary checks and the full selector.
    if sha256(raw).hexdigest() != 'abf3dadb856accb9f7239aa98cedda2c66fd9476e331592fa89438b25418782b':
        raise AssertionError('The archived original289 planning changed.')
    module = types.ModuleType('rouge._event_planning_289_comparison')
    module.__package__ = 'rouge'
    module.__file__ = str(ROOT / 'rouge/event_planning.py')
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def entry(**extra):
    record = next(row for row in catalog.all_events(include_indirect=True)['rows'] if row['id'] == EVENT)
    return {'kind':'event', 'record':record, **extra}


def row(context=None):
    return next(row for row in event_planning.choice_eligibility(EVENT, SCENE, context)['rows']
                if row['choice_key'] == CHOICE)


class RecruitmentIntegration290Tests(unittest.TestCase):
    def test_all_event_choices_keep_original_eligibility_and_only_target_annotation_changes(self):
        previous = previous_planning()
        # Section298 adds a source-bound main-floor constraint after this historical
        # comparison baseline. Verify the exact addition, then compare every older
        # field without disabling the live source or replacing its derived status.
        rule_path = ROOT / 'rouge/data/event-node-requirements.json'
        rule_raw = rule_path.read_bytes()
        self.assertEqual(sha256(rule_raw).hexdigest(),
                         'f11c6d83a048ffdea14cbccdd1506ff02c3ef35a1cf94f107e30845b2d1deab3')
        rules = json.loads(rule_raw)
        expected_forbidden = {'community_group_024':[1,5,6], 'community_group_025':[1,6],
                              'community_group_027':[1,2,6], 'community_group_028':[1,2,6],
                              'community_group_029':[1,2,6], 'community_group_037':[1]}
        self.assertEqual({identity:rule['documented_excluded_main_floors']
                          for identity,rule in rules['events'].items()}, expected_forbidden)
        for context in ({}, {'floor':2,'node_type':'不期而遇','entry_mode':'content','resources':{'hope':20}},
                        {'floor':1,'difficulty':3,'node_type':'作战','entry_mode':'natural'}):
            for event in catalog._data()['events']:
                for scene in event['scenes']:
                    old = previous.choice_eligibility(event['id'],scene['key'],context)
                    current = event_planning.choice_eligibility(event['id'],scene['key'],context)
                    for current_row in current['rows']:
                        added = [check for check in current_row['checks']
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
                            current_row['checks'] = [check for check in current_row['checks']
                                if check['key']!='documented_node_natural_main_floor']
                            matches = [check['matches'] for check in current_row['checks']]
                            current_row['status'] = ('excluded' if False in matches else
                                'unknown' if None in matches or not matches else 'matched')
                        movement=current_row.pop('movement_result_reference',None)
                        if movement is not None:
                            self.assertEqual(current_row['choice_key'],'community_group_019:scene:1:choice:0')
                            self.assertEqual(movement['status'],'documented_reference')
                            self.assertEqual(movement['annotation_role'],'selection_result')
                            self.assertEqual(movement['choice_key'],current_row['choice_key'])
                            self.assertFalse(movement['source_scene_link_verified'])
                            self.assertIsNone(movement['actual_moved'])
                            self.assertIsNone(current_row['unparsed_condition_text'])
                            current_row['unparsed_condition_text']=current_row['conditional_text']
                        if current_row['choice_key'] != CHOICE:
                            continue
                        reference = current_row.pop('recruitment_result_reference')
                        self.assertEqual(reference['status'],'documented_reference')
                        self.assertEqual(reference['annotation_role'],'selection_result')
                        self.assertIsNone(current_row['unparsed_condition_text'])
                        current_row['unparsed_condition_text'] = current_row['conditional_text']
                    self.assertEqual(current,old,(event['id'],scene['key'],context))

    def test_one_hope_gain_is_not_multiplied_by_four_reference_variants(self):
        for context in ({},{'resources':{'hope':0}},{'resources':{'hope':20}}):
            before=deepcopy(context)
            resource_row=next(r for r in event_planning.choice_resources(EVENT,SCENE,context)['rows']
                              if r['choice_key']==CHOICE)
            references=resource_row['resource_references']
            self.assertEqual(len(references),1)
            self.assertEqual((references[0]['resource'],references[0]['quantity_reference']),('hope',2))
            self.assertIsNone(references[0]['actual_changed'])
            reference=resource_row['choice_eligibility']['recruitment_result_reference']
            self.assertEqual([v['profession_pair'] for v in reference['variants']],PAIRS)
            self.assertTrue(reference['variants_are_alternatives'])
            self.assertEqual(context,before)
            self.assertIsNone(resource_row['actual_new_resources'])
            self.assertIsNone(reference['actual_granted'])
            self.assertIsNone(reference['recruitment_cost'])
            self.assertIsNone(reference['actual_cultivation'])

    def test_player_results_are_chinese_and_raw_placeholder_stays_in_evidence_page(self):
        text=node_information_text(entry())
        for index,pair in enumerate(PAIRS,1):
            self.assertIn(f'职业组合 {index}：'+ '或'.join(pair)+'。',text)
        self.assertIn('获得2希望，招募1名5星及以下的直升干员',text)
        self.assertIn('本次职业组合、实际招募、招募费用和直升后的等级/精英阶段：尚未确认',text)
        self.assertIn('职业组合说明不作为选项出现条件',text)
        self.assertNotIn('??',text)
        self.assertNotIn('条件原文：可出现的职业搭配',text)
        self.assertNotIn('https://',text)
        self.assertNotIn('choice_ro6_hire',text)
        evidence=event_details_text(EVENT)
        self.assertIn('??或??',evidence)
        self.assertIn('349818',evidence)
        self.assertIn('440271',evidence)
        self.assertIn('choice_ro6_hire1_6',evidence)

    def test_unparsed_annotations_in_all_other_choices_are_untouched(self):
        previous=previous_planning()
        remaining=[];movement_annotations=[]
        for event in catalog._data()['events']:
            for scene in event['scenes']:
                old=previous.choice_eligibility(event['id'],scene['key'])
                current=event_planning.choice_eligibility(event['id'],scene['key'])
                for before,after in zip(old['rows'],current['rows']):
                    if before['choice_key']!=CHOICE and before['unparsed_condition_text']:
                        if before['choice_key']=='community_group_019:scene:1:choice:0':
                            movement=after['movement_result_reference']
                            self.assertEqual(movement['status'],'documented_reference')
                            self.assertEqual(movement['annotation_role'],'selection_result')
                            self.assertIsNone(after['unparsed_condition_text'])
                            self.assertEqual(after['conditional_text'],before['conditional_text'])
                            normalized=deepcopy(after);normalized.pop('movement_result_reference')
                            normalized['unparsed_condition_text']=before['unparsed_condition_text']
                            self.assertEqual(normalized,before)
                            movement_annotations.append(before['choice_key'])
                        else:
                            self.assertEqual(after['unparsed_condition_text'],before['unparsed_condition_text'])
                            remaining.append(before['choice_key'])
                        self.assertNotIn('recruitment_result_reference',after)
        self.assertEqual(len(remaining),10)
        self.assertEqual(movement_annotations,['community_group_019:scene:1:choice:0'])

    def test_history_and_copies_do_not_create_operator_or_inventory_state(self):
        context={'resources':{'hope':20},'item_quantities':{'rogue_6_scrap_G_12':1}}
        before=deepcopy(context)
        text=node_information_text(entry(history_read=True),context=context)
        self.assertIn('历史',text)
        self.assertIn('职业组合 4：术师或特种',text)
        self.assertIn('实际招募',text)
        self.assertEqual(context,before)
        reference=row()['recruitment_result_reference']
        reference['variants'][0]['profession_pair'][0]='错误职业'
        self.assertEqual(row()['recruitment_result_reference']['variants'][0]['profession_pair'],PAIRS[0])
        self.assertEqual(catalog._scene(EVENT,SCENE)['choices'][1]['game_choice_ids'],[])

    def test_valid_then_tampered_source_restores_unknown_and_original_annotation(self):
        from rouge import choice_recruitment_results as model
        manifest=json.loads((ROOT/model.MANIFEST).read_text(encoding='utf8'))
        with tempfile.TemporaryDirectory(prefix='rouge-290-public-source-') as directory:
            clone=Path(directory)
            for relative in (model.MANIFEST,*manifest['files']):
                target=clone/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/relative).read_bytes())
            with patch.object(model,'ROOT',clone):
                self.assertEqual(row()['recruitment_result_reference']['status'],'documented_reference')
                # Select a sealed complete public HTML; no private fixture is used.
                html=next(relative for relative in manifest['files'] if relative.endswith('.html'))
                target=clone/html
                target.write_bytes(target.read_bytes()+b' ')
                value=row()
                self.assertEqual(value['recruitment_result_reference']['status'],'unknown')
                self.assertEqual(value['unparsed_condition_text'],value['conditional_text'])
                text=node_information_text(entry())
                self.assertIn('补充招募资料暂时无法核对',text)
                self.assertNotIn('职业组合 1：先锋或近卫',text)
                self.assertIn('补充招募来源未通过核对',event_details_text(EVENT))
        self.assertEqual(row()['recruitment_result_reference']['status'],'documented_reference')


class RecruitmentView290Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance() or QApplication([])

    def test_two_reading_pages_keep_exact_selection_and_nonzero_scroll(self):
        panel=NodeCatalogPanel()
        self.addCleanup(panel.close)
        panel.resize(1050,680)
        panel.show()
        panel.list.setCurrentRow(next(i for i,e in enumerate(panel.entries)
                                     if e['kind']=='event' and e['record']['id']==EVENT))
        for widget in (panel.player_detail,panel.detail):
            panel.reading_tabs.setCurrentWidget(widget)
            self.qt.processEvents()
            self.assertIn('直升',widget.toPlainText())
            cursor=widget.textCursor()
            cursor.setPosition(3)
            cursor.setPosition(14,QTextCursor.MoveMode.KeepAnchor)
            widget.setTextCursor(cursor)
            bar=widget.verticalScrollBar()
            self.assertGreater(bar.maximum(),0)
            bar.setValue(max(1,bar.maximum()//2))
            before=(panel.detail_key,widget.toPlainText(),cursor.selectedText(),bar.value())
            panel.refresh()
            self.qt.processEvents()
            self.assertIs(panel.reading_tabs.currentWidget(),widget)
            self.assertEqual((panel.detail_key,widget.toPlainText(),widget.textCursor().selectedText(),bar.value()),before)


if __name__=='__main__':
    unittest.main()

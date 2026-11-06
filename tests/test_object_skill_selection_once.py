from collections import Counter
import unittest
from rouge import current_stage_objects as model


class TrackedDeclaration(dict):
    def __init__(self, **values):
        super().__init__(values)
        self.reads = Counter()

    def get(self, key, default=None):
        self.reads[key] += 1
        return super().get(key, default)


class ObjectSkillSelectionOnceTests(unittest.TestCase):
    def derive(self, index, level):
        raw = TrackedDeclaration(inst={'characterKey': 'unit'}, skillIndex=index, mainSkillLvl=level)
        current = {'id': 'stage', 'name': 'stage', 'level_key': 'level', 'source': {},
                   'source_identity': 'source', 'actions': [],
                   'level': {'predefines': {'tokenInsts': [raw]}}}
        reference = {'identity': 'verified', 'selected': {
            'characters': {'unit': {'name': 'unit', 'skills': [{'skillId': 'a'}, {'skillId': 'b'}]}},
            'skills': {'a': {'levels': ['a1', 'a2']}, 'b': {'levels': ['b1']}}}}
        return raw, model._derive(current, reference)['entries'][0]['skills']

    def test_declaration_selection_read_once(self):
        raw, skills = self.derive(1, 2)
        self.assertEqual(raw.reads['skillIndex'], 1)
        self.assertEqual(raw.reads['mainSkillLvl'], 1)
        self.assertEqual([s['selected_by_index'] for s in skills], [False, True])
        self.assertEqual([s['selected_level'] for s in skills], ['a2', None])

    def test_unknown_index_and_level_do_not_select_other_skill(self):
        for index in (None, False, -1, 2, '1'):
            for level in (None, False, 0, -1, 3, '1'):
                with self.subTest(index=index, level=level):
                    _, skills = self.derive(index, level)
                    self.assertEqual([s['selected_by_index'] for s in skills], [False, False])
                    self.assertEqual([s['selected_level'] for s in skills], [None, None])

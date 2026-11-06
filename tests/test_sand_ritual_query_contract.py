import unittest
from unittest.mock import patch

from rouge import current_sand_reference as sand
from rouge import current_ritual_reference as ritual


class SandRitualQueryContractTests(unittest.TestCase):
    def test_invalid_query_types_raise_before_loading(self):
        for model in (sand, ritual):
            with patch.object(model, 'packet') as load:
                for value in (None, False, 0, [], {}):
                    for args in ((value, 'key'), ('scenes', value)):
                        with self.subTest(model=model.__name__, args=args), self.assertRaises(TypeError):
                            model.locate(*args)
                    with self.subTest(model=model.__name__, event=value), self.assertRaises(TypeError):
                        model.reference(value)
                self.assertIsNone(model.reference('unknown'))
                self.assertIsNone(model.locate('stages', 'unknown'))
                load.assert_not_called()

    def test_choice_none_is_normal_but_other_bad_types_raise(self):
        for model in (sand, ritual):
            for sid, cid in ((None, None), ('scene', None), (None, 'choice')):
                self.assertIsNone(model.choice_reference({}, sid, cid))
            for value in (False, 0, [], {}):
                for sid, cid in ((value, 'choice'), ('scene', value), (value, None), (None, value)):
                    with self.subTest(model=model.__name__, sid=sid, cid=cid), self.assertRaises(TypeError):
                        model.choice_reference({}, sid, cid)

    def test_exact_membership_and_unknown_selection_remain_unchanged(self):
        for model in (sand, ritual):
            result = model.reference()
            for cid, choice in result['choices'].items():
                with self.subTest(model=model.__name__, cid=cid):
                    found = model.choice_reference(result, choice['scene_id'], cid)
                    self.assertEqual(found['id'], cid)
                    self.assertIsNone(model.choice_reference(result, 'not-this-scene', cid))
            self.assertIsNone(model.choice_reference(result, result['event']['entry_scene_id'], 'unknown'))

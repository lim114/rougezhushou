from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import current_elbert_reference as model


class RelatedSnapshotTests(unittest.TestCase):
    def test_each_valid_related_jump_refreshes_once(self):
        for stage in model.STAGES:
            result = model.reference(stage)
            for row in result['entities']:
                for request in model.related_entities(result, row['key']):
                    with self.subTest(stage=stage, key=row['key']), patch.object(model, 'reference', wraps=model.reference) as read:
                        self.assertEqual(model.resolve_related(result, row['key'], request),
                            {'stage_id': stage, 'enemy_key': request['enemy_key']})
                        read.assert_called_once_with(stage, row['key'])

    def test_changed_source_and_stage_rejected(self):
        result = model.reference('ro6_b_3')
        request = model.related_entities(result, '0')[0]
        for field, value in (('source_identity', ('changed',)), ('stage', {})):
            fresh = deepcopy(result); fresh[field] = value
            with self.subTest(field=field), patch.object(model, 'reference', return_value=fresh) as read:
                self.assertIsNone(model.resolve_related(result, '0', request))
                read.assert_called_once()
        with patch.object(model, 'reference', return_value=None):
            self.assertIsNone(model.resolve_related(result, '0', request))

    def test_wrong_request_rejected_before_refresh(self):
        result = model.reference('ro6_b_3')
        request = model.related_entities(result, '0')[0]
        request['enemy_key'] = 'not-a-target'
        with patch.object(model, 'reference') as read:
            self.assertIsNone(model.resolve_related(result, '0', request))
            read.assert_not_called()

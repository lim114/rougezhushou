from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from rouge import expansion_reference as model
from rouge.player_reference_notes import note_for,reference_target
from rouge.player_notes import content_key,NoteStore

class ReferenceNoteTests(unittest.TestCase):
    def sample(self,category):return next(row for row in model.rows(category,changes_only=False)if row['name'].strip())
    def test_exact_stage_and_scene_contexts_round_trip_without_name_guess(self):
        for category in('stages','scenes'):
            row=self.sample(category);note=note_for(category,row['id']);self.assertEqual(reference_target(note),(category,row['id']));self.assertEqual(note['title'],row['name'])
            self.assertNotEqual(content_key(note),content_key({'kind':'battle'if category=='stages'else'event','title':note['title']}))
    def test_same_name_stage_variants_do_not_share_notes(self):
        rows=model.rows('stages',changes_only=False);seen={}
        for row in rows:seen.setdefault(row['name'],[]).append(row['id'])
        candidates=next(ids for name,ids in seen.items()if name and len(ids)>1)
        self.assertNotEqual(content_key(note_for('stages',candidates[0])),content_key(note_for('stages',candidates[1])))
    def test_unknown_identity_and_mutated_source_key_cannot_resolve_by_title(self):
        self.assertIsNone(note_for('stages','not-current-id'));row=self.sample('stages');note=note_for('stages',row['id']);note['variant_id']='other-source';self.assertIsNone(reference_target(note))
        self.assertIsNone(reference_target({'kind':'battle','title':row['name']}));self.assertIsNone(note_for('relics','anything'))
    def test_source_failure_leaves_saved_note_readable_but_reference_unknown(self):
        row=self.sample('scenes');note=note_for('scenes',row['id'])
        with TemporaryDirectory()as folder:
            store=NoteStore(folder);key=content_key(note);store.save(key,'旧资料下的个人记录',store.read(key)[1])
            with patch.object(model,'packet',return_value=None):self.assertIsNone(reference_target(note));self.assertEqual(store.read(key)[0],'旧资料下的个人记录')
    def test_malformed_context_never_enables_a_different_entry(self):
        for content in(None,[],{}, {'kind':'reference-scene','event_id':[]},{'kind':'reference-stage','event_id':True}):self.assertIsNone(reference_target(content))

if __name__=='__main__':unittest.main()

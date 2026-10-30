"""Current code binding restores the unchanged documented fixed-stage links."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge import battle_event_references as model, node_catalog, event_planning

ROOT=Path(__file__).resolve().parents[1]
OLD='research/p3-battle-event-references-296/source-manifest.json'
NEW='research/p3-battle-entry-compatibility-299/source-manifest.json'
OLD_SHA='c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21'
NEW_SHA='26fadacc46fcd890aef672509db414ca3fad1a407b5affc06a18753f45427a3c'
def load(name):return json.loads((ROOT/name).read_bytes())
def canon(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

class BattleEntryCompatibility299Tests(unittest.TestCase):
 def test_only_two_current_code_bindings_change_and_original_source_remains(self):
  old=load(OLD);new=load(NEW)
  self.assertEqual(sha256((ROOT/OLD).read_bytes()).hexdigest(),OLD_SHA)
  self.assertEqual(sha256((ROOT/NEW).read_bytes()).hexdigest(),NEW_SHA)
  changed=[key for key in old['files']if old['files'][key]!=new['files'][key]]
  self.assertEqual(set(changed),{'rouge/event_planning.py','rouge/node_catalog.py'})
  for name in changed:
   historical=ROOT/'verification/sections/298-preparation/before'/name
   self.assertEqual(sha256(historical.read_bytes()).hexdigest(),old['files'][name]['sha256'])
   # Later reviewed refactors are not the historical 299 parser. Check that
   # original byte identity against the preserved source, not today's program.
   historical299=ROOT/'research/runtime-reference-loaders-20261031/baseline/historical-299'/name
   self.assertEqual(sha256(historical299.read_bytes()).hexdigest(),new['files'][name]['sha256'])
  new.pop('compatibility_rebinding');new['section']=296
  for name in changed:new['files'][name]=old['files'][name]
  self.assertEqual(new,old)

 def test_reverse_reader_code_changes_only_two_explicit_source_binding_constants(self):
  old=ROOT/'verification/sections/299-preparation/before/rouge/battle_event_references.py'
  def tree(path):
   result=ast.parse(path.read_bytes())
   result.body=[n for n in result.body if not(isinstance(n,ast.Assign)and any(
     isinstance(k,ast.Name)and k.id in ('MANIFEST','MANIFEST_SHA256')for k in n.targets))]
   return ast.dump(result,include_attributes=False)
  self.assertEqual(tree(old),tree(ROOT/'rouge/battle_event_references.py'))
  runtime=load(model.MANIFEST)
  self.assertEqual(runtime['historical_recipe_manifest'],{'path':NEW,'sha256':NEW_SHA,'bytes':(ROOT/NEW).stat().st_size})
  self.assertEqual(runtime['files'],{n:v for n,v in load(NEW)['files'].items()if not n.endswith('.py')})
  self.assertEqual(model.MANIFEST,'research/runtime-reference-loaders-20261031/battle-events/source-manifest.json')
  self.assertEqual(sha256((ROOT/model.MANIFEST).read_bytes()).hexdigest(),model.MANIFEST_SHA256)

 def test_old_byte_binding_still_rejects_current_files_and_new_binding_restores_exact_counts(self):
  with patch.object(model,'MANIFEST',OLD),patch.object(model,'MANIFEST_SHA256',OLD_SHA),patch.object(model,'_CACHE',{}):
   self.assertIsNone(model._packet())
   for sid in model.STAGE_IDS:
    result=model.stage_event_references(sid)
    self.assertFalse(result['source_valid']);self.assertEqual(result['rows'],[])
  rows=[model.stage_event_references(sid)for sid in model.STAGE_IDS]
  self.assertTrue(all(r['source_valid']for r in rows))
  self.assertEqual(sum(r['raw_edge_count']for r in rows),14)
  self.assertEqual(sum(len(r['rows'])for r in rows),11)
  self.assertEqual(sum(len(r['excluded_rows'])for r in rows),3)
  self.assertTrue(all(r['actual_entered']is None and r['current_server_verified']is False for r in rows))

 def legacy_results(self):
  """Replay old bound public bytes with the unchanged current forward API.

  Old code files are guard inputs only. They are not executed, and this is not
  an original296 runtime or native test. Every14 source link is cross-checked
  again by the unchanged reverse-link implementation.
  """
  manifest=load(OLD)
  with tempfile.TemporaryDirectory(prefix='rouge299-legacy-public-binding-')as folder:
   root=Path(folder)
   for name in [OLD,*manifest['files']]:
    source=(ROOT/'verification/sections/298-preparation/before'/name if name in (
     'rouge/event_planning.py','rouge/node_catalog.py')else ROOT/name)
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
   with patch.object(model,'ROOT',root),patch.object(model,'MANIFEST',OLD),patch.object(model,'MANIFEST_SHA256',OLD_SHA),patch.object(model,'_CACHE',{}):
    rows=[model.stage_event_references(sid)for sid in model.STAGE_IDS]
    self.assertTrue(all(r['source_valid']for r in rows));return deepcopy(rows)

 def test_all_source_rows_and_choices_are_identical_apart_from_the_new_manifest_identity(self):
  old=self.legacy_results();new=[model.stage_event_references(sid)for sid in model.STAGE_IDS]
  def normalized(value):
   if isinstance(value,dict):return {k:(OLD_SHA if k=='manifest_sha256'else normalized(v))for k,v in value.items()}
   if isinstance(value,list):return[normalized(v)for v in value]
   return value
  self.assertEqual(normalized(new),old)

 def test_old_source_tokens_cannot_borrow_current_source_and_current_exact_tokens_resolve(self):
  old=self.legacy_results()
  for packet in old:
   for row in packet['rows']:
    self.assertIsNone(model.resolve_stage_event_reference(packet['stage_id'],row['token']))
  for sid in model.STAGE_IDS:
   for row in model.stage_event_references(sid)['rows']:
    resolved=model.resolve_stage_event_reference(sid,row['token'])
    self.assertEqual(resolved['reference_id'],row['reference_id'])

 def test_all_190_default_resource_queries_keep_the_original_fixed_values(self):
  before=load('verification/sections/298-preparation/before-output.json')['default_choice_resources_scenes'];actual={}
  for event in node_catalog.all_events(include_indirect=True)['rows']:
   for scene in node_catalog.event_details(event['id'])['rows']:
    actual[scene['key']]=sha256(canon(event_planning.choice_resources(event['id'],scene['key']))).hexdigest()
  self.assertEqual(len(actual),190);self.assertEqual(actual,before)

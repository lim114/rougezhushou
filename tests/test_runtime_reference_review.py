"""Public reference semantics and data guards survive code-provenance separation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from hashlib import sha256
from unittest.mock import patch
import ast,json,unittest
from rouge import battle_event_references as battle,named_reward_items as items,ritual_weakening as ritual

ROOT=Path(__file__).resolve().parents[1]
RECIPES=[(battle,'battle-events','research/p3-battle-entry-compatibility-299/source-manifest.json'),
         (items,'named-items','research/p3-named-reward-items-301/source-manifest.json'),
         (ritual,'ritual','research/p3-ritual-weakening-302/source-manifest.json')]


def packet(model):
    return model._packet()if model is battle else model._verified_packet(items.EVENT_IDS[0])if model is items else model._verified_packet()


def outputs(model):
    if model is battle:return [model.stage_event_references(s)for s in model.STAGE_IDS]
    if model is items:
        result=[]
        for identity in model.EVENT_IDS:
            p=model.event_reference(identity);result.append(p)
            if p['source_valid']:
                result.extend(model.item_details(identity,r['scene_key'],r['choice_key'])for r in p['choices'])
        return result
    p=model.event_reference(model.EVENT_ID)
    return [p]+[model.weakening_details(model.EVENT_ID,r['scene_key'],r['choice_key'])for r in p['choices']]


def clone(root,model,manifest_name):
    manifest=json.loads((ROOT/manifest_name).read_bytes())
    for name in (manifest_name,*manifest.get('runtime_files',manifest['files'])):
        source=ROOT/name
        if name=='rouge/node_catalog.py':source=ROOT/'research/runtime-reference-loaders-20261031/baseline/historical-299'/name
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
    return manifest


class RuntimeReferenceReviewTests(unittest.TestCase):
    def test_existing_loaders_only_change_the_two_manifest_binding_assignments(self):
        for model,tag,_ in RECIPES:
            def tree(raw):
                tree=ast.parse(raw);tree.body=[n for n in tree.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ('MANIFEST','MANIFEST_SHA256')for t in n.targets))];return ast.dump(tree,include_attributes=False)
            name=Path(model.__file__).name
            self.assertEqual(tree((ROOT/'research/runtime-reference-loaders-20261031/baseline/rouge'/name).read_bytes()),tree(Path(model.__file__).read_bytes()))
            manifest=json.loads((ROOT/model.MANIFEST).read_bytes());runtime=manifest.get('runtime_files',manifest['files']);self.assertFalse(any(p.endswith('.py')for p in runtime))

    def test_current_references_equal_legacy_public_guard_replay_except_manifest_identity(self):
        for model,tag,recipe in RECIPES:
            old_digest=sha256((ROOT/recipe).read_bytes()).hexdigest();new_digest=model.MANIFEST_SHA256
            current=outputs(model);self.assertTrue(current and all(p['source_valid']for p in current))
            with TemporaryDirectory()as folder,ExitStack()as stack:
                root=Path(folder);clone(root,model,recipe);stack.enter_context(patch.object(model,'ROOT',root));stack.enter_context(patch.object(model,'MANIFEST',recipe));stack.enter_context(patch.object(model,'MANIFEST_SHA256',old_digest))
                if model is battle:stack.enter_context(patch.object(model,'_CACHE',{}))
                if model is items:stack.enter_context(patch.object(model,'_parsed_packet',None))
                legacy=outputs(model);self.assertTrue(legacy and all(p['source_valid']for p in legacy))
            normalize=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).replace(new_digest,old_digest)
            self.assertEqual(normalize(current),normalize(legacy),tag)

    def test_unrelated_program_bytes_do_not_hide_unchanged_public_data(self):
        for model,_,_ in RECIPES:
            with TemporaryDirectory()as folder,ExitStack()as stack:
                root=Path(folder);clone(root,model,model.MANIFEST);path=root/'rouge/node_catalog.py';path.parent.mkdir(parents=True,exist_ok=True);path.write_text('# unrelated reviewed refactor\n','utf8')
                stack.enter_context(patch.object(model,'ROOT',root))
                if model is battle:stack.enter_context(patch.object(model,'_CACHE',{}))
                if model is items:stack.enter_context(patch.object(model,'_parsed_packet',None))
                self.assertIsNotNone(packet(model))
                data=root/model.DATA;raw=data.read_bytes();data.write_bytes(raw+b' ');self.assertIsNone(packet(model));data.write_bytes(raw);self.assertIsNotNone(packet(model))

    def test_live_api_pollution_still_rejects_when_public_file_bytes_match(self):
        from rouge import node_catalog
        for model,_,_ in RECIPES:
            self.assertIsNotNone(packet(model))
            with patch.object(node_catalog,'_event',return_value={}):
                if model is battle:self.assertFalse(model.stage_event_references(model.STAGE_IDS[0])['source_valid'])
                else:self.assertIsNone(packet(model))

    def test_no_local_actual_state_is_inferred_from_restored_reference(self):
        for model,_,_ in RECIPES:
            for result in outputs(model):
                self.assertTrue(result['source_valid'])
                for key,value in result.items():
                    if key.startswith('actual_'):self.assertIsNone(value,key)
                self.assertFalse(result.get('run_state_updated',False));self.assertFalse(result.get('inventory_updated',False))

if __name__=='__main__':unittest.main()

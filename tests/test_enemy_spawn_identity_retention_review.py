from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from rouge import current_enemy_spawns as model


class EnemySpawnIdentityRetentionTests(TestCase):
    def test_each_pinned_member_corruption_is_rejected(self):
        root=Path(__file__).resolve().parents[1]
        names=[model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']]
        with TemporaryDirectory() as temporary:
            target=Path(temporary)
            for name in names:
                path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes((root/name).read_bytes())
            with patch.object(model.battle.version,'_file',side_effect=lambda name:target/name):
                self.assertIsNotNone(model.evidence())
                for name in names:
                    with self.subTest(name=name):
                        path=target/name;raw=path.read_bytes();path.write_bytes(raw+b' ')
                        self.assertIsNone(model.evidence())
                        path.write_bytes(raw)

    def test_scope_identity_stage_and_original_source_are_distinct_gates(self):
        stage=model.battle.stage_reference('ro6_n_1_1');original=model.evidence()
        for change in ('identity','stage','level','original'):
            scope=deepcopy(original)
            if change=='identity':scope['source_identity']='different'
            elif change=='stage':scope['stages'].pop(stage['id'])
            elif change=='level':scope['stages'][stage['id']]['level_key']='different'
            else:scope['stages'][stage['id']]['original_source']={}
            with self.subTest(change=change),patch.object(model,'evidence',return_value=scope),patch.object(model,'_derive') as derive:
                self.assertIsNone(model.stage_reference(stage['id'],'0',prepared_current=stage))
                derive.assert_not_called()

    def test_missing_exact_binding_raises_instead_of_using_matching_id(self):
        stage=model.battle.stage_reference('ro6_n_1_1');enemy=stage['enemies'][0]
        action=next(a for a in stage['actions'] if a['raw']['actionType']=='SPAWN' and a['raw']['key']==enemy['id'])
        action['enemy_candidates']=[]
        with self.assertRaisesRegex(ValueError,'Exact candidate binding missing'):model._derive(stage,enemy['key'])

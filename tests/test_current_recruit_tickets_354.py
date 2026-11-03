"""Candidate354 tests: not executed or counted as validation during preparation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import subprocess
import sys
import unittest

from rouge import current_recruit_tickets as model


def clone(root):
    for name in (model.MANIFEST, *json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']):
        target = root/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((model.ROOT/name).read_bytes())


class CurrentRecruitTickets354Tests(unittest.TestCase):
    def test_rebuild_and_all47_exact_pairs_cover94_records_without_pool_claim(self):
        result = subprocess.run([sys.executable, '-B', 'scripts/build_current_recruit_tickets_354.py', '--check'],
                                cwd=model.ROOT, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        packet = model.reference()
        self.assertEqual(len(packet['rows']), 47)
        self.assertIsNone(packet['selected'])
        self.assertFalse(packet['data']['complete_reward_pool'])
        current = model.version.packet()['current']['details']
        ids = set()
        for row in packet['rows']:
            a, b = row['id'], row['stashed_id']
            self.assertEqual(row['pair'], current['stashableTickets'][a])
            self.assertEqual(row['original_item'], current['items'][a])
            self.assertEqual(row['stashed_item'], current['items'][b])
            self.assertEqual(row['original_ticket'], current['recruitTickets'][a])
            self.assertEqual(row['stashed_ticket'], current['recruitTickets'][b])
            self.assertEqual({k:v for k,v in row['original_ticket'].items()if k!='id'},
                             {k:v for k,v in row['stashed_ticket'].items()if k!='id'})
            ids.update((a,b))
        self.assertEqual(ids,set(current['recruitTickets']))
        for key in ('actual_inventory','actual_owned','actual_recruited','actual_cost','actual_random_result'):
            self.assertIsNone(packet[key])
        self.assertFalse(packet['run_updated'])

    def test_profession_and_family_are_real_intersecting_filters(self):
        all_rows = model.reference()['rows']
        families = {key: model.reference(ticket_family=key)['rows']for key,_ in model.FAMILIES}
        self.assertEqual({key:len(rows)for key,rows in families.items()},
                         {'profession':24,'protocol':8,'coordination':4,'dispatch':4,'limited':7})
        self.assertEqual({row['id']for rows in families.values()for row in rows},
                         {row['id']for row in all_rows})
        for profession,_ in model.PROFESSIONS:
            filtered = model.reference(profession=profession)['rows']
            self.assertEqual(filtered,[row for row in all_rows if profession in row['professions']])
            for family,_ in model.FAMILIES:
                rows = model.reference(profession=profession,ticket_family=family)['rows']
                self.assertEqual(rows,[row for row in filtered if row['family']==family])
        self.assertIn('rogue_6_recruit_ticket_double_1',
                      {r['id']for r in model.reference(profession='PIONEER')['rows']})
        self.assertIn('rogue_6_recruit_ticket_double_1',
                      {r['id']for r in model.reference(profession='WARRIOR')['rows']})

    def test_full_chinese_usage_stars_and_exact_stashed_identity(self):
        ids = ('rogue_6_recruit_ticket_pioneer_sp','rogue_6_recruit_ticket_temp_5_up',
               'rogue_6_recruit_ticket_temp_6','rogue_6_recruit_ticket_all_discount')
        for identity in ids:
            a = model.reference(identity)
            b = model.reference(a['selected']['stashed_id'])
            self.assertEqual(a['selected'],b['selected'])
            self.assertIn(model.version._plain(a['selected']['original_item']['usage']),model.player_text(a))
        five=model.reference('rogue_6_recruit_ticket_temp_5_up')
        self.assertEqual(five['selected']['stars'],[5]);self.assertIn('初次招募即相当于已经进阶',model.player_text(five))
        six=model.reference('rogue_6_recruit_ticket_temp_6')
        self.assertEqual(six['selected']['stars'],[6]);self.assertNotIn('初次招募即相当于已经进阶',model.player_text(six))

    def test_documented3_not_configuration15_and_complete_stashing_rules(self):
        result=model.reference();data=result['data'];text=model.player_text(result)
        self.assertEqual(data['documented_initial_capacity'],3)
        self.assertEqual(data['configuration_bounds'],{'recruitStashMinNum':1,'recruitStashMaxNum':15})
        self.assertEqual(len(data['documented_rules']),5)
        self.assertEqual(data['documented_revision'],442954)
        for phrase in ('初始招募阶段不能留存','初始留存上限为3张','不能再次存入',
                       '重新判定','不能用新券替换旧券','血管','不是本局容量','实际库存'):
            self.assertIn(phrase,text)

    def test_two_links_keep_exact_existing_originals_and_provider_targets(self):
        from rouge import current_exit, current_rest_travel
        for key,provider,cid in [('exit',current_exit,'choice_ro6_final1_2'),
                                 ('rest',current_rest_travel,'choice_ro6_rest_7')]:
            link=model.destination(key)
            self.assertEqual(link['original_choice_id'],cid)
            self.assertEqual(link['target'],provider.locate('choices',cid))
            self.assertEqual(link['original_choice']['type'],'USE_STASHED_TICKET')
            self.assertIsNone(link['actual_inventory']);self.assertIsNone(link['actual_eligible'])
        self.assertIsNone(model.destination('scene_ro6_final1_enter'));self.assertIsNone(model.destination(True))

    def test_real_manifest_member_damage_clears_after_success_then_recovers(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    path=root/name;raw=path.read_bytes();self.assertIsNotNone(model.packet())
                    path.write_bytes(raw+b'x');self.assertIsNone(model.packet(),name)
                    path.write_bytes(raw);self.assertIsNotNone(model.packet())

    def test_underlying_provider_loss_is_not_hidden_by_directory_copy(self):
        from rouge import current_exit,current_rest_travel
        for provider in (current_exit,current_rest_travel):
            with patch.object(provider,'packet',return_value=None):self.assertIsNone(model.packet())

    def test_invalid_types_unknown_id_and_mutable_results_do_not_leak(self):
        for kwargs in ({'ticket_id':True},{'ticket_id':'rogue_6_recruit_ticket_unknown'},
                       {'profession':True},{'profession':'GUARD'},{'ticket_family':'normal'},
                       {'ticket_family':False},{'query':None}):self.assertIsNone(model.reference(**kwargs))
        result=model.reference();result['rows'].clear();result['data']['links'].clear()
        self.assertEqual(len(model.reference()['rows']),47);self.assertEqual(len(model.reference()['data']['links']),2)


if __name__=='__main__':unittest.main()

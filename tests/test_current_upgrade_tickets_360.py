"""Prepared360 functional cases; not executed during cache-only preparation."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import subprocess
import sys
import unittest
from rouge import current_upgrade_tickets as model


def clone(root):
    for name in (model.MANIFEST, *json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']):
        target=root/name; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((model.ROOT/name).read_bytes())


class CurrentUpgradeTickets360Tests(unittest.TestCase):
    def test_rebuild_complete18_originals_and_explicit_not_actual_boundaries(self):
        run=subprocess.run([sys.executable,'-B','scripts/build_current_upgrade_tickets_360.py','--check'],cwd=model.ROOT,capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr)
        result=model.reference(); self.assertIsNone(result['selected']); self.assertEqual(len(result['rows']),18)
        current=model.version.packet()['current']['details']
        self.assertEqual({r['id'] for r in result['rows']},set(current['upgradeTickets']))
        for row in result['rows']:
            self.assertEqual(row['item'],current['items'][row['id']])
            self.assertEqual(row['ticket'],current['upgradeTickets'][row['id']])
            self.assertEqual(row['professions'],row['ticket']['professionList'])
            self.assertEqual(row['stars'],[int(t[-1]) for t in row['ticket']['rarityList']])
        for key in ('actual_owned','actual_candidates','actual_eligible','actual_cost','actual_upgraded','actual_cultivation'):
            self.assertIsNone(result[key])
        self.assertFalse(result['run_updated']); self.assertFalse(result['calculation_applied'])
        self.assertFalse(result['data']['complete_acquisition_pool'])

    def test_three_real_kinds_and_independent_profession_star_intersections(self):
        result=model.reference()
        self.assertEqual({kind:len(model.reference(kind=kind)['rows']) for kind,_ in model.KINDS},
                         {'general':2,'profession':8,'relic':8})
        for profession,_ in model.PROFESSIONS:
            for kind,_ in model.KINDS:
                for star in (1,5,6):
                    rows=model.reference(profession=profession,kind=kind,star=star)['rows']
                    self.assertEqual(rows,[r for r in result['rows'] if profession in r['professions'] and r['kind']==kind and star in r['stars']])
        five='rogue_6_upgrade_ticket_5star'
        self.assertIsNotNone(model.reference(five,star=5)); self.assertIsNone(model.reference(five,star=6))
        self.assertEqual(model.reference('rogue_6_upgrade_ticket_all')['selected']['stars'],[1,2,3,4,5,6])

    def test_same_names_have_distinct_exact_relic_source_ids_and_do_not_merge(self):
        result=model.reference(); source=model.version.packet()['current']['details']
        for row in result['rows']:
            if row['kind']!='relic': continue
            origin=row['relic_origin']; self.assertEqual(origin['item'],source['items'][origin['id']])
            self.assertEqual(origin['relic'],source['relics'][origin['id']])
            buff=origin['relic']['buffs'][0]; values={b['key']:b['valueStr'] if b['valueStr'] is not None else b['value'] for b in buff['blackboard']}
            self.assertEqual(values['id'],row['id']); self.assertEqual(values['count'],1)
            self.assertEqual(origin['reference_count'],1); self.assertIsNone(origin['actual_recipient'])
            ordinary=[r for r in result['rows'] if r['name']==row['name'] and r['kind']=='profession']
            self.assertEqual(len(ordinary),1); self.assertNotEqual(ordinary[0]['id'],row['id'])
            self.assertIsNone(ordinary[0]['relic_origin']); self.assertIsNone(model.destination(ordinary[0]['id']))
            self.assertIn(origin['item']['name'],row['label'])
            self.assertEqual(model.locate('relics',origin['id'])['ticket_id'],row['id'])

    def test_exact_rest_source_no_borrowed_quantity_and_relic_reverse_destinations(self):
        from rouge import current_rest_travel as rest
        result=model.reference(); link=model.destination('rogue_6_upgrade_ticket_all')
        self.assertEqual(link['reader'],'rest'); self.assertEqual(link['target'],rest.locate('choices',model.REST_CHOICE))
        self.assertEqual(link['choice']['displayData']['itemId'],'rogue_6_upgrade_ticket_all')
        self.assertIsNone(link['original_quantity']); self.assertIsNone(link['actual_owned'])
        self.assertEqual(model.locate('choices',model.REST_CHOICE)['ticket_id'],'rogue_6_upgrade_ticket_all')
        for row in result['rows']:
            self.assertEqual(model.locate('items',row['id'])['ticket_id'],row['id'])
            if row['relic_origin']:
                self.assertEqual(model.destination(row['id'])['key'],row['relic_origin']['id'])
        for args in (('choices','choice_ro6_rest_7'),('relics','rogue_6_relic_assign_13'),('items',True),('stages','rogue_6_upgrade_ticket_all')):
            self.assertIsNone(model.locate(*args))

    def test_player_text_separates_range_actual_eligibility_promotion_and_stashing(self):
        for row in model.reference()['rows']:
            result=model.reference(row['id']); text=model.player_text(result)
            self.assertIn(model.version._plain(row['item']['usage']),text)
            for phrase in ('不消耗希望','不是本局持有券','不证明对应星级','首次招募时就处于已进阶状态','不会超过账号已有培养',
                           '不属于已核对的招募券留存配对','不能据此认定可以留存','当前服务器资格仍未知'):
                self.assertIn(phrase,text)
        self.assertIn('不能把新典训的1张或1人套到这里',model.player_text(model.reference('rogue_6_upgrade_ticket_all')))

    def test_real_source_member_loss_clears_packet_then_restores_and_provider_loss_propagates(self):
        from rouge import current_rest_travel as rest
        with TemporaryDirectory() as folder:
            root=Path(folder); clone(root)
            with patch.object(model,'ROOT',root):
                for name in (model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    path=root/name; raw=path.read_bytes(); self.assertIsNotNone(model.packet())
                    path.write_bytes(raw+b'x'); self.assertIsNone(model.packet(),name)
                    path.write_bytes(raw); self.assertIsNotNone(model.packet())
        with patch.object(rest,'packet',return_value=None): self.assertIsNone(model.packet())
        with patch.object(model.version,'packet',return_value=None): self.assertIsNone(model.packet())

    def test_unknown_numeric_masks_id_suffix_or_duplicate_bindings_cannot_supply_missing_lists(self):
        source=deepcopy(model.version.packet()['current']['details'])
        source['upgradeTickets']['rogue_6_upgrade_ticket_all']['rarityList']=['TIER_7']
        with self.assertRaises(ValueError): model.source_rows(source)
        source=deepcopy(model.version.packet()['current']['details'])
        source['relics']['rogue_6_relic_assign_1']['buffs'][0]['blackboard'][0]['valueStr']='unknown'
        with self.assertRaises(ValueError): model.source_rows(source)

    def test_invalid_inputs_and_mutation_do_not_leak_or_generate_candidates(self):
        for kwargs in ({'ticket_id':True},{'ticket_id':'unknown'},{'profession':'GUARD'},{'profession':False},
                       {'kind':True},{'kind':'recruit'},{'star':True},{'star':0},{'star':7},{'query':None}):
            self.assertIsNone(model.reference(**kwargs))
        result=model.reference(); result['rows'].clear(); result['data']['rows'].clear()
        self.assertEqual(len(model.reference()['rows']),18)


if __name__=='__main__': unittest.main()

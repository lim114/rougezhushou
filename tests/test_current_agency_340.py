from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_agency as model,node_catalog

def clone(root,icons=True):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']}
    if icons:names.update('rouge/data/'+v['file']for v in model.packet()['data']['profession_icons'].values())
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

class CurrentAgency340Tests(unittest.TestCase):
    def test_complete_build_reproduces_four_scenes_six_choices_and_eight_icons(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_agency_340.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();self.assertEqual((len(r['scenes']),len(r['choices']),len(r['data']['profession_icons'])),(4,6,8));self.assertIn('随机',r['data']['random_profession_document_source']['text'])
    def test_four_promoted_groups_each_two_hope_one_person_rarity_ceiling5(self):
        r=model.reference();rows=[c for c in r['choices'].values()if c['role']=='promoted'];self.assertEqual(len(rows),4)
        self.assertEqual(['或'.join(c['profession_pair'])for c in rows],list(model.OFFER_LABELS))
        for c in rows:
            self.assertEqual((c['hope_gain_reference'],c['recruit_count_reference'],c['rarity_ceiling_reference']),(2,1,5));self.assertIs(c['promoted_on_first_recruit_reference'],True);self.assertIsNone(c['actual_cost']);self.assertIsNone(c['actual_cultivation']);self.assertIsNone(c['actual_recruited'])
    def test_two_professions_not_two_people_and_four_rows_never_sum_rewards(self):
        r=model.reference()
        for c in r['choices'].values():
            if c['role']=='promoted':
                text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不是两个职业各招一名',text);self.assertIn('不累计成8希望或4名干员',text)
        self.assertIsNone(r['actual_hope']);self.assertFalse(r['run_updated'])
    def test_random_six_not_reliable_offer_or_two_hope_and_is_not_emergency(self):
        r=model.reference(offer=model.OFFER_LABELS[0]);c=next(c for c in r['choices'].values()if c['role']=='temporary_six');out=model.choice_reference(r,c['scene_id'],c['id'])
        self.assertIsNone(c['profession_pair']);self.assertIsNone(c['hope_gain_reference']);self.assertEqual(c['exact_rarity_reference'],6);self.assertIsNone(out['listed_condition_match'])
        text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不额外加上那个分支的2希望',text);self.assertIn('不同机制',text);self.assertIsNone(c['actual_cost'])
    def test_leave_no_invented_recruitment_and_each_terminal_has_no_extra_choices(self):
        r=model.reference();c=next(c for c in r['choices'].values()if c['role']=='leave');self.assertIsNone(c['recruit_count_reference']);self.assertIsNone(c['hope_gain_reference'])
        self.assertTrue(all(not s['choice_ids']for sid,s in r['scenes'].items()if sid!=r['event']['entry_scene_id']))
    def test_every_original_choice_and_scene_matches_complete_pinned_record(self):
        r=model.reference();d=model.version.packet()['current']['details']
        for kind,table in [('choices','choices'),('scenes','choiceScenes')]:
            for key,v in r['data']['originals'][kind].items():self.assertEqual(v,d[table][key])
    def test_all_ten_source_entries_exact_and_unknown_keys_never_fuzzy_match(self):
        r=model.reference();count=0
        for cat in('scenes','choices'):
            for key in r['data']['originals'][cat]:
                t=model.locate(cat,key);self.assertEqual(t['scene_id'],key if cat=='scenes'else r['choices'][key]['scene_id']);self.assertEqual(t['choice_id'],None if cat=='scenes'else key);count+=1
        self.assertEqual(count,10)
        for cat,key in [('choices','可靠的中介值得信任'),('scenes','scene_ro6_hire1_enter_2'),('relics','choice_ro6_hire1_1'),(True,'choice_ro6_hire1_1')]:self.assertIsNone(model.locate(cat,key))
    def test_four_by_four_declared_group_comparison_does_not_become_actual_offer(self):
        for offer in model.OFFER_LABELS:
            r=model.reference(offer=offer)
            for c in r['choices'].values():
                match=model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match'];self.assertIs(match,('或'.join(c['profession_pair'])==offer)if c['role']=='promoted'else None)
            self.assertIsNone(r['actual_profession_offer']);self.assertIsNone(r['actual_eligible'])
    def test_bad_offer_types_values_event_ids_and_unknown_choices_rejected(self):
        for offer in(True,1,[],{},'先锋','先锋或近卫 '):self.assertIsNone(model.reference(offer=offer))
        self.assertIsNone(model.reference(event_id='other'));self.assertIsNone(model.reference(event_id=True));r=model.reference();self.assertIsNone(model.choice_reference(r,1,True))
    def test_results_are_isolated_not_shared_mutable_state(self):
        r=model.reference();r['choices'].clear();r['data']['profession_icons'].clear();self.assertEqual(len(model.reference()['choices']),6);self.assertEqual(len(model.reference()['data']['profession_icons']),8)
    def test_every_source_member_fails_closed_after_success_then_recovers(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    f=root/name;raw=f.read_bytes();self.assertIsNotNone(model.reference());f.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);f.write_bytes(raw)
    def test_all_eight_icons_exact_bytes_and_bad_ornament_keeps_event_text(self):
        for label in model.packet()['data']['profession_icons']:self.assertIsNotNone(model.icon_bytes(label))
        self.assertIsNone(model.icon_bytes('all'));self.assertIsNone(model.icon_bytes(True))
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                f=root/'rouge/data/profession-icons/pioneer.png';raw=f.read_bytes();f.write_bytes(raw+b'x');self.assertIsNone(model.icon_bytes('先锋'));self.assertIsNotNone(model.reference());self.assertIsNotNone(model.icon_bytes('近卫'));f.write_bytes(raw);self.assertIsNotNone(model.icon_bytes('先锋'))
    def test_catalogue_full_narrative_and_id_required(self):
        e=deepcopy(node_catalog._event('community_group_018'));b=model.catalogue_binding(e);self.assertIsNotNone(b);self.assertEqual(len(b['exact_scene_links']),4);e['scenes'][0]['description']+='changed';self.assertIsNone(model.catalogue_binding(e))
    def test_direct_promotion_term_no_fabricated_cultivation_or_free_recruit(self):
        r=model.reference();c=r['choices']['choice_ro6_hire1_1'];text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('首次招募时即获得已进阶效果',text);self.assertIn('具体等级、精英阶段、技能、模组、潜能或信赖',text);self.assertIn('不能把获得2希望视为免费招募',text)
    def test_old290_legacy_annotation_preserved_with_its_original_scope(self):
        from rouge import choice_recruitment_results as old
        d=old.source_data();self.assertIsNotNone(d);self.assertFalse(d['original_entry_scene_verified']);self.assertEqual(len(d['variants']),4)
if __name__=='__main__':unittest.main()

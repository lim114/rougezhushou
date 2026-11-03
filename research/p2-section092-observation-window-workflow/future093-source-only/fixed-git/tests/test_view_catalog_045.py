"""Pinned pictures, grouping identities and predicted-only normal displays."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QComboBox
from rouge.catalog import catalog,operator_profiles
from rouge.battle_preview import battle_data,enemy_preview,enemy_text
from rouge.operator_summary import format_operator_observation
from rouge.view_catalog import (view_catalog,portrait_record,portrait_icon,SubjectPicture,
    add_groups,operator_groups,stage_groups,enemy_groups,PROFESSIONS,ENEMY_TIERS,DATA)
APP=QApplication.instance() or QApplication([])
ROOT=Path(__file__).resolve().parents[1]


def choices(combo):
    return [combo.itemData(i) for i in range(combo.count()) if combo.itemData(i) is not None]


class ViewCatalogTests(unittest.TestCase):
    def test_all_pinned_originals_keep_blob_hash_bytes_and_dimensions(self):
        from PIL import Image
        d=view_catalog();self.assertEqual(len(d['images']),735)
        for record in d['images'].values():
            path=DATA/record['file'];raw=path.read_bytes()
            self.assertEqual(len(raw),record['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),record['blob_sha1'])
            with Image.open(path) as im:
                self.assertEqual(im.format,'PNG');self.assertEqual(im.size,(record['width'],record['height']))
                im.verify()

    def test_all_operator_identities_have_own_profession_and_portrait(self):
        profiles=operator_profiles();d=view_catalog()['operators']
        self.assertEqual(len(profiles),431);self.assertEqual(set(d),set(profiles))
        for key,p in profiles.items():
            self.assertEqual(d[key]['character_id'],p['id'])
            self.assertEqual(d[key]['profession'],p['profession'])
            self.assertIn(p['profession'],PROFESSIONS)
            self.assertTrue(d[key]['portrait'].startswith(p['id']+'.') or d[key]['portrait']==p['id']+'_2.png')
            self.assertFalse(portrait_icon('operator',key).isNull(),key)

    def test_operator_headings_cannot_be_selected_and_choices_remain_unique(self):
        combo=QComboBox();add_groups(combo,operator_groups(operator_profiles(),catalog()['operators']))
        self.assertEqual(len(choices(combo)),431);self.assertEqual(len(set(choices(combo))),431)
        self.assertIsNotNone(combo.currentData())
        headings=[]
        for i in range(combo.count()):
            if combo.itemData(i) is None:
                flags=combo.model().item(i).flags()
                self.assertFalse(flags&Qt.ItemFlag.ItemIsEnabled)
                self.assertFalse(flags&Qt.ItemFlag.ItemIsSelectable)
                headings.append(combo.itemText(i))
        self.assertEqual(len(headings),8)

    def test_floor_source_is_bound_and_special_ids_do_not_imply_floor_number(self):
        d=view_catalog()
        path=ROOT/'.cache/research/visual-catalog-045/stage-floor-input.json'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),d['source']['floor_input_sha256'])
        self.assertEqual(d['stages']['ro6_n_1_1']['floor'],1)
        self.assertEqual(d['stages']['ro6_n_6_1']['floor'],0)
        self.assertEqual(d['stages']['ro6_b_1']['floor'],3)
        self.assertIsNone(d['stages']['ro6_duel_1']['floor'])
        self.assertEqual(d['source']['game_commit'],battle_data()['source']['game_commit'])
        self.assertEqual(d['source']['resource_commit'],battle_data()['source']['resource_commit'])

    def test_all_stages_are_grouped_without_losing_variants(self):
        combo=QComboBox();add_groups(combo,stage_groups(battle_data()['stages']),'尚未选择')
        self.assertEqual(set(choices(combo)),set(battle_data()['stages']))
        self.assertEqual(len(choices(combo)),105)
        self.assertIsNone(combo.currentData())
        normal=combo.findData('ro6_n_1_2');urgent=combo.findData('ro6_e_1_2')
        self.assertGreater(normal,0);self.assertGreater(urgent,0);self.assertNotEqual(normal,urgent)
        combo.setCurrentIndex(urgent);self.assertEqual(combo.currentData(),'ro6_e_1_2')

    def test_enemy_groups_follow_exact_reference_tiers_in_every_stage(self):
        count=0;unknown=0
        for sid,s in battle_data()['stages'].items():
            combo=QComboBox();groups=enemy_groups(s['enemies'],lambda e:(e['id'],e['level']))
            add_groups(combo,groups,'全部敌人')
            expected=[(e['id'],e['level']) for e in s['enemies']]
            self.assertCountEqual(choices(combo),expected,sid)
            for name,items in groups:
                for _,identity,_ in items:
                    e=next(e for e in s['enemies'] if (e['id'],e['level'])==identity)
                    self.assertEqual(name,ENEMY_TIERS.get(e['level_type'],'类别未确认'))
                    unknown+=e['level_type'] not in ENEMY_TIERS;count+=1
        self.assertEqual(count,1087);self.assertEqual(unknown,8)

    def test_missing_gallery_images_are_explicit_without_unrelated_fallback(self):
        d=view_catalog();missing={eid for eid,e in d['enemies'].items() if not e['portrait']}
        self.assertEqual(missing,{'enemy_2156_shsmok','enemy_2154_shdfb','enemy_1177_dufrbl_2','enemy_2121_dyspl2'})
        for eid in missing:
            self.assertIsNone(portrait_record('enemy',eid))
            self.assertTrue(portrait_icon('enemy',eid).isNull())
        self.assertIsNone(portrait_record('other','missing'))
        picture=SubjectPicture();picture.set_subject('operator','mechanist','机械师')
        self.assertFalse(picture.image.pixmap().isNull())
        picture.set_subject('enemy','enemy_2156_shsmok','烟雾弹')
        self.assertEqual(picture.image.text(),'图片未取得')
        self.assertTrue(picture.image.pixmap().isNull())
        picture.set_subject('enemy','enemy_1093_ccsbr','提亚卡乌战士')
        self.assertFalse(picture.image.pixmap().isNull())
        self.assertIn('enemy_1093_ccsbr.png',picture.toolTip())

    def test_alias_gallery_uses_explicit_pinned_prefab_reference(self):
        receipt=json.loads((ROOT/'.cache/research/visual-catalog-045/portrait-download-receipt.json').read_text(encoding='utf-8'))
        d=view_catalog()
        for eid,refs in receipt['prefab_evidence'].items():
            for ref in refs:self.assertEqual(d['enemies'][eid]['prefab_key'],ref['prefab_key'])
            portrait=d['enemies'][eid]['portrait']
            if portrait:self.assertEqual(portrait,d['enemies'][eid]['prefab_key']+'.png')
        self.assertEqual(d['enemies']['enemy_2133_shdopl_lancer']['portrait'],'enemy_2133_shdopl.png')
        # A picture alias establishes appearance only, never an enemy tier.
        s=battle_data()['stages']['ro6_n_2_3']
        self.assertIsNone(next(e for e in s['enemies'] if e['id']=='enemy_2133_shdopl_lancer')['level_type'])

    def test_enemy_display_hides_white_stats_and_updates_confirmed_prediction(self):
        cfg={'difficulty':{'value':15},'zone':{'id':'zone_3'}}
        text=enemy_text(enemy_preview('ro6_n_1_2','enemy_1093_ccsbr',0,cfg))
        self.assertIn('预计生命值：5840.64',text);self.assertIn('预计攻击力：501.12',text)
        self.assertNotIn('基础引用：',text);self.assertNotIn('基础移速属性',text)
        self.assertNotIn('生命值：2600',text);self.assertIn('预计有效移速：未知',text)
        unknown=enemy_text(enemy_preview('ro6_n_1_2','enemy_1093_ccsbr',0,{}))
        self.assertIn('预计生命值：未知',unknown)
        self.assertIn('保密等级尚未确认',unknown);self.assertNotIn('生命值：2600',unknown)

    def test_operator_observation_has_training_metadata_without_white_stats(self):
        state={'id':'mechanist','fields':{'elite':2,'level':90,'trust':100,'potential':6,
               'module_id':None,'module_level':0,'selected_skill':3},'skill_ranks':{'3':10}}
        text=format_operator_observation(state)
        self.assertIn('干员：机械师',text);self.assertIn('专精 3',text)
        self.assertNotIn('白值',text);self.assertNotIn('攻击力：',text);self.assertNotIn('生命值：',text)


if __name__=='__main__':unittest.main()
